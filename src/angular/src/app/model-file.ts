import {Record, Set} from 'immutable';

/**
 * Model file received from the backend
 * Note: Naming convention matches that used in the JSON
 */
interface IModelFile {
    name: string;
    local_size: number;
    remote_size: number;
    children: Set<ModelFile>;
}

// Boiler plate code to set up an immutable class
const DefaultModelFile: IModelFile = {
    name: null,
    local_size: null,
    remote_size: null,
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
    local_size: number;
    remote_size: number;
    children: Set<ModelFile>;

    constructor(props) {
        // Create immutable objects for children as well
        let children: ModelFile[] = [];
        for(let child of props.children) {
            children.push(new ModelFile(child));
        }
        props.children = children;

        super(props);
    }
}
