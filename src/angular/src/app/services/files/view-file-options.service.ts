import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import * as Immutable from "immutable";

import {LoggerService} from "../utils/logger.service";
import {ViewFileOptions} from "./view-file-options";



/**
 * ViewFileOptionsService class provides display option services
 * for view files
 *
 * This class is used to broadcast changes to the display options
 */
@Injectable()
export class ViewFileOptionsService {

    private _options: BehaviorSubject<ViewFileOptions> = new BehaviorSubject(
        new ViewFileOptions({
            showDetails: false
        })
    );

    get options(): Observable<ViewFileOptions> {
        return this._options.asObservable();
    }

    public setShowDetails(show: boolean) {
        const options = this._options.getValue();
        if (options.showDetails !== show) {
            const newOptions = new ViewFileOptions(options.set("showDetails", show));
            this._options.next(newOptions);
        }
    }
}
