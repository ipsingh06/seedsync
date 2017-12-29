import {fakeAsync, TestBed, tick} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";

import * as Immutable from "immutable";

import {ServerStatusService} from "../../../other/server-status.service";
import {createMockEventSource, MockEventSource} from "../../mocks/common/mock-event-source.ts";
import {LoggerService} from "../../../common/logger.service";
import {EventSourceFactory} from "../../../common/base-stream.service";
import {ServerStatus} from "../../../other/server-status";


describe("Testing server status service", () => {
    let serverStatusService: ServerStatusService;

    let mockEventSource: MockEventSource;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [],
            providers: [
                LoggerService,
                ServerStatusService
            ]
        });

        spyOn(EventSourceFactory, 'createEventSource').and.callFake(
            (url: string) => {
                mockEventSource = createMockEventSource(url);
                return mockEventSource;
            }
        );

        serverStatusService = TestBed.get(ServerStatusService);
        serverStatusService.onInit();
    });

    it("should create an instance", () => {
        expect(serverStatusService).toBeDefined();
    });

    it("should construct an event source with correct url", () => {
        expect(mockEventSource.url).toBe("/server/status-stream");
    });

    it("should register all events with the event source", () => {
        expect(mockEventSource.eventListeners.size).toBe(1);
        expect(mockEventSource.eventListeners.has("status")).toBe(true);
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
        mockEventSource.eventListeners.get("status")({data: JSON.stringify({
            server: {
                up: true,
                error_msg: null
            }
        })});
        tick();
        expect(count).toBe(2);
        expect(latestStatus.server.up).toBe(true);

        // Status update
        mockEventSource.eventListeners.get("status")({data: JSON.stringify({
            server: {
                up: false,
                error_msg: "uh oh spaghettios"
            }
        })});
        tick();
        expect(count).toBe(3);
        expect(latestStatus.server.up).toBe(false);
        expect(latestStatus.server.errorMessage).toBe("uh oh spaghettios");
    }));

    it("should send correct status on error", fakeAsync(() => {
        // Initial status
        mockEventSource.eventListeners.get("status")({data: JSON.stringify({
            server: {
                up: true,
                error_msg: null
            }
        })});

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
        mockEventSource.onerror(new Event("bad event"));
        tick();
        expect(count).toBe(2);
        expect(latestStatus.server.up).toBe(false);

        tick(4000);
    }));

});
