import {Injectable} from "@angular/core";

import {LoggerService} from "../utils/logger.service";
import {ViewFile} from "./view-file";
import {ViewFileFilterCriteria, ViewFileService} from "./view-file.service";
import {ViewFileOptionsService} from "./view-file-options.service";


class AndFilterCriteria implements ViewFileFilterCriteria {
    constructor(private a: ViewFileFilterCriteria,
                private b: ViewFileFilterCriteria) {
    }

    meetsCriteria(viewFile: ViewFile): boolean {
        return this.a.meetsCriteria(viewFile) && this.b.meetsCriteria(viewFile);
    }
}

class StatusFilterCriteria implements ViewFileFilterCriteria {
    constructor(private _status: ViewFile.Status) {}

    get status(): ViewFile.Status {
        return this._status;
    }

    meetsCriteria(viewFile: ViewFile): boolean {
        return this._status == null || this._status === viewFile.status;
    }
}

class NameFilterCriteria implements ViewFileFilterCriteria {
    private _name: string = null;
    private _queryCandidates = [];

    get name(): string {
        return this._name;
    }

    constructor(name: string) {
        this._name = name;
        if (this._name != null) {
            const query = this._name.toLowerCase();
            this._queryCandidates = [
                query,
                // treat dots and spaces as the same
                query.replace(/\s/g, "."),
                query.replace(/\./g, " "),
            ];
        }
    }

    meetsCriteria(viewFile: ViewFile): boolean {
        if (this._name == null || this._name === "") { return true; }
        const search = viewFile.name.toLowerCase();
        return this._queryCandidates.reduce(
            (a: boolean, b: string) => a || search.indexOf(b) >= 0,
            false  // initial value
        );
    }
}


/**
 * ViewFileFilterService class provides filtering services for
 * view files
 *
 * This class responds to changes in the filter settings and
 * applies the appropriate filters to the ViewFileService
 */
@Injectable()
export class ViewFileFilterService {
    private _statusFilter: StatusFilterCriteria = null;
    private _nameFilter: NameFilterCriteria = null;

    constructor(private _logger: LoggerService,
                private _viewFileService: ViewFileService,
                private _viewFileOptionsService: ViewFileOptionsService) {
        this._viewFileOptionsService.options.subscribe(options => {
            let updateFilterCriteria = false;

            // Check to see if status filter changed
            if (this._statusFilter == null ||
                    this._statusFilter.status !== options.selectedStatusFilter){
                updateFilterCriteria = true;
                this._statusFilter = new StatusFilterCriteria(options.selectedStatusFilter);
                this._logger.debug("Status filter set to: " + options.selectedStatusFilter);
            }

            // Check to see if the name filter changed
            if (this._nameFilter == null ||
                    this._nameFilter.name !== options.nameFilter) {
                updateFilterCriteria = true;
                this._nameFilter = new NameFilterCriteria(options.nameFilter);
                this._logger.debug("Name filter set to: " + options.nameFilter);
            }

            // Update the filter criteria if necessary
            if (updateFilterCriteria) {
                this._viewFileService.setFilterCriteria(this.buildFilterCriteria());
            }
        });
    }

    private buildFilterCriteria(): ViewFileFilterCriteria {
        if (this._statusFilter != null && this._nameFilter != null) {
            return new AndFilterCriteria(this._statusFilter, this._nameFilter);
        } else if (this._statusFilter != null) {
            return this._statusFilter;
        } else if (this._nameFilter != null) {
            return this._nameFilter;
        } else {
            return null;
        }
    }
}
