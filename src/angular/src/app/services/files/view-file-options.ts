import {Record} from "immutable";

/**
 * View file options
 * Describes display related options for view files
 */
interface IViewFileOptions {
    showDetails: boolean;
}


// Boiler plate code to set up an immutable class
const DefaultViewFileOptions: IViewFileOptions = {
    showDetails: null
};
const ViewFileOptionsRecord = Record(DefaultViewFileOptions);


/**
 * Immutable class that implements the interface
 */
export class ViewFileOptions extends ViewFileOptionsRecord implements IViewFileOptions {
    showDetails: boolean;

    constructor(props) {
        super(props);
    }
}
