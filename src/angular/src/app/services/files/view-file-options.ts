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
}


// Boiler plate code to set up an immutable class
const DefaultViewFileOptions: IViewFileOptions = {
    showDetails: null,
    sortMethod: null,
    selectedStatusFilter: null,
    nameFilter: null,
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
