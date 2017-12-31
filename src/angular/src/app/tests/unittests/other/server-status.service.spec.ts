import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {ServerStatusService} from "../../../other/server-status.service";
import {LoggerService} from "../../../common/logger.service";
import {ServerStatus} from "../../../other/server-status";


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
        serverStatusService.notifyEvent("status", JSON.stringify({
            server: {
                up: true,
                error_msg: null
            }
        }));
        tick();
        expect(count).toBe(2);
        expect(latestStatus.server.up).toBe(true);

        // Status update
        serverStatusService.notifyEvent("status", JSON.stringify({
            server: {
                up: false,
                error_msg: "uh oh spaghettios"
            }
        }));
        tick();
        expect(count).toBe(3);
        expect(latestStatus.server.up).toBe(false);
        expect(latestStatus.server.errorMessage).toBe("uh oh spaghettios");
    }));

    it("should send correct status on disconnect", fakeAsync(() => {
        // Initial status
        serverStatusService.notifyEvent("status", JSON.stringify({
            server: {
                up: true,
                error_msg: null
            }
        }));

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
