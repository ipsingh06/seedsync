import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import * as Immutable from "immutable";

import {LoggerService} from "../common/logger.service";
import {ModelFile} from "../model/model-file";
import {ModelFileReaction, ModelFileService} from "../model/model-file.service";
import {ViewFile} from "./view-file";
import {MOCK_MODEL_FILES} from "../model/mock-model-files";


/**
 * ViewFileReaction encapsulates the response for an action
 * executed on the ViewFileService
 */
export class ViewFileReaction {
    readonly success: boolean;
    readonly errorMessage: string;

    constructor(success: boolean, errorMessage: string) {
        this.success = success;
        this.errorMessage = errorMessage;
    }
}

/**
 * Interface defining filtering criteria for view files
 */
export interface ViewFileFilterCriteria {
    meetsCriteria(viewFile: ViewFile): boolean;
}


/**
 * ViewFileService class provides the store of view files.
 * It implements the observable service pattern to push updates
 * as they become available.
 *
 * The view model needs to be ordered and have fast lookup/update.
 * Unfortunately, there exists no immutable SortedMap structure.
 * This class stores the following data structures:
 *    1. files: List(ViewFile)
 *              ViewFiles sorted in the display order
 *    2. indices: Map(name, index)
 *                Maps name to its index in sortedList
 * The runtime complexity of operations is:
 *    1. Update w/o state change:
 *          O(1) to find index and update the sorted list
 *    2. Updates w/ state change:
 *          O(1) to find index and update the sorted list
 *          O(n log n) to sort list (might be faster since
 *                     list is mostly sorted already??)
 *          O(n) to update indexMap
 *    3. Add:
 *          O(1) to add to list
 *          O(n log n) to sort list (might be faster since
 *                     list is mostly sorted already??)
 *          O(n) to update indexMap
 *    4. Remove:
 *          O(n) to remove from sorted list
 *          O(n) to update indexMap
 *
 * Filtering:
 *      This service also supports providing a filtered list of view files.
 *      The strategy of using pipes to filter at the component level is not
 *      recommended by Angular: https://angular.io/guide/pipes#appendix-no
 *      -filterpipe-or-orderbypipe
 *      Instead, we provide a separate filtered observer.
 *      Filtering is controlled via a single filter criteria. Advanced filters
 *      need to be built outside the service (see ViewFileFilterService)
 */
@Injectable()
export class ViewFileService {

    private readonly USE_MOCK_MODEL = false;

    private _files: Immutable.List<ViewFile> = Immutable.List([]);
    private _filesSubject: BehaviorSubject<Immutable.List<ViewFile>> = new BehaviorSubject(this._files);
    private _filteredFilesSubject: BehaviorSubject<Immutable.List<ViewFile>> = new BehaviorSubject(this._files);
    private _indices: Map<string, number> = new Map<string, number>();

    private _prevModelFiles: Immutable.Map<string, ModelFile> = Immutable.Map<string, ModelFile>();

    private _filterCriteria: ViewFileFilterCriteria = null;

    /**
     * Comparator used to sort the ViewFiles
     * First, sorts by status.
     * Second, sorts by name.
     * @param {ViewFile} a
     * @param {ViewFile} b
     * @returns {number}
     * @private
     */
    private _comparator = (a: ViewFile, b: ViewFile): number => {
        if (a.status != b.status) {
            const statusPriorities = {
                [ViewFile.Status.DOWNLOADING]: 0,
                [ViewFile.Status.QUEUED]: 1,
                [ViewFile.Status.DOWNLOADED]: 2,
                [ViewFile.Status.STOPPED]: 3,
                [ViewFile.Status.DEFAULT]: 4,
                [ViewFile.Status.DELETED]: 4  // intermix deleted and default
            };
            if (statusPriorities[a.status] != statusPriorities[b.status]) {
                return statusPriorities[a.status] - statusPriorities[b.status];
            }
        }
        return a.name.localeCompare(b.name);
    }

    constructor(private _logger: LoggerService,
                private modelFileService: ModelFileService) {
        const _viewFileService = this;

        if (!this.USE_MOCK_MODEL) {
            this.modelFileService.files.subscribe({
                next: modelFiles => _viewFileService.buildViewFromModelFiles(modelFiles)
            });
        } else {
            // For layout/style testing
            this.buildViewFromModelFiles(MOCK_MODEL_FILES);
        }
    }

    private buildViewFromModelFiles(modelFiles: Immutable.Map<string, ModelFile>) {
        this._logger.debug("Received next model files");

        // Diff the previous domain model with the current domain model, then apply
        // those changes to the view model
        // This is a roughly O(2N) operation on every update, so won't scale well
        // But should be fine for small models
        // A more scalable solution would be to subscribe to domain model updates
        let newViewFiles = this._files;

        const addedNames: string[] = [];
        const removedNames: string[] = [];
        const updatedNames: string[] = [];
        // Loop through old model to find deletions
        this._prevModelFiles.keySeq().forEach(
            name => {
                if (!modelFiles.has(name)) removedNames.push(name);
            }
        );
        // Loop through new model to find additions and updates
        modelFiles.keySeq().forEach(
            name => {
                if (!this._prevModelFiles.has(name)) addedNames.push(name);
                else if (!Immutable.is(modelFiles.get(name), this._prevModelFiles.get(name))) updatedNames.push(name);
            }
        );

        let reSort = false;
        let updateIndices = false;
        // Do the updates first before indices change (re-sort may be required)
        updatedNames.forEach(
            name => {
                const index = this._indices.get(name);
                const oldViewFile = newViewFiles.get(index);
                const newViewFile = ViewFileService.createViewFile(modelFiles.get(name), oldViewFile.isSelected);
                newViewFiles = newViewFiles.set(index, newViewFile);
                if (this._comparator(oldViewFile, newViewFile) != 0) {
                    reSort = true;
                }
            }
        );
        // Do the adds (requires re-sort)
        addedNames.forEach(
            name => {
                reSort = true;
                const viewFile = ViewFileService.createViewFile(modelFiles.get(name));
                newViewFiles = newViewFiles.push(viewFile);
                this._indices.set(name, newViewFiles.size - 1);
            }
        );
        // Do the removes (no re-sort required)
        removedNames.forEach(
            name => {
                updateIndices = true;
                const index = newViewFiles.findIndex(value => value.name == name);
                newViewFiles = newViewFiles.remove(index);
                this._indices.delete(name);
            }
        );

        if (reSort) {
            this._logger.debug("Re-sorting view files");
            updateIndices = true;
            newViewFiles = newViewFiles.sort(this._comparator).toList();
        }
        if (updateIndices) {
            this._indices.clear();
            newViewFiles.forEach(
                (value, index) => this._indices.set(value.name, index)
            );
        }

        this._files = newViewFiles;
        this.pushViewFiles();
        this._prevModelFiles = modelFiles;
        this._logger.debug("New view model: %O", this._files.toJS());
    }

    get files(): Observable<Immutable.List<ViewFile>> {
        return this._filesSubject.asObservable();
    }

    get filteredFiles(): Observable<Immutable.List<ViewFile>> {
        return this._filteredFilesSubject.asObservable();
    }

    /**
     * Set a file to be in selected state
     * @param {ViewFile} file
     */
    public setSelected(file: ViewFile) {
        // Find the selected file, if any
        // Note: we can optimize this by storing an additional
        //       state that tracks the selected file
        //       but that would duplicate state and can introduce
        //       bugs, so we just search instead
        let viewFiles = this._files;
        const unSelectIndex = viewFiles.findIndex(value => value.isSelected);

        // Unset the previously selected file, if any
        if (unSelectIndex >= 0) {
            let unSelectViewFile = viewFiles.get(unSelectIndex);

            // Do nothing if file is already selected
            if (unSelectViewFile.name == file.name) return;

            unSelectViewFile = new ViewFile(unSelectViewFile.set("isSelected", false));
            viewFiles = viewFiles.set(unSelectIndex, unSelectViewFile);
        }

        // Set the new selected file
        if (this._indices.has(file.name)) {
            const index = this._indices.get(file.name);
            let viewFile = viewFiles.get(index);
            viewFile = new ViewFile(viewFile.set("isSelected", true));
            viewFiles = viewFiles.set(index, viewFile);
        } else {
            this._logger.error("Can't find file to select: " + file.name);
        }

        // Send update
        this._files = viewFiles;
        this.pushViewFiles();
    }

    /**
     * Un-select the currently selected file
     */
    public unsetSelected() {
        // Unset the previously selected file, if any
        let viewFiles = this._files;
        const unSelectIndex = viewFiles.findIndex(value => value.isSelected);

        // Unset the previously selected file, if any
        if (unSelectIndex >= 0) {
            let unSelectViewFile = viewFiles.get(unSelectIndex);

            unSelectViewFile = new ViewFile(unSelectViewFile.set("isSelected", false));
            viewFiles = viewFiles.set(unSelectIndex, unSelectViewFile);

            // Send update
            this._files = viewFiles;
            this.pushViewFiles();
        }
    }

    /**
     * Queue a file for download
     * @param {ViewFile} file
     * @returns {Observable<ViewFileReaction>}
     */
    public queue(file: ViewFile): Observable<ViewFileReaction> {
        this._logger.debug("Queue view file: " + file.name);
        return this.createAction(file, (f) => this.modelFileService.queue(f));
    }

    /**
     * Stop a file
     * @param {ViewFile} file
     * @returns {Observable<ViewFileReaction>}
     */
    public stop(file: ViewFile): Observable<ViewFileReaction> {
        this._logger.debug("Stop view file: " + file.name);
        return this.createAction(file, (f) => this.modelFileService.stop(f));
    }

    /**
     * Set a new filter criteria
     * @param {ViewFileFilterCriteria} criteria
     */
    public setFilterCriteria(criteria: ViewFileFilterCriteria) {
        this._filterCriteria = criteria;
        this.pushViewFiles();
    }

    /**
     * Re-apply the filters and push out the view files
     * Use this if filter criteria's state changed but the reference did not
     */
    public reapplyFilters() {
        this.pushViewFiles();
    }

    private static createViewFile(modelFile: ModelFile, isSelected: boolean = false): ViewFile {
        // Use zero for unknown sizes
        let localSize: number = modelFile.local_size;
        if (localSize == null) {
            localSize = 0;
        }
        let remoteSize: number = modelFile.remote_size;
        if (remoteSize == null) {
            remoteSize = 0;
        }
        let percentDownloaded: number = null;
        if (remoteSize > 0) {
            percentDownloaded = Math.trunc(100.0 * localSize / remoteSize);
        } else {
            percentDownloaded = 100;
        }

        // Translate the status
        let status = null;
        switch (modelFile.state) {
            case ModelFile.State.DEFAULT: {
                if (localSize > 0 && remoteSize > 0) {
                    status = ViewFile.Status.STOPPED;
                } else {
                    status = ViewFile.Status.DEFAULT;
                }
                break;
            }
            case ModelFile.State.QUEUED: {
                status = ViewFile.Status.QUEUED;
                break;
            }
            case ModelFile.State.DOWNLOADING: {
                status = ViewFile.Status.DOWNLOADING;
                break;
            }
            case ModelFile.State.DOWNLOADED: {
                status = ViewFile.Status.DOWNLOADED;
                break;
            }
            case ModelFile.State.DELETED: {
                status = ViewFile.Status.DELETED;
                break;
            }
        }

        const isQueueable: boolean = [ViewFile.Status.DEFAULT,
                                    ViewFile.Status.STOPPED,
                                    ViewFile.Status.DELETED].includes(status)
                                    && remoteSize > 0;
        const isStoppable: boolean = [ViewFile.Status.QUEUED,
                                    ViewFile.Status.DOWNLOADING].includes(status);

        return new ViewFile({
            name: modelFile.name,
            isDir: modelFile.is_dir,
            localSize: localSize,
            remoteSize: remoteSize,
            percentDownloaded: percentDownloaded,
            status: status,
            downloadingSpeed: modelFile.downloading_speed,
            eta: modelFile.eta,
            fullPath: modelFile.full_path,
            isSelected: isSelected,
            isQueueable: isQueueable,
            isStoppable: isStoppable
        });
    }

    /**
     * Helper method to execute an action on ModelFileService and generate a ViewFileReaction
     * @param {ViewFile} file
     * @param {Observable<ModelFileReaction>} action
     * @returns {Observable<ViewFileReaction>}
     */
    private createAction(file: ViewFile,
                         action: (file: ModelFile) => Observable<ModelFileReaction>)
            : Observable<ViewFileReaction> {
        return Observable.create(observer => {
            if (!this._prevModelFiles.has(file.name)) {
                // File not found, exit early
                this._logger.error("File to queue not found: " + file.name);
                observer.next(new ViewFileReaction(false, `File '${file.name}' not found`));
            } else {
                const modelFile = this._prevModelFiles.get(file.name);
                action(modelFile).subscribe(data => {
                    this._logger.debug("Received model reaction: %O", data);
                    observer.next(new ViewFileReaction(data.success, data.errorMessage));
                });
            }
        });
    }

    private pushViewFiles() {
        // Unfiltered files
        this._filesSubject.next(this._files);

        // Filtered files
        let filteredFiles = this._files;
        if (this._filterCriteria != null) {
            filteredFiles = Immutable.List<ViewFile>(
                this._files.filter(f => this._filterCriteria.meetsCriteria(f))
            );
        }
        this._filteredFilesSubject.next(filteredFiles);
    }
}
