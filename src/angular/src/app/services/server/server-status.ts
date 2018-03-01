import {Record} from "immutable";

/**
 * ServerStatus immutable
 */
interface IServerStatus {
    server: {
        up: boolean;
        errorMessage: string;
    };

    controller: {
        latestLocalScanTime: Date;
        latestRemoteScanTime: Date;
    };
}
const DefaultServerStatus: IServerStatus = {
    server: {
        up: null,
        errorMessage: null
    },
    controller: {
        latestLocalScanTime: null,
        latestRemoteScanTime: null
    }
};
const ServerStatusRecord = Record(DefaultServerStatus);
export class ServerStatus extends ServerStatusRecord implements IServerStatus {
    server: {
        up: boolean;
        errorMessage: string;
    };

    controller: {
        latestLocalScanTime: Date;
        latestRemoteScanTime: Date;
    };

    constructor(props) {
        super(props);
    }
}


export module ServerStatus {
    export function fromJson(json: ServerStatusJson): ServerStatus {
        let latestLocalScanTime: Date = null;
        if(json.controller.latest_local_scan_time != null) {
            // str -> number, then sec -> ms
            latestLocalScanTime = new Date(1000 * +json.controller.latest_local_scan_time);
        }

        let latestRemoteScanTime: Date = null;
        if(json.controller.latest_remote_scan_time != null) {
            // str -> number, then sec -> ms
            latestRemoteScanTime = new Date(1000 * +json.controller.latest_remote_scan_time);
        }

        return new ServerStatus({
            server: {
                up: json.server.up,
                errorMessage: json.server.error_msg
            },
            controller: {
                latestLocalScanTime: latestLocalScanTime,
                latestRemoteScanTime: latestRemoteScanTime
            }
        });
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

    controller: {
        latest_local_scan_time: string;
        latest_remote_scan_time: string;
    }
}
