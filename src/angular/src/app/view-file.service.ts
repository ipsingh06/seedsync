import {Injectable} from '@angular/core';
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import * as Immutable from 'immutable';

import {ModelFile} from './model-file'
import {ModelFileService} from "./model-file.service";
import {ViewFile} from "./view-file"


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
 */
@Injectable()
export class ViewFileService {

    private _files: BehaviorSubject<Immutable.List<ViewFile>> = new BehaviorSubject(Immutable.List([]));
    private _indices: Map<string, number> = new Map<string, number>();

    private _prevModelFiles: Immutable.Map<string, ModelFile> = Immutable.Map<string, ModelFile>();

    /**
     * Comparator used to sort the ViewFiles
     * @param {ViewFile} a
     * @param {ViewFile} b
     * @returns {number}
     * @private
     */
    private _comparator = (a: ViewFile, b: ViewFile): number => {
        return a.name.localeCompare(b.name);
    };

    constructor(private modelFileService: ModelFileService) {
        let _viewFileService = this;
        this.modelFileService.files.subscribe({
            next: modelFiles => _viewFileService.nextModelFiles(modelFiles)
        });
    }

    private nextModelFiles(modelFiles: Immutable.Map<string, ModelFile>) {
        console.debug("Received next model files");

        // Diff the previous domain model with the current domain model, then apply
        // those changes to the view model
        // This is a roughly O(2N) operation on every update, so won't scale well
        // But should be fine for small models
        // A more scalable solution would be to subscribe to domain model updates
        let newViewFiles = this._files.getValue();

        let addedNames: string[] = [];
        let removedNames: string[] = [];
        let updatedNames: string[] = [];
        // Loop through old model to find deletions
        this._prevModelFiles.keySeq().forEach(
            name => {
                if(!modelFiles.has(name)) removedNames.push(name)
            }
        );
        // Loop through new model to find additions and updates
        modelFiles.keySeq().forEach(
            name => {
                if(!this._prevModelFiles.has(name)) addedNames.push(name);
                else if(!Immutable.is(modelFiles.get(name), this._prevModelFiles.get(name))) updatedNames.push(name);
            }
        );

        let reSort = false;
        let updateIndices = false;
        // Do the updates first before indices change (re-sort may be required)
        updatedNames.forEach(
            name => {
                let index = this._indices.get(name);
                let oldViewFile = newViewFiles.get(index);
                let newViewFile = ViewFileService.createViewFile(modelFiles.get(name));
                newViewFiles = newViewFiles.set(index, newViewFile);
                if(this._comparator(oldViewFile, newViewFile) != 0) {
                    reSort = true;
                }
            }
        );
        // Do the adds (requires re-sort)
        addedNames.forEach(
            name => {
                reSort = true;
                let viewFile = ViewFileService.createViewFile(modelFiles.get(name));
                newViewFiles = newViewFiles.push(viewFile);
                this._indices.set(name, newViewFiles.size-1);
            }
        );
        // Do the removes (no re-sort required)
        removedNames.forEach(
            name => {
                updateIndices = true;
                let index = newViewFiles.findIndex(value => value.name == name);
                newViewFiles = newViewFiles.remove(index);
                this._indices.delete(name);
            }
        );

        if(reSort) {
            console.log("Re-sorting view files");
            updateIndices = true;
            newViewFiles = newViewFiles.sort(this._comparator).toList();
        }
        if(updateIndices) {
            this._indices.clear();
            newViewFiles.forEach(
                (value, index) => this._indices.set(value.name, index)
            );
        }

        this._files.next(newViewFiles);
        this._prevModelFiles = modelFiles;
    }

    get files() : Observable<Immutable.List<ViewFile>> {
        return this._files.asObservable();
    }

    private static createViewFile(modelFile: ModelFile): ViewFile {
        let status = null;
        switch(modelFile.state) {
            case ModelFile.State.DEFAULT: {
                status = ViewFile.Status.DEFAULT;
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
        }
        return new ViewFile({
            name: modelFile.name,
            localSize: modelFile.local_size,
            remoteSize: modelFile.remote_size,
            status: status,
        })
    }
}
