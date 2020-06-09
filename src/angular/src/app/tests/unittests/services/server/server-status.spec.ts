import * as Immutable from "immutable";

import {ServerStatus, ServerStatusJson} from "../../../../services/server/server-status";


describe("Testing log record initialization", () => {
    let baseJson: ServerStatusJson;
    let baseStatus: ServerStatus;

    beforeEach(() => {
        baseJson = {
            server: {
                up: true,
                error_msg: "An error message"
            },
            controller: {
                latest_local_scan_time: "1514776875.9439101",
                latest_remote_scan_time: "1524743857.3456243",
                latest_remote_scan_failed: true,
                latest_remote_scan_error: "message failure reason"
            }
        };
        baseStatus = ServerStatus.fromJson(baseJson);
    });

    it("should be immutable", () => {
        expect(baseStatus instanceof Immutable.Record).toBe(true);
    });

    it("should correctly initialize server up", () => {
        expect(baseStatus.server.up).toBe(true);
    });

    it("should correctly initialize server error message", () => {
        expect(baseStatus.server.errorMessage).toBe("An error message");
    });

    it("should correctly initialize controller latest local scan time", () => {
        expect(baseStatus.controller.latestLocalScanTime).toEqual(new Date(1514776875943));
        // Allow null
        baseJson.controller.latest_local_scan_time = null;
        const newStatus = ServerStatus.fromJson(baseJson);
        expect(newStatus.controller.latestLocalScanTime).toBeNull();
    });

    it("should correctly initialize controller latest remote scan time", () => {
        expect(baseStatus.controller.latestRemoteScanTime).toEqual(new Date(1524743857345));
        // Allow null
        baseJson.controller.latest_remote_scan_time = null;
        const newStatus = ServerStatus.fromJson(baseJson);
        expect(newStatus.controller.latestRemoteScanTime).toBeNull();
    });

    it("should correctly initialize controller failure", () => {
        expect(baseStatus.controller.latestRemoteScanFailed).toBe(true);
    });

    it("should correctly initialize controller error", () => {
        expect(baseStatus.controller.latestRemoteScanError).toBe("message failure reason");
    });
});
