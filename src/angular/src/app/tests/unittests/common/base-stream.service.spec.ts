import {TestBed} from "@angular/core/testing";

import {BaseStreamService} from "../../../common/base-stream.service";
import {createMockEventSource, MockEventSource} from "../../mocks/common/mock-event-source";
import {EventSourceFactory} from "../../../common/stream-service.registry";


// noinspection JSUnusedLocalSymbols
const DoNothing = {next: reaction => {}};


class TestBaseStreamService extends BaseStreamService {
    eventList = [];

    public registerEventName(eventName: string) {
        super.registerEventName(eventName);
    }

    protected onEvent(eventName: string, data: string) {
        console.log(eventName, data);
        this.eventList.push([eventName, data]);
    }

    public onConnected() {}

    public onDisconnected() {}
}


describe("Testing base stream service", () => {
    let baseStreamService: TestBaseStreamService;

    let mockEventSource: MockEventSource;

    beforeEach(() => {
        TestBed.configureTestingModule({
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
        spyOn(baseStreamService, "onConnected");
        spyOn(baseStreamService, "onDisconnected");
    });

    it("should create an instance", () => {
        expect(baseStreamService).toBeDefined();
    });

    it("should return all registered event names", () => {
        baseStreamService.registerEventName("event1");
        baseStreamService.registerEventName("event2");
        baseStreamService.registerEventName("event3");
        expect(baseStreamService.getEventNames()).toEqual(["event1", "event2", "event3"]);
    });

    it("should forward the event notifications", () => {
        baseStreamService.notifyEvent("event1", "data1");
        expect(baseStreamService.eventList).toEqual([
            ["event1", "data1"]
        ]);
        baseStreamService.notifyEvent("event2", "data2");
        expect(baseStreamService.eventList).toEqual([
            ["event1", "data1"], ["event2", "data2"]
        ]);
        baseStreamService.notifyEvent("event3", "data3");
        expect(baseStreamService.eventList).toEqual([
            ["event1", "data1"], ["event2", "data2"], ["event3", "data3"]
        ]);
    });

    it("should forward the connected notifications", () => {
        baseStreamService.notifyConnected();
        expect(baseStreamService.onConnected).toHaveBeenCalledTimes(1);
        baseStreamService.notifyConnected();
        expect(baseStreamService.onConnected).toHaveBeenCalledTimes(2);
    });

    it("should forward the disconnected notifications", () => {
        baseStreamService.notifyDisconnected();
        expect(baseStreamService.onDisconnected).toHaveBeenCalledTimes(1);
        baseStreamService.notifyDisconnected();
        expect(baseStreamService.onDisconnected).toHaveBeenCalledTimes(2);
    });

});
