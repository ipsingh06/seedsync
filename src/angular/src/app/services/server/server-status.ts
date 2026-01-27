/**
 * ServerStatus
 */
export interface ServerStatusData {
    readonly server: {
        readonly up: boolean;
        readonly errorMessage: string | null;
    };
    readonly controller: {
        readonly latestLocalScanTime: Date | null;
        readonly latestRemoteScanTime: Date | null;
        readonly latestRemoteScanFailed: boolean;
        readonly latestRemoteScanError: string | null;
    };
}

/**
 * Immutable ServerStatus class
 */
export class ServerStatus implements ServerStatusData {
    readonly server: {
        readonly up: boolean;
        readonly errorMessage: string | null;
    };
    readonly controller: {
        readonly latestLocalScanTime: Date | null;
        readonly latestRemoteScanTime: Date | null;
        readonly latestRemoteScanFailed: boolean;
        readonly latestRemoteScanError: string | null;
    };

    constructor(data: ServerStatusData) {
        this.server = Object.freeze({ ...data.server });
        this.controller = Object.freeze({ ...data.controller });
        Object.freeze(this);
    }

    /**
     * Create a new ServerStatus with updated properties
     */
    update(updates: Partial<ServerStatusData>): ServerStatus {
        return new ServerStatus({
            server: updates.server ?? this.server,
            controller: updates.controller ?? this.controller
        });
    }

    /**
     * Create from JSON response
     */
    static fromJson(json: ServerStatusJson): ServerStatus {
        let latestLocalScanTime: Date | null = null;
        if (json.controller.latest_local_scan_time != null) {
            // str -> number, then sec -> ms
            latestLocalScanTime = new Date(1000 * +json.controller.latest_local_scan_time);
        }

        let latestRemoteScanTime: Date | null = null;
        if (json.controller.latest_remote_scan_time != null) {
            // str -> number, then sec -> ms
            latestRemoteScanTime = new Date(1000 * +json.controller.latest_remote_scan_time);
        }

        return new ServerStatus({
            server: {
                up: json.server.up,
                errorMessage: json.server.error_msg ?? null
            },
            controller: {
                latestLocalScanTime,
                latestRemoteScanTime,
                latestRemoteScanFailed: json.controller.latest_remote_scan_failed,
                latestRemoteScanError: json.controller.latest_remote_scan_error ?? null
            }
        });
    }

    /**
     * Create default (disconnected) ServerStatus
     */
    static createDefault(): ServerStatus {
        return new ServerStatus({
            server: {
                up: false,
                errorMessage: null
            },
            controller: {
                latestLocalScanTime: null,
                latestRemoteScanTime: null,
                latestRemoteScanFailed: false,
                latestRemoteScanError: null
            }
        });
    }
}

/**
 * JSON structure from backend
 */
export interface ServerStatusJson {
    server: {
        up: boolean;
        error_msg: string | null;
    };
    controller: {
        latest_local_scan_time: string | null;
        latest_remote_scan_time: string | null;
        latest_remote_scan_failed: boolean;
        latest_remote_scan_error: string | null;
    };
}
