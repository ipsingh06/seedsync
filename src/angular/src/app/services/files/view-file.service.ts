import { Injectable, inject } from '@angular/core';
import { Observable, BehaviorSubject, of } from 'rxjs';

import { LoggerService } from '../utils/logger.service';
import { ModelFile, ModelFileState } from './model-file';
import { ModelFileService } from './model-file.service';
import { ViewFile, ViewFileStatus } from './view-file';
import { StreamServiceRegistry } from '../base/stream-service.registry';
import { WebReaction } from '../utils/rest.service';

/**
 * Interface defining filtering criteria for view files
 */
export interface ViewFileFilterCriteria {
    meetsCriteria(viewFile: ViewFile): boolean;
}

/**
 * Interface for sorting view files
 */
export type ViewFileComparator = (a: ViewFile, b: ViewFile) => number;

/**
 * ViewFileService class provides the store of view files.
 * It implements the observable service pattern to push updates
 * as they become available.
 */
@Injectable({
    providedIn: 'root'
})
export class ViewFileService {
    private readonly USE_MOCK_MODEL = false;

    private modelFileService!: ModelFileService;

    private _files: ViewFile[] = [];
    private filesSubject = new BehaviorSubject<readonly ViewFile[]>([]);
    private filteredFilesSubject = new BehaviorSubject<readonly ViewFile[]>([]);
    private indices = new Map<string, number>();

    private prevModelFiles = new Map<string, ModelFile>();

    private filterCriteria: ViewFileFilterCriteria | null = null;
    private sortComparator: ViewFileComparator | null = null;

    private logger = inject(LoggerService);
    private streamServiceRegistry = inject(StreamServiceRegistry);

    constructor() {
        // Initialize in ngOnInit or manually called init
    }

    public init(): void {
        this.modelFileService = this.streamServiceRegistry.modelFileService;

        if (!this.USE_MOCK_MODEL) {
            this.modelFileService.files.subscribe({
                next: modelFiles => {
                    const t0 = performance.now();
                    this.buildViewFromModelFiles(modelFiles);
                    const t1 = performance.now();
                    this.logger.debug('ViewFile creation took', (t1 - t0).toFixed(0), 'ms');
                }
            });
        }
    }

    private buildViewFromModelFiles(modelFiles: Map<string, ModelFile>): void {
        this.logger.debug('Received next model files');

        // Diff the previous domain model with the current domain model, then apply
        // those changes to the view model
        let newViewFiles = [...this._files];

        const addedNames: string[] = [];
        const removedNames: string[] = [];
        const updatedNames: string[] = [];

        // Loop through old model to find deletions
        for (const name of this.prevModelFiles.keys()) {
            if (!modelFiles.has(name)) {
                removedNames.push(name);
            }
        }

        // Loop through new model to find additions and updates
        for (const name of modelFiles.keys()) {
            if (!this.prevModelFiles.has(name)) {
                addedNames.push(name);
            } else {
                const newFile = modelFiles.get(name)!;
                const oldFile = this.prevModelFiles.get(name)!;
                if (this.modelFilesChanged(newFile, oldFile)) {
                    updatedNames.push(name);
                }
            }
        }

        let reSort = false;
        let updateIndices = false;

        // Do the updates first before indices change (re-sort may be required)
        for (const name of updatedNames) {
            const index = this.indices.get(name)!;
            const oldViewFile = newViewFiles[index];
            const newViewFile = ViewFileService.createViewFile(modelFiles.get(name)!, oldViewFile.isSelected);
            newViewFiles[index] = newViewFile;
            if (this.sortComparator != null && this.sortComparator(oldViewFile, newViewFile) !== 0) {
                reSort = true;
            }
        }

        // Do the adds (requires re-sort)
        for (const name of addedNames) {
            reSort = true;
            const viewFile = ViewFileService.createViewFile(modelFiles.get(name)!);
            newViewFiles.push(viewFile);
            this.indices.set(name, newViewFiles.length - 1);
        }

        // Do the removes (no re-sort required)
        for (const name of removedNames) {
            updateIndices = true;
            const index = newViewFiles.findIndex(value => value.name === name);
            newViewFiles.splice(index, 1);
            this.indices.delete(name);
        }

        if (reSort && this.sortComparator != null) {
            this.logger.debug('Re-sorting view files');
            updateIndices = true;
            newViewFiles.sort(this.sortComparator);
        }

        if (updateIndices) {
            this.indices.clear();
            newViewFiles.forEach((value, index) => this.indices.set(value.name, index));
        }

        this._files = newViewFiles;
        this.pushViewFiles();
        this.prevModelFiles = new Map(modelFiles);
        this.logger.debug('New view model:', this._files);
    }

    private modelFilesChanged(a: ModelFile, b: ModelFile): boolean {
        return a.name !== b.name ||
            a.state !== b.state ||
            a.local_size !== b.local_size ||
            a.remote_size !== b.remote_size ||
            a.downloading_speed !== b.downloading_speed ||
            a.eta !== b.eta;
    }

    get files(): Observable<readonly ViewFile[]> {
        return this.filesSubject.asObservable();
    }

    get filteredFiles(): Observable<readonly ViewFile[]> {
        return this.filteredFilesSubject.asObservable();
    }

    /**
     * Set a file to be in selected state
     */
    public setSelected(file: ViewFile): void {
        let viewFiles = [...this._files];
        const unSelectIndex = viewFiles.findIndex(value => value.isSelected);

        // Unset the previously selected file, if any
        if (unSelectIndex >= 0) {
            const unSelectViewFile = viewFiles[unSelectIndex];

            // Do nothing if file is already selected
            if (unSelectViewFile.name === file.name) { return; }

            viewFiles[unSelectIndex] = unSelectViewFile.update({ isSelected: false });
        }

        // Set the new selected file
        if (this.indices.has(file.name)) {
            const index = this.indices.get(file.name)!;
            const viewFile = viewFiles[index];
            viewFiles[index] = viewFile.update({ isSelected: true });
        } else {
            this.logger.error("Can't find file to select: " + file.name);
        }

        // Send update
        this._files = viewFiles;
        this.pushViewFiles();
    }

    /**
     * Un-select the currently selected file
     */
    public unsetSelected(): void {
        let viewFiles = [...this._files];
        const unSelectIndex = viewFiles.findIndex(value => value.isSelected);

        // Unset the previously selected file, if any
        if (unSelectIndex >= 0) {
            const unSelectViewFile = viewFiles[unSelectIndex];
            viewFiles[unSelectIndex] = unSelectViewFile.update({ isSelected: false });

            // Send update
            this._files = viewFiles;
            this.pushViewFiles();
        }
    }

    /**
     * Queue a file for download
     */
    public queue(file: ViewFile): Observable<WebReaction> {
        this.logger.debug('Queue view file: ' + file.name);
        return this.createAction(file, f => this.modelFileService.queue(f));
    }

    /**
     * Stop a file
     */
    public stop(file: ViewFile): Observable<WebReaction> {
        this.logger.debug('Stop view file: ' + file.name);
        return this.createAction(file, f => this.modelFileService.stop(f));
    }

    /**
     * Extract a file
     */
    public extract(file: ViewFile): Observable<WebReaction> {
        this.logger.debug('Extract view file: ' + file.name);
        return this.createAction(file, f => this.modelFileService.extract(f));
    }

    /**
     * Locally delete a file
     */
    public deleteLocal(file: ViewFile): Observable<WebReaction> {
        this.logger.debug('Locally delete view file: ' + file.name);
        return this.createAction(file, f => this.modelFileService.deleteLocal(f));
    }

    /**
     * Remotely delete a file
     */
    public deleteRemote(file: ViewFile): Observable<WebReaction> {
        this.logger.debug('Remotely delete view file: ' + file.name);
        return this.createAction(file, f => this.modelFileService.deleteRemote(f));
    }

    /**
     * Set a new filter criteria
     */
    public setFilterCriteria(criteria: ViewFileFilterCriteria | null): void {
        this.filterCriteria = criteria;
        this.pushViewFiles();
    }

    /**
     * Sets a new comparator.
     */
    public setComparator(comparator: ViewFileComparator | null): void {
        this.sortComparator = comparator;

        // Re-sort and regenerate index cache
        this.logger.debug('Re-sorting view files');
        let newViewFiles = [...this._files];
        if (this.sortComparator != null) {
            newViewFiles.sort(this.sortComparator);
        }
        this._files = newViewFiles;
        this.indices.clear();
        newViewFiles.forEach((value, index) => this.indices.set(value.name, index));

        this.pushViewFiles();
    }

    private static createViewFile(modelFile: ModelFile, isSelected: boolean = false): ViewFile {
        // Use zero for unknown sizes
        let localSize = modelFile.local_size ?? 0;
        let remoteSize = modelFile.remote_size ?? 0;

        let percentDownloaded: number;
        if (remoteSize > 0) {
            percentDownloaded = Math.trunc(100.0 * localSize / remoteSize);
        } else {
            percentDownloaded = 100;
        }

        // Translate the status
        let status: ViewFileStatus;
        switch (modelFile.state) {
            case ModelFileState.DEFAULT: {
                if (localSize > 0 && remoteSize > 0) {
                    status = ViewFileStatus.STOPPED;
                } else {
                    status = ViewFileStatus.DEFAULT;
                }
                break;
            }
            case ModelFileState.QUEUED:
                status = ViewFileStatus.QUEUED;
                break;
            case ModelFileState.DOWNLOADING:
                status = ViewFileStatus.DOWNLOADING;
                break;
            case ModelFileState.DOWNLOADED:
                status = ViewFileStatus.DOWNLOADED;
                break;
            case ModelFileState.DELETED:
                status = ViewFileStatus.DELETED;
                break;
            case ModelFileState.EXTRACTING:
                status = ViewFileStatus.EXTRACTING;
                break;
            case ModelFileState.EXTRACTED:
                status = ViewFileStatus.EXTRACTED;
                break;
            default:
                status = ViewFileStatus.DEFAULT;
        }

        const isQueueable = [ViewFileStatus.DEFAULT, ViewFileStatus.STOPPED, ViewFileStatus.DELETED].includes(status)
            && remoteSize > 0;
        const isStoppable = [ViewFileStatus.QUEUED, ViewFileStatus.DOWNLOADING].includes(status);
        const isExtractable = [ViewFileStatus.DEFAULT, ViewFileStatus.STOPPED, ViewFileStatus.DOWNLOADED, ViewFileStatus.EXTRACTED].includes(status)
            && localSize > 0;
        const isLocallyDeletable = [ViewFileStatus.DEFAULT, ViewFileStatus.STOPPED, ViewFileStatus.DOWNLOADED, ViewFileStatus.EXTRACTED].includes(status)
            && localSize > 0;
        const isRemotelyDeletable = [ViewFileStatus.DEFAULT, ViewFileStatus.STOPPED, ViewFileStatus.DOWNLOADED, ViewFileStatus.EXTRACTED, ViewFileStatus.DELETED].includes(status)
            && remoteSize > 0;

        return new ViewFile({
            name: modelFile.name,
            isDir: modelFile.is_dir,
            localSize,
            remoteSize,
            percentDownloaded,
            status,
            downloadingSpeed: modelFile.downloading_speed,
            eta: modelFile.eta,
            fullPath: modelFile.full_path,
            isArchive: modelFile.is_extractable,
            isSelected,
            isQueueable,
            isStoppable,
            isExtractable,
            isLocallyDeletable,
            isRemotelyDeletable,
            localCreatedTimestamp: modelFile.local_created_timestamp,
            localModifiedTimestamp: modelFile.local_modified_timestamp,
            remoteCreatedTimestamp: modelFile.remote_created_timestamp,
            remoteModifiedTimestamp: modelFile.remote_modified_timestamp
        });
    }

    /**
     * Helper method to execute an action on ModelFileService and generate a WebReaction
     */
    private createAction(
        file: ViewFile,
        action: (file: ModelFile) => Observable<WebReaction>
    ): Observable<WebReaction> {
        if (!this.prevModelFiles.has(file.name)) {
            // File not found, exit early
            this.logger.error('File to queue not found: ' + file.name);
            return of(new WebReaction(false, null, `File '${file.name}' not found`));
        }

        const modelFile = this.prevModelFiles.get(file.name)!;
        return new Observable(observer => {
            action(modelFile).subscribe(reaction => {
                this.logger.debug('Received model reaction:', reaction);
                observer.next(reaction);
                observer.complete();
            });
        });
    }

    private pushViewFiles(): void {
        // Unfiltered files
        this.filesSubject.next(Object.freeze([...this._files]));

        // Filtered files
        let filteredFiles = this._files;
        if (this.filterCriteria != null) {
            filteredFiles = this._files.filter(f => this.filterCriteria!.meetsCriteria(f));
        }
        this.filteredFilesSubject.next(Object.freeze(filteredFiles));
    }
}
