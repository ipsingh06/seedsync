import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {ServerStatusService} from "../../../../services/server/server-status.service";
import {LoggerService} from "../../../../services/utils/logger.service";
import {ServerStatus, ServerStatusJson} from "../../../../services/server/server-status";


describe("Testing server status service", () => {
    let serverStatusService: ServerStatusService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                LoggerService,
                ServerStatusService
            ]
        });

        serverStatusService = TestBed.get(ServerStatusService);
    });

    it("should create an instance", () => {
        expect(serverStatusService).toBeDefined();
    });

    it("should register all events with the event source", () => {
        expect(serverStatusService.getEventNames()).toEqual(
            ["status"]
        );
    });

    it("should send correct status on event", fakeAsync(() => {
        let count = 0;
        let latestStatus: ServerStatus = null;
        serverStatusService.status.subscribe({
            next: status => {
                count++;
                latestStatus = status;
            }
        });

        // Initial status
        tick();
        expect(count).toBe(1);
        expect(latestStatus.server.up).toBe(false);

        // New status
        let statusJson: ServerStatusJson = {
            server: {
                up: true,
                error_msg: null
            },
            controller: {
                latest_local_scan_time: null,
                latest_remote_scan_time: null
            }
        };
        serverStatusService.notifyEvent("status", JSON.stringify(statusJson));
        tick();
        expect(count).toBe(2);
        expect(latestStatus.server.up).toBe(true);

        // Status update
        statusJson.server.up = false;
        statusJson.server.error_msg = "uh oh spaghettios";
        serverStatusService.notifyEvent("status", JSON.stringify(statusJson));
        tick();
        expect(count).toBe(3);
        expect(latestStatus.server.up).toBe(false);
        expect(latestStatus.server.errorMessage).toBe("uh oh spaghettios");
    }));

    it("should send correct status on disconnect", fakeAsync(() => {
        // Initial status
        let statusJson: ServerStatusJson = {
            server: {
                up: true,
                error_msg: null
            },
            controller: {
                latest_local_scan_time: null,
                latest_remote_scan_time: null
            }
        };
        serverStatusService.notifyEvent("status", JSON.stringify(statusJson));

        let count = 0;
        let latestStatus: ServerStatus = null;
        serverStatusService.status.subscribe({
            next: status => {
                count++;
                latestStatus = status;
            }
        });

        tick();
        expect(count).toBe(1);

        // Error
        serverStatusService.notifyDisconnected();
        tick();
        expect(count).toBe(2);
        expect(latestStatus.server.up).toBe(false);
    }));

});
