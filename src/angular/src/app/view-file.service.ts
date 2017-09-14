import {Injectable} from '@angular/core';
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import {List, Set} from 'immutable';

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

    constructor(private modelFileService: ModelFileService) {
        let _viewFileService = this;
        this.modelFileService.files.subscribe({
            next: modelFiles => _viewFileService.nextModelFiles(modelFiles)
        });
    }

    private nextModelFiles(modelFiles: Set<ModelFile>) {
        console.debug("Received next model files");
        let viewFiles: ViewFile[] = [];
        modelFiles.valueSeq().forEach(
            modelFile => viewFiles.push(new ViewFile({
                name: modelFile.name,
                localSize: modelFile.local_size,
                remoteSize: modelFile.remote_size
            }))
        );
        this._files.next(List(viewFiles));
    }

    get files() : Observable<List<ViewFile>> {
        return this._files.asObservable();
    }
}
