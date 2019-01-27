import {Subject} from "rxjs/Subject";
import {Observable} from "rxjs/Observable";

import {ViewFileOptions} from "../../services/files/view-file-options";


export class MockViewFileOptionsService {

    _options = new Subject<ViewFileOptions>();

    get options(): Observable<ViewFileOptions> {
        return this._options.asObservable();
    }
}
