import {Record} from 'immutable';

/**
 * View file
 * Represents the View Model
 */
interface IViewFile {
    name: string;
    isDir: boolean;
    localSize: number;
    remoteSize: number;
    percentDownloaded: number;
    status: ViewFile.Status;
    downloadingSpeed: number;
    eta: number;
    fullPath: string;
    isSelected: boolean;
}

// Boiler plate code to set up an immutable class
const DefaultViewFile: IViewFile = {
    name: null,
    isDir: null,
    localSize: null,
    remoteSize: null,
    percentDownloaded: null,
    status: null,
    downloadingSpeed: null,
    eta: null,
    fullPath: null,
    isSelected: null
};
const ViewFileRecord = Record(DefaultViewFile);

/**
 * Immutable class that implements the interface
 */
export class ViewFile extends ViewFileRecord implements IViewFile {
    name: string;
    isDir: boolean;
    localSize: number;
    remoteSize: number;
    percentDownloaded: number;
    status: ViewFile.Status;
    downloadingSpeed: number;
    eta: number;
    fullPath: string;
    isSelected: boolean;

    constructor(props) {
        super(props);
    }
}

export module ViewFile {
    export enum Status {
        DEFAULT         = <any> "default",
        QUEUED          = <any> "queued",
        DOWNLOADING     = <any> "downloading",
        DOWNLOADED      = <any> "downloaded",
        STOPPED         = <any> "stopped"
    }
}
