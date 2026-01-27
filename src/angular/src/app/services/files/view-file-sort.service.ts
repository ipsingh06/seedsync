import { Injectable, inject } from '@angular/core';

import { LoggerService } from '../utils/logger.service';
import { ViewFile, ViewFileStatus } from './view-file';
import { ViewFileComparator, ViewFileService } from './view-file.service';
import { ViewFileOptionsService } from './view-file-options.service';
import { ViewFileOptionsSortMethod } from './view-file-options';

/**
 * Comparator used to sort the ViewFiles
 * First, sorts by status.
 * Second, sorts by name.
 */
const StatusComparator: ViewFileComparator = (a: ViewFile, b: ViewFile): number => {
    if (a.status !== b.status) {
        const statusPriorities: Record<ViewFileStatus, number> = {
            [ViewFileStatus.EXTRACTING]: 0,
            [ViewFileStatus.DOWNLOADING]: 1,
            [ViewFileStatus.QUEUED]: 2,
            [ViewFileStatus.EXTRACTED]: 3,
            [ViewFileStatus.DOWNLOADED]: 4,
            [ViewFileStatus.STOPPED]: 5,
            [ViewFileStatus.DEFAULT]: 6,
            [ViewFileStatus.DELETED]: 6  // intermix deleted and default
        };
        if (statusPriorities[a.status] !== statusPriorities[b.status]) {
            return statusPriorities[a.status] - statusPriorities[b.status];
        }
    }
    return a.name.localeCompare(b.name);
};

/**
 * Comparator used to sort the ViewFiles
 * Sort by name, ascending
 */
const NameAscendingComparator: ViewFileComparator = (a: ViewFile, b: ViewFile): number => {
    return a.name.localeCompare(b.name);
};

/**
 * Comparator used to sort the ViewFiles
 * Sort by name, descending
 */
const NameDescendingComparator: ViewFileComparator = (a: ViewFile, b: ViewFile): number => {
    return b.name.localeCompare(a.name);
};

/**
 * ViewFileSortService class provides sorting services for
 * view files
 *
 * This class responds to changes in the sort settings and
 * applies the appropriate comparators to the ViewFileService
 */
@Injectable({
    providedIn: 'root'
})
export class ViewFileSortService {
    private sortMethod: ViewFileOptionsSortMethod | null = null;

    private logger = inject(LoggerService);
    private viewFileService = inject(ViewFileService);
    private viewFileOptionsService = inject(ViewFileOptionsService);

    public init(): void {
        this.viewFileOptionsService.options.subscribe(options => {
            // Check if the sort method changed
            if (this.sortMethod !== options.sortMethod) {
                this.sortMethod = options.sortMethod;
                if (this.sortMethod === ViewFileOptionsSortMethod.STATUS) {
                    this.viewFileService.setComparator(StatusComparator);
                    this.logger.debug('Comparator set to: Status');
                } else if (this.sortMethod === ViewFileOptionsSortMethod.NAME_DESC) {
                    this.viewFileService.setComparator(NameDescendingComparator);
                    this.logger.debug('Comparator set to: Name Desc');
                } else if (this.sortMethod === ViewFileOptionsSortMethod.NAME_ASC) {
                    this.viewFileService.setComparator(NameAscendingComparator);
                    this.logger.debug('Comparator set to: Name Asc');
                } else {
                    this.viewFileService.setComparator(null);
                    this.logger.debug('Comparator set to: null');
                }
            }
        });
    }
}
