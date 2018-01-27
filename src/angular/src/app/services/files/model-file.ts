import {Record, Set} from "immutable";

/**
 * Model file received from the backend
 * Note: Naming convention matches that used in the JSON
 */
interface IModelFile {
    name: string;
    is_dir: boolean;
    local_size: number;
    remote_size: number;
    state: ModelFile.State;
    downloading_speed: number;
    eta: number;
    full_path: string;
    is_extractable: boolean;
    children: Set<ModelFile>;
}

// Boiler plate code to set up an immutable class
const DefaultModelFile: IModelFile = {
    name: null,
    is_dir: null,
    local_size: null,
    remote_size: null,
    state: null,
    downloading_speed: null,
    eta: null,
    full_path: null,
    is_extractable: null,
    children: null
};
const ModelFileRecord = Record(DefaultModelFile);

/**
 * Immutable class that implements the interface
 * Pattern inspired by: http://blog.angular-university.io/angular-2-application
 *                      -architecture-building-flux-like-apps-using-redux-and
 *                      -immutable-js-js
 */
export class ModelFile extends ModelFileRecord implements IModelFile {
    name: string;
    is_dir: boolean;
    local_size: number;
    remote_size: number;
    state: ModelFile.State;
    downloading_speed: number;
    eta: number;
    full_path: string;
    is_extractable: boolean;
    children: Set<ModelFile>;

    constructor(props) {
        super(props);
    }
}

// Additional types
export module ModelFile {
    export function fromJson(json): ModelFile {
        // Create immutable objects for children as well
        const children: ModelFile[] = [];
        for (const child of json.children) {
            children.push(ModelFile.fromJson(child));
        }
        json.children = Set<ModelFile>(children);

        // State mapping
        json.state = ModelFile.State[json.state.toUpperCase()];

        return new ModelFile(json);
    }

    export enum State {
        DEFAULT         = <any> "default",
        QUEUED          = <any> "queued",
        DOWNLOADING     = <any> "downloading",
        DOWNLOADED      = <any> "downloaded",
        DELETED         = <any> "deleted",
        EXTRACTING      = <any> "extracting",
        EXTRACTED       = <any> "extracted"
    }
}
