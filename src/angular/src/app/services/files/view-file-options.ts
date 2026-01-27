import { ViewFileStatus } from './view-file';

/**
 * View file options - Describes display related options for view files
 */
export interface ViewFileOptionsData {
    // Show additional details about the view file
    readonly showDetails: boolean;
    // Method to use to sort the view file list
    readonly sortMethod: ViewFileOptionsSortMethod;
    // Status filter setting
    readonly selectedStatusFilter: ViewFileStatus | null;
    // Name filter setting
    readonly nameFilter: string;
    // Track filter pin status
    readonly pinFilter: boolean;
}

export enum ViewFileOptionsSortMethod {
    STATUS = 'STATUS',
    NAME_ASC = 'NAME_ASC',
    NAME_DESC = 'NAME_DESC'
}

/**
 * Immutable ViewFileOptions class
 */
export class ViewFileOptions implements ViewFileOptionsData {
    readonly showDetails: boolean;
    readonly sortMethod: ViewFileOptionsSortMethod;
    readonly selectedStatusFilter: ViewFileStatus | null;
    readonly nameFilter: string;
    readonly pinFilter: boolean;

    constructor(data: ViewFileOptionsData) {
        this.showDetails = data.showDetails;
        this.sortMethod = data.sortMethod;
        this.selectedStatusFilter = data.selectedStatusFilter;
        this.nameFilter = data.nameFilter;
        this.pinFilter = data.pinFilter;
        Object.freeze(this);
    }

    /**
     * Create a new ViewFileOptions with updated properties
     */
    update(updates: Partial<ViewFileOptionsData>): ViewFileOptions {
        return new ViewFileOptions({
            showDetails: updates.showDetails ?? this.showDetails,
            sortMethod: updates.sortMethod ?? this.sortMethod,
            selectedStatusFilter: updates.selectedStatusFilter !== undefined ? updates.selectedStatusFilter : this.selectedStatusFilter,
            nameFilter: updates.nameFilter ?? this.nameFilter,
            pinFilter: updates.pinFilter ?? this.pinFilter
        });
    }

    /**
     * Create default ViewFileOptions
     */
    static createDefault(): ViewFileOptions {
        return new ViewFileOptions({
            showDetails: false,
            sortMethod: ViewFileOptionsSortMethod.STATUS,
            selectedStatusFilter: null,
            nameFilter: '',
            pinFilter: false
        });
    }
}
