import {TestBed} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";
import {Subject} from "rxjs/Subject";
import {Observable} from "rxjs/Observable";

import {BaseStreamService, EventSourceFactory} from "../../../common/base-stream.service";


class TestBaseStreamService extends BaseStreamService {
    eventList = [];

    public set testStreamUrl(url: string) {
        this.streamUrl = url;
    }

    public registerEvent(eventName: string) {
        super.registerEvent(eventName);
    }

    public rescheduleCreateSseObserver() {
        // Do nothing
    }

    protected onEvent(eventName: string, data: string) {
        console.log(eventName, data);
        this.eventList.push({name: eventName, data: data});
    }

    public onError(err: any) {}
}


describe("Testing base stream service", () => {
    let baseStreamService: TestBaseStreamService;
    let sseSpy: any;
    let eventListeners: any;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
            ],
            providers: [
                TestBaseStreamService,
            ]
        });

        eventListeners = [];
        sseSpy = jasmine.createSpyObj(
            'sseSpy',
            [
                'addEventListener',
                'close'
            ]
        );
        sseSpy.addEventListener.and.callFake(
            (name, listener) => {
                eventListeners.push({name: name, listener: listener});
            }
        );
        spyOn(EventSourceFactory, 'createEventSource').and.returnValue(sseSpy);

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
        expect(EventSourceFactory.createEventSource).toHaveBeenCalledWith("/stream/url/for/service");
    });

    it("should register all events with the event source", () => {
        expect(sseSpy.addEventListener).toHaveBeenCalledTimes(3);
        expect(eventListeners.length).toBe(3);
        expect(eventListeners[0]["name"]).toBe("event1");
        expect(eventListeners[1]["name"]).toBe("event2");
        expect(eventListeners[2]["name"]).toBe("event3");
    });

    it("should set an error handler on the event source", () => {
        expect(sseSpy.onerror).toBeDefined();
    });

    it("forwards event name and data", () => {
        eventListeners[2]["listener"]({data: "data3"});
        eventListeners[0]["listener"]({data: "data1"});
        eventListeners[1]["listener"]({data: "data2"});
        expect(baseStreamService.eventList.length).toBe(3);
        expect(baseStreamService.eventList).toEqual(
            [
                {name: "event3", data: "data3"},
                {name: "event1", data: "data1"},
                {name: "event2", data: "data2"},
            ]
        )
    });

    it("should forward errors", () => {
        spyOn(baseStreamService, 'onError');
        spyOn(baseStreamService, 'rescheduleCreateSseObserver');
        sseSpy.onerror({msg: "error msg", code: 55});
        expect(baseStreamService.onError).toHaveBeenCalledWith({msg: "error msg", code: 55});
        expect(baseStreamService.rescheduleCreateSseObserver).toHaveBeenCalledTimes(1);
    });

});
