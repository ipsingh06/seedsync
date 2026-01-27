import { Injectable, inject } from '@angular/core';

import { LoggerService } from '../utils/logger.service';
import { ViewFile, ViewFileStatus } from './view-file';
import { ViewFileFilterCriteria, ViewFileService } from './view-file.service';
import { ViewFileOptionsService } from './view-file-options.service';

class AndFilterCriteria implements ViewFileFilterCriteria {
    constructor(
        private a: ViewFileFilterCriteria,
        private b: ViewFileFilterCriteria
    ) {}

    meetsCriteria(viewFile: ViewFile): boolean {
        return this.a.meetsCriteria(viewFile) && this.b.meetsCriteria(viewFile);
    }
}

class StatusFilterCriteria implements ViewFileFilterCriteria {
    constructor(private _status: ViewFileStatus | null) {}

    get status(): ViewFileStatus | null {
        return this._status;
    }

    meetsCriteria(viewFile: ViewFile): boolean {
        return this._status == null || this._status === viewFile.status;
    }
}

class NameFilterCriteria implements ViewFileFilterCriteria {
    private _name: string | null = null;
    private queryCandidates: string[] = [];

    get name(): string | null {
        return this._name;
    }

    constructor(name: string | null) {
        this._name = name;
        if (this._name != null) {
            const query = this._name.toLowerCase();
            this.queryCandidates = [
                query,
                // treat dots and spaces as the same
                query.replace(/\s/g, '.'),
                query.replace(/\./g, ' ')
            ];
        }
    }

    meetsCriteria(viewFile: ViewFile): boolean {
        if (this._name == null || this._name === '') { return true; }
        const search = viewFile.name.toLowerCase();
        return this.queryCandidates.some(candidate => search.indexOf(candidate) >= 0);
    }
}

/**
 * ViewFileFilterService class provides filtering services for
 * view files
 *
 * This class responds to changes in the filter settings and
 * applies the appropriate filters to the ViewFileService
 */
@Injectable({
    providedIn: 'root'
})
export class ViewFileFilterService {
    private statusFilter: StatusFilterCriteria | null = null;
    private nameFilter: NameFilterCriteria | null = null;

    private logger = inject(LoggerService);
    private viewFileService = inject(ViewFileService);
    private viewFileOptionsService = inject(ViewFileOptionsService);

    public init(): void {
        this.viewFileOptionsService.options.subscribe(options => {
            let updateFilterCriteria = false;

            // Check to see if status filter changed
            if (this.statusFilter == null ||
                    this.statusFilter.status !== options.selectedStatusFilter) {
                updateFilterCriteria = true;
                this.statusFilter = new StatusFilterCriteria(options.selectedStatusFilter);
                this.logger.debug('Status filter set to: ' + options.selectedStatusFilter);
            }

            // Check to see if the name filter changed
            if (this.nameFilter == null ||
                    this.nameFilter.name !== options.nameFilter) {
                updateFilterCriteria = true;
                this.nameFilter = new NameFilterCriteria(options.nameFilter);
                this.logger.debug('Name filter set to: ' + options.nameFilter);
            }

            // Update the filter criteria if necessary
            if (updateFilterCriteria) {
                this.viewFileService.setFilterCriteria(this.buildFilterCriteria());
            }
        });
    }

    private buildFilterCriteria(): ViewFileFilterCriteria | null {
        if (this.statusFilter != null && this.nameFilter != null) {
            return new AndFilterCriteria(this.statusFilter, this.nameFilter);
        } else if (this.statusFilter != null) {
            return this.statusFilter;
        } else if (this.nameFilter != null) {
            return this.nameFilter;
        }
        return null;
    }
}
