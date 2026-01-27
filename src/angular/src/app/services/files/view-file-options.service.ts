import { Injectable, inject } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';

import { LoggerService } from '../utils/logger.service';
import { ViewFileOptions, ViewFileOptionsSortMethod } from './view-file-options';
import { ViewFileStatus } from './view-file';
import { StorageKeys } from '../../common/storage-keys';

/**
 * ViewFileOptionsService class provides display option services
 * for view files
 *
 * This class is used to broadcast changes to the display options
 */
@Injectable({
    providedIn: 'root'
})
export class ViewFileOptionsService {
    private optionsSubject: BehaviorSubject<ViewFileOptions>;
    private logger = inject(LoggerService);

    constructor() {
        // Load some options from storage
        const showDetails = this.getStorageValue<boolean>(StorageKeys.VIEW_OPTION_SHOW_DETAILS) ?? false;
        const sortMethod = this.getStorageValue<ViewFileOptionsSortMethod>(StorageKeys.VIEW_OPTION_SORT_METHOD) ?? ViewFileOptionsSortMethod.STATUS;
        const pinFilter = this.getStorageValue<boolean>(StorageKeys.VIEW_OPTION_PIN) ?? false;

        this.optionsSubject = new BehaviorSubject(
            new ViewFileOptions({
                showDetails,
                sortMethod,
                selectedStatusFilter: null,
                nameFilter: '',
                pinFilter
            })
        );
    }

    private getStorageValue<T>(key: string): T | null {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : null;
        } catch {
            return null;
        }
    }

    private setStorageValue<T>(key: string, value: T): void {
        localStorage.setItem(key, JSON.stringify(value));
    }

    get options(): Observable<ViewFileOptions> {
        return this.optionsSubject.asObservable();
    }

    public setShowDetails(show: boolean): void {
        const options = this.optionsSubject.getValue();
        if (options.showDetails !== show) {
            const newOptions = options.update({ showDetails: show });
            this.optionsSubject.next(newOptions);
            this.setStorageValue(StorageKeys.VIEW_OPTION_SHOW_DETAILS, show);
            this.logger.debug('ViewOption showDetails set to: ' + newOptions.showDetails);
        }
    }

    public setSortMethod(sortMethod: ViewFileOptionsSortMethod): void {
        const options = this.optionsSubject.getValue();
        if (options.sortMethod !== sortMethod) {
            const newOptions = options.update({ sortMethod });
            this.optionsSubject.next(newOptions);
            this.setStorageValue(StorageKeys.VIEW_OPTION_SORT_METHOD, sortMethod);
            this.logger.debug('ViewOption sortMethod set to: ' + newOptions.sortMethod);
        }
    }

    public setSelectedStatusFilter(status: ViewFileStatus | null): void {
        const options = this.optionsSubject.getValue();
        if (options.selectedStatusFilter !== status) {
            const newOptions = options.update({ selectedStatusFilter: status });
            this.optionsSubject.next(newOptions);
            this.logger.debug('ViewOption selectedStatusFilter set to: ' + newOptions.selectedStatusFilter);
        }
    }

    public setNameFilter(name: string): void {
        const options = this.optionsSubject.getValue();
        if (options.nameFilter !== name) {
            const newOptions = options.update({ nameFilter: name });
            this.optionsSubject.next(newOptions);
            this.logger.debug('ViewOption nameFilter set to: ' + newOptions.nameFilter);
        }
    }

    public setPinFilter(pinned: boolean): void {
        const options = this.optionsSubject.getValue();
        if (options.pinFilter !== pinned) {
            const newOptions = options.update({ pinFilter: pinned });
            this.optionsSubject.next(newOptions);
            this.setStorageValue(StorageKeys.VIEW_OPTION_PIN, pinned);
            this.logger.debug('ViewOption pinFilter set to: ' + newOptions.pinFilter);
        }
    }
}
