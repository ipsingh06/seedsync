import {Injectable} from '@angular/core';
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import {List, Map} from 'immutable';

import {ModelFile} from './model-file'
import {ModelFileService} from "./model-file.service";
import {ViewFile} from "./view-file"


/**
 * ViewFileService class provides the store of view files.
 * It implements the observable service pattern to push updates
 * as they become available.
 * The view model is stored as an Immutable List of ViewFiles. The
 * order of the list defines the display order.
 */
@Injectable()
export class ViewFileService {

    private _files: BehaviorSubject<List<ViewFile>> = new BehaviorSubject(List([]));

    private _prevModelFiles: Map<string, ModelFile> = Map<string, ModelFile>();

    constructor(private modelFileService: ModelFileService) {
        let _viewFileService = this;
        this.modelFileService.files.subscribe({
            next: modelFiles => _viewFileService.nextModelFiles(modelFiles)
        });
    }

    private nextModelFiles(modelFiles: Map<string, ModelFile>) {
        console.debug("Received next model files");
        // Diff the previous domain model with the current domain model, then apply
        // those changes to the view model
        // This is a roughly O(N) operation on every update, so won't scale well
        // But should be fine for small models
        // A more scalable solution would be to subscribe to domain model updates
        let viewFiles: ViewFile[] = [];
        modelFiles.valueSeq().forEach(
            modelFile => viewFiles.push(new ViewFile({
                name: modelFile.name,
                localSize: modelFile.local_size,
                remoteSize: modelFile.remote_size
            }))
        );
        this._files.next(List(viewFiles));
        this._prevModelFiles = modelFiles;
    }

    get files() : Observable<List<ViewFile>> {
        return this._files.asObservable();
    }
}
