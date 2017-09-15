import {Record} from 'immutable';

/**
 * View file
 * Represents the View Model
 */
interface IViewFile {
    name: string;
    localSize: number;
    remoteSize: number;
    status: ViewFile.Status;
}

// Boiler plate code to set up an immutable class
const DefaultViewFile: IViewFile = {
    name: null,
    localSize: null,
    remoteSize: null,
    status: null
};
const ViewFileRecord = Record(DefaultViewFile);

/**
 * Immutable class that implements the interface
 */
export class ViewFile extends ViewFileRecord implements IViewFile {
    name: string;
    localSize: number;
    remoteSize: number;
    status: ViewFile.Status;

    constructor(props) {
        super(props);
    }
}

export module ViewFile {
    export enum Status {
        DEFAULT         = <any> "default",
        QUEUED          = <any> "queued",
        DOWNLOADING     = <any> "downloading",
        DOWNLOADED      = <any> "downloaded"
    }
}
