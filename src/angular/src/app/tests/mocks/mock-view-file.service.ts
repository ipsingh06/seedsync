import {Subject} from "rxjs/Subject";
import {Observable} from "rxjs/Observable";

import * as Immutable from "immutable";

import {ViewFile} from "../../services/files/view-file";
import {ViewFileFilterCriteria} from "../../services/files/view-file.service";


export class MockViewFileService {

    _files = new Subject<Immutable.List<ViewFile>>();
    _filteredFiles = new Subject<Immutable.List<ViewFile>>();

    get files(): Observable<Immutable.List<ViewFile>> {
        return this._files.asObservable();
    }

    get filteredFiles(): Observable<Immutable.List<ViewFile>> {
        return this._filteredFiles.asObservable();
    }

    // noinspection JSUnusedLocalSymbols
    public setFilterCriteria(criteria: ViewFileFilterCriteria) {}
}
