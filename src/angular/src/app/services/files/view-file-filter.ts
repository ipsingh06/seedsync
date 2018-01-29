import {Record} from "immutable";

/**
 * View file filter
 * Describes filter state and provider filtering helpers
 */
interface IViewFileFilter {
    extractedFilterEnabled: boolean;
    extractingFilterEnabled: boolean;
    downloadedFilterEnabled: boolean;
    downloadingFilterEnabled: boolean;
    queuedFilterEnabled: boolean;
    stoppedFilterEnabled: boolean;
    defaultFilterEnabled: boolean;

    allFilterSelected: boolean;
    extractedFilterSelected: boolean;
    extractingFilterSelected: boolean;
    downloadedFilterSelected: boolean;
    downloadingFilterSelected: boolean;
    queuedFilterSelected: boolean;
    stoppedFilterSelected: boolean;
    defaultFilterSelected: boolean;
}

// Boiler plate code to set up an immutable class
const DefaultViewFileFilter: IViewFileFilter = {
    extractedFilterEnabled: null,
    extractingFilterEnabled: null,
    downloadedFilterEnabled: null,
    downloadingFilterEnabled: null,
    queuedFilterEnabled: null,
    stoppedFilterEnabled: null,
    defaultFilterEnabled: null,

    allFilterSelected: null,
    extractedFilterSelected: null,
    extractingFilterSelected: null,
    downloadedFilterSelected: null,
    downloadingFilterSelected: null,
    queuedFilterSelected: null,
    stoppedFilterSelected: null,
    defaultFilterSelected: null,
};
const ViewFileFilterRecord = Record(DefaultViewFileFilter);

/**
 * Immutable class that implements the interface
 */
export class ViewFileFilter extends ViewFileFilterRecord implements IViewFileFilter {
    extractedFilterEnabled: boolean;
    extractingFilterEnabled: boolean;
    downloadedFilterEnabled: boolean;
    downloadingFilterEnabled: boolean;
    queuedFilterEnabled: boolean;
    stoppedFilterEnabled: boolean;
    // noinspection JSUnusedGlobalSymbols
    defaultFilterEnabled: boolean;

    allFilterSelected: boolean;
    extractedFilterSelected: boolean;
    extractingFilterSelected: boolean;
    downloadedFilterSelected: boolean;
    downloadingFilterSelected: boolean;
    queuedFilterSelected: boolean;
    stoppedFilterSelected: boolean;
    // noinspection JSUnusedGlobalSymbols
    defaultFilterSelected: boolean;

    constructor(props) {
        super(props);
    }
}
