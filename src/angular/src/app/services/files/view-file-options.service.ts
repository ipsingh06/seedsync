import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import * as Immutable from "immutable";

import {LoggerService} from "../utils/logger.service";
import {ViewFileOptions} from "./view-file-options";
import {ViewFile} from "./view-file";



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
            showDetails: false,
            sortMethod: ViewFileOptions.SortMethod.STATUS,
            selectedStatusFilter: null,
            nameFilter: null,
        })
    );

    constructor(private _logger: LoggerService) {}

    get options(): Observable<ViewFileOptions> {
        return this._options.asObservable();
    }

    public setShowDetails(show: boolean) {
        const options = this._options.getValue();
        if (options.showDetails !== show) {
            const newOptions = new ViewFileOptions(options.set("showDetails", show));
            this._options.next(newOptions);
            this._logger.debug("ViewOption showDetails set to: " + newOptions.showDetails);
        }
    }

    public setSortMethod(sortMethod: ViewFileOptions.SortMethod) {
        const options = this._options.getValue();
        if (options.sortMethod !== sortMethod) {
            const newOptions = new ViewFileOptions(options.set("sortMethod", sortMethod));
            this._options.next(newOptions);
            this._logger.debug("ViewOption sortMethod set to: " + newOptions.sortMethod);
        }
    }

    public setSelectedStatusFilter(status: ViewFile.Status) {
        const options = this._options.getValue();
        if (options.selectedStatusFilter !== status) {
            const newOptions = new ViewFileOptions(options.set("selectedStatusFilter", status));
            this._options.next(newOptions);
            this._logger.debug("ViewOption selectedStatusFilter set to: " + newOptions.selectedStatusFilter);
        }
    }

    public setNameFilter(name: string) {
        const options = this._options.getValue();
        if (options.nameFilter !== name) {
            const newOptions = new ViewFileOptions(options.set("nameFilter", name));
            this._options.next(newOptions);
            this._logger.debug("ViewOption nameFilter set to: " + newOptions.nameFilter);
        }
    }
}
