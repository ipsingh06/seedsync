import {Inject, Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import {LoggerService} from "../utils/logger.service";
import {ViewFileOptions} from "./view-file-options";
import {ViewFile} from "./view-file";
import {LOCAL_STORAGE, StorageService} from "angular-webstorage-service";
import {StorageKeys} from "../../common/storage-keys";



/**
 * ViewFileOptionsService class provides display option services
 * for view files
 *
 * This class is used to broadcast changes to the display options
 */
@Injectable()
export class ViewFileOptionsService {

    private _options: BehaviorSubject<ViewFileOptions>;

    constructor(private _logger: LoggerService,
                @Inject(LOCAL_STORAGE) private _storage: StorageService) {
        // Load some options from storage
        const showDetails: boolean =
            this._storage.get(StorageKeys.VIEW_OPTION_SHOW_DETAILS) || false;
        const sortMethod: ViewFileOptions.SortMethod =
            this._storage.get(StorageKeys.VIEW_OPTION_SORT_METHOD) ||
                ViewFileOptions.SortMethod.STATUS;
        const pinFilter: boolean =
            this._storage.get(StorageKeys.VIEW_OPTION_PIN) || false;

        this._options = new BehaviorSubject(
            new ViewFileOptions({
                showDetails: showDetails,
                sortMethod: sortMethod,
                selectedStatusFilter: null,
                nameFilter: null,
                pinFilter: pinFilter,
            })
        );
    }

    get options(): Observable<ViewFileOptions> {
        return this._options.asObservable();
    }

    public setShowDetails(show: boolean) {
        const options = this._options.getValue();
        if (options.showDetails !== show) {
            const newOptions = new ViewFileOptions(options.set("showDetails", show));
            this._options.next(newOptions);
            this._storage.set(StorageKeys.VIEW_OPTION_SHOW_DETAILS, show);
            this._logger.debug("ViewOption showDetails set to: " + newOptions.showDetails);
        }
    }

    public setSortMethod(sortMethod: ViewFileOptions.SortMethod) {
        const options = this._options.getValue();
        if (options.sortMethod !== sortMethod) {
            const newOptions = new ViewFileOptions(options.set("sortMethod", sortMethod));
            this._options.next(newOptions);
            this._storage.set(StorageKeys.VIEW_OPTION_SORT_METHOD, sortMethod);
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

    public setPinFilter(pinned: boolean) {
        const options = this._options.getValue();
        if (options.pinFilter !== pinned) {
            const newOptions = new ViewFileOptions(options.set("pinFilter", pinned));
            this._options.next(newOptions);
            this._storage.set(StorageKeys.VIEW_OPTION_PIN, pinned);
            this._logger.debug("ViewOption pinFilter set to: " + newOptions.pinFilter);
        }
    }
}
