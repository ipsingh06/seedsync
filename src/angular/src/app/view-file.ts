import {Record, Set} from 'immutable';

/**
 * View file
 * Represents the View Model
 */
interface IViewFile {
    name: string;
    localSize: number;
    remoteSize: number;
}

// Boiler plate code to set up an immutable class
const DefaultViewFile: IViewFile = {
    name: null,
    localSize: null,
    remoteSize: null
};
const ViewFileRecord = Record(DefaultViewFile);

/**
 * Immutable class that implements the interface
 */
export class ViewFile extends ViewFileRecord implements IViewFile {
    name: string;
    localSize: number;
    remoteSize: number;

    constructor(props) {
        super(props);
    }
}
