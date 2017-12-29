import {fakeAsync, TestBed, tick} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";

import {ConnectedService} from "../../../other/connected.service";
import {createMockEventSource, MockEventSource} from "../../mocks/common/mock-event-source";
import {EventSourceFactory} from "../../../common/base-stream.service";
import {LoggerService} from "../../../common/logger.service";


describe("Testing connected service", () => {
    let connectedService: ConnectedService;
    let httpMock: HttpTestingController;

    let mockEventSource: MockEventSource;

    let connectedResults: boolean[];

    beforeEach(fakeAsync(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                ConnectedService,
                LoggerService,
            ]
        });

        spyOn(EventSourceFactory, 'createEventSource').and.callFake(
            (url: string) => {
                mockEventSource = createMockEventSource(url);
                return mockEventSource;
            }
        );

        connectedService = TestBed.get(ConnectedService);
        httpMock = TestBed.get(HttpTestingController);

        // Initialize base web service
        connectedService.onInit();

        connectedResults = [];
        connectedService.connected.subscribe({
            next: connected => {
                connectedResults.push(connected);
            }
        });
        tick();
    }));

    it("should create an instance", () => {
        expect(connectedService).toBeDefined();
    });

    it("should start off unconnected", () => {
        expect(connectedResults).toEqual([false]);
    });

    it("should notify on first connection success", fakeAsync(() => {
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();

        expect(connectedResults).toEqual([false, true]);
    }));

    it("should NOT notify on first connection failure", fakeAsync(() => {
        mockEventSource.onerror(new Event("bad event"));
        tick();

        expect(connectedResults).toEqual([false]);
        tick(4000);
    }));

    it("should notify on disconnection", fakeAsync(() => {
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        mockEventSource.onerror(new Event("bad event"));
        tick();
        expect(connectedResults).toEqual([false, true, false]);
        tick(4000);
    }));

    it("should notify on re-connection", fakeAsync(() => {
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        mockEventSource.onerror(new Event("bad event"));
        tick(4000);
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        expect(connectedResults).toEqual([false, true, false, true]);
        tick(4000);
    }));

    it("should NOT notify on repeated disconnection", fakeAsync(() => {
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        mockEventSource.onerror(new Event("bad event"));
        tick();
        mockEventSource.onerror(new Event("bad event"));
        tick();
        expect(connectedResults).toEqual([false, true, false]);
        tick(4000);
    }));

    it("should NOT notify on repeated re-connection", fakeAsync(() => {
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        expect(connectedResults).toEqual([false, true]);
    }));

});
