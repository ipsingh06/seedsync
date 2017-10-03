import {Record} from 'immutable';

/**
 * View file filter
 * Describes filter state and provider filtering helpers
 */
interface IViewFileFilter {
    downloadedFilterEnabled: boolean;
    downloadingFilterEnabled: boolean;
    queuedFilterEnabled: boolean;
    stoppedFilterEnabled: boolean;
    defaultFilterEnabled: boolean;

    allFilterSelected: boolean;
    downloadedFilterSelected: boolean;
    downloadingFilterSelected: boolean;
    queuedFilterSelected: boolean;
    stoppedFilterSelected: boolean;
    defaultFilterSelected: boolean;
}

// Boiler plate code to set up an immutable class
const DefaultViewFileFilter: IViewFileFilter = {
    downloadedFilterEnabled: null,
    downloadingFilterEnabled: null,
    queuedFilterEnabled: null,
    stoppedFilterEnabled: null,
    defaultFilterEnabled: null,

    allFilterSelected: null,
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
    downloadedFilterEnabled: boolean;
    downloadingFilterEnabled: boolean;
    queuedFilterEnabled: boolean;
    stoppedFilterEnabled: boolean;
    defaultFilterEnabled: boolean;

    allFilterSelected: boolean;
    downloadedFilterSelected: boolean;
    downloadingFilterSelected: boolean;
    queuedFilterSelected: boolean;
    stoppedFilterSelected: boolean;
    defaultFilterSelected: boolean;

    constructor(props) {
        super(props);
    }
}
