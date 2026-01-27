import {Record} from "immutable";

import {ViewFile} from "./view-file";

/**
 * View file options
 * Describes display related options for view files
 */
interface IViewFileOptions {
    // Show additional details about the view file
    showDetails: boolean;

    // Method to use to sort the view file list
    sortMethod: ViewFileOptions.SortMethod;

    // Status filter setting
    selectedStatusFilter: ViewFile.Status;

    // Name filter setting
    nameFilter: string;

    // Track filter pin status
    pinFilter: boolean;
}


// Boiler plate code to set up an immutable class
const DefaultViewFileOptions: IViewFileOptions = {
    showDetails: null,
    sortMethod: null,
    selectedStatusFilter: null,
    nameFilter: null,
    pinFilter: null,
};
const ViewFileOptionsRecord = Record(DefaultViewFileOptions);


/**
 * Immutable class that implements the interface
 */
export class ViewFileOptions extends ViewFileOptionsRecord implements IViewFileOptions {
    showDetails: boolean;
    sortMethod: ViewFileOptions.SortMethod;
    selectedStatusFilter: ViewFile.Status;
    nameFilter: string;
    pinFilter: boolean;

    constructor(props) {
        super(props);
    }
}

export module ViewFileOptions {
    export enum SortMethod {
        STATUS,
        NAME_ASC,
        NAME_DESC
    }
}
