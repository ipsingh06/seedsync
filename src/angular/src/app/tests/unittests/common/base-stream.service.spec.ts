import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {BaseStreamService, EventSourceFactory} from "../../../common/base-stream.service";
import {createMockEventSource, MockEventSource} from "../../mocks/common/mock-event-source.ts";


class TestBaseStreamService extends BaseStreamService {
    eventList = [];

    public set testStreamUrl(url: string) {
        this.streamUrl = url;
    }

    public registerEvent(eventName: string) {
        super.registerEvent(eventName);
    }

    protected onEvent(eventName: string, data: string) {
        console.log(eventName, data);
        this.eventList.push({name: eventName, data: data});
    }

    public onError(err: any) {}
}


describe("Testing base stream service", () => {
    let baseStreamService: TestBaseStreamService;

    let mockEventSource: MockEventSource;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
            ],
            providers: [
                TestBaseStreamService,
            ]
        });

        spyOn(EventSourceFactory, 'createEventSource').and.callFake(
            (url: string) => {
                mockEventSource = createMockEventSource(url);
                return mockEventSource;
            }
        );

        baseStreamService = TestBed.get(TestBaseStreamService);
        baseStreamService.testStreamUrl = "/stream/url/for/service";
        baseStreamService.registerEvent("event1");
        baseStreamService.registerEvent("event2");
        baseStreamService.registerEvent("event3");
        baseStreamService.onInit();
    });

    it("should create an instance", () => {
        expect(baseStreamService).toBeDefined();
    });

    it("should construct an event source with correct url", () => {
        expect(mockEventSource.url).toBe("/stream/url/for/service");
    });

    it("should register all events with the event source", () => {
        expect(mockEventSource.addEventListener).toHaveBeenCalledTimes(3);
        expect(mockEventSource.eventListeners.size).toBe(3);
        expect(mockEventSource.eventListeners.has("event1")).toBe(true);
        expect(mockEventSource.eventListeners.has("event2")).toBe(true);
        expect(mockEventSource.eventListeners.has("event3")).toBe(true);
    });

    it("should set an error handler on the event source", () => {
        expect(mockEventSource.onerror).toBeDefined();
    });

    it("forwards event name and data", () => {
        mockEventSource.eventListeners.get("event3")({data: "data3"});
        mockEventSource.eventListeners.get("event1")({data: "data1"});
        mockEventSource.eventListeners.get("event2")({data: "data2"});
        expect(baseStreamService.eventList.length).toBe(3);
        expect(baseStreamService.eventList).toEqual(
            [
                {name: "event3", data: "data3"},
                {name: "event1", data: "data1"},
                {name: "event2", data: "data2"},
            ]
        )
    });

    it("should forward errors", fakeAsync(() => {
        spyOn(baseStreamService, 'onError');
        mockEventSource.onerror(new Event("bad event"));
        expect(baseStreamService.onError).toHaveBeenCalledWith(new Event("bad event"));
        tick(4000);
    }));

});
