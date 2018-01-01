import {Record} from "immutable";

/**
 * ServerStatus immutable
 */
interface IServerStatus {
    server: {
        up: boolean;
        errorMessage: string;
    };
}
const DefaultServerStatus: IServerStatus = {
    server: {
        up: null,
        errorMessage: null
    }
};
const ServerStatusRecord = Record(DefaultServerStatus);
export class ServerStatus extends ServerStatusRecord implements IServerStatus {
    server: {
        up: boolean;
        errorMessage: string;
    };

    constructor(props) {
        super(props);
    }
}

/**
 * ServerStatus as serialized by the backend.
 * Note: naming convention matches that used in JSON
 */
export interface ServerStatusJson {
    server: {
        up: boolean;
        error_msg: string;
    };
}
