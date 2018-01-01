import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {createMockEventSource, MockEventSource} from "../../../mocks/mock-event-source";
import {LoggerService} from "../../../../services/utils/logger.service";
import {EventSourceFactory, IStreamService, StreamDispatchService, StreamServiceRegistry} from "../../../../services/base/stream-service.registry";
import {ModelFileService} from "../../../../services/files/model-file.service";
import {ServerStatusService} from "../../../../services/server/server-status.service";
import {ConnectedService} from "../../../../services/utils/connected.service";
import {LogService} from "../../../../services/logs/log.service";


class MockStreamService implements IStreamService {
    eventList = [];
    connectedSeq = [];

    getEventNames(): string[] {
        throw new Error("Method not implemented.");
    }

    notifyConnected() {
        this.connectedSeq.push(true);
    }

    notifyDisconnected() {
        this.connectedSeq.push(false);
    }

    notifyEvent(eventName: string, data: string) {
        this.eventList.push([eventName, data]);
    }
}


describe("Testing stream dispatch service", () => {
    let dispatchService: StreamDispatchService;

    let mockEventSource: MockEventSource;
    let mockService1: MockStreamService;
    let mockService2: MockStreamService;

    beforeEach(fakeAsync(() => {
        TestBed.configureTestingModule({
            providers: [
                LoggerService,
                StreamDispatchService
            ]
        });

        spyOn(EventSourceFactory, "createEventSource").and.callFake(
            (url: string) => {
                mockEventSource = createMockEventSource(url);
                return mockEventSource;
            }
        );
        mockService1 = new MockStreamService();
        mockService2 = new MockStreamService();
        spyOn(mockService1, "getEventNames").and.returnValue(['event1a', 'event1b']);
        spyOn(mockService2, "getEventNames").and.returnValue(['event2a', 'event2b']);

        dispatchService = TestBed.get(StreamDispatchService);

        dispatchService.registerService(mockService1);
        dispatchService.registerService(mockService2);
        dispatchService.onInit();
        tick();
    }));

    it("should create an instance", () => {
        expect(dispatchService).toBeDefined();
    });

    it("should construct an event source with correct url", fakeAsync(() => {
        expect(mockEventSource.url).toBe("/server/stream");
    }));

    it("should register all events with the event source", fakeAsync(() => {
        expect(mockEventSource.addEventListener).toHaveBeenCalledTimes(4);
        expect(mockEventSource.eventListeners.size).toBe(4);
        expect(mockEventSource.eventListeners.has("event1a")).toBe(true);
        expect(mockEventSource.eventListeners.has("event1b")).toBe(true);
        expect(mockEventSource.eventListeners.has("event2a")).toBe(true);
        expect(mockEventSource.eventListeners.has("event2b")).toBe(true);
    }));

    it("should set an error handler on the event source", fakeAsync(() => {
        expect(mockEventSource.onerror).toBeDefined();
    }));

    it("should forward name and data correctly", fakeAsync(() => {
        mockEventSource.eventListeners.get("event1a")({data: "data1a"});
        tick();
        expect(mockService1.eventList).toEqual([
            ["event1a", "data1a"]
        ]);
        expect(mockService2.eventList).toEqual([]);

        mockEventSource.eventListeners.get("event1b")({data: "data1b"});
        tick();
        expect(mockService1.eventList).toEqual([
            ["event1a", "data1a"], ["event1b", "data1b"]
        ]);
        expect(mockService2.eventList).toEqual([]);

        mockEventSource.eventListeners.get("event2a")({data: "data2a"});
        tick();
        expect(mockService1.eventList).toEqual([
            ["event1a", "data1a"], ["event1b", "data1b"]
        ]);
        expect(mockService2.eventList).toEqual([
            ["event2a", "data2a"]
        ]);

        mockEventSource.eventListeners.get("event2b")({data: "data2b"});
        tick();
        expect(mockService1.eventList).toEqual([
            ["event1a", "data1a"], ["event1b", "data1b"]
        ]);
        expect(mockService2.eventList).toEqual([
            ["event2a", "data2a"], ["event2b", "data2b"]
        ]);

        mockEventSource.eventListeners.get("event1b")({data: "data1bbb"});
        tick();
        expect(mockService1.eventList).toEqual([
            ["event1a", "data1a"], ["event1b", "data1b"], ["event1b", "data1bbb"]
        ]);
        expect(mockService2.eventList).toEqual([
            ["event2a", "data2a"], ["event2b", "data2b"]
        ]);
    }));

    it("should call connect on open", fakeAsync(() => {
        mockEventSource.onopen(new Event("connected"));
        tick();
        expect(mockService1.connectedSeq).toEqual([true]);
        expect(mockService2.connectedSeq).toEqual([true]);
    }));

    it("should call disconnect on error", fakeAsync(() => {
        mockEventSource.onerror(new Event("bad event"));
        tick();
        expect(mockService1.connectedSeq).toEqual([false]);
        expect(mockService2.connectedSeq).toEqual([false]);
        tick(4000);
    }));

    it("should send events after reconnect", fakeAsync(() => {
        mockEventSource.onopen(new Event("connected"));
        tick();
        mockEventSource.onerror(new Event("bad event"));
        tick(4000);
        mockEventSource.onopen(new Event("connected"));
        tick();
        mockEventSource.eventListeners.get("event1a")({data: "data1a"});
        tick();
        expect(mockService1.eventList).toEqual([
            ["event1a", "data1a"]
        ]);
        expect(mockService2.eventList).toEqual([]);
        mockEventSource.eventListeners.get("event2b")({data: "data2b"});
        tick();
        expect(mockService1.eventList).toEqual([["event1a", "data1a"]]);
        expect(mockService2.eventList).toEqual([["event2b", "data2b"]]);
    }));
});



describe("Testing stream service registry", () => {
    let registry: StreamServiceRegistry;

    let mockDispatch;

    let mockModelFileService;
    let mockServerStatusService;
    let mockConnectedService;
    let mockLogService;

    let registered;

    beforeEach(() => {
        registered = [];

        mockDispatch = jasmine.createSpyObj("mockDispatch", ["registerService"]);
        mockDispatch.registerService.and.callFake(value => registered.push(value));

        mockModelFileService = jasmine.createSpy("mockModelFileService");
        mockServerStatusService = jasmine.createSpy("mockServerStatusService");
        mockConnectedService = jasmine.createSpy("mockConnectedService");
        mockLogService = jasmine.createSpy("mockLogService");

        TestBed.configureTestingModule({
            providers: [
                StreamServiceRegistry,
                LoggerService,
                {provide: StreamDispatchService, useValue: mockDispatch},
                {provide: ModelFileService, useValue: mockModelFileService},
                {provide: ServerStatusService, useValue: mockServerStatusService},
                {provide: ConnectedService, useValue: mockConnectedService},
                {provide: LogService, useValue: mockLogService}
            ]
        });

        registry = TestBed.get(StreamServiceRegistry);
    });

    it("should create an instance", () => {
        expect(registry).toBeDefined();
    });

    it("should register model file service", () => {
        expect(registered.includes(mockModelFileService)).toBe(true);
    });

    it("should register server status service", () => {
        expect(registered.includes(mockServerStatusService)).toBe(true);
    });

    it("should register connected service", () => {
        expect(registered.includes(mockConnectedService)).toBe(true);
    });

    it("should register log service", () => {
        expect(registered.includes(mockLogService)).toBe(true);
    });
});
