import {fakeAsync, TestBed, tick} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";

import {BaseStreamService, WebReaction} from "../../../common/base-stream.service";
import {createMockEventSource, MockEventSource} from "../../mocks/common/mock-event-source";
import {LoggerService} from "../../../common/logger.service";
import {EventSourceFactory} from "../../../common/stream-service.registry";
import {Observable} from "rxjs/Observable";


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


    public sendRequest(url: string): Observable<WebReaction> {
        return super.sendRequest(url);
    }
}


describe("Testing base stream service", () => {
    let baseStreamService: TestBaseStreamService;

    let httpMock: HttpTestingController;
    let mockEventSource: MockEventSource;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                LoggerService,
                TestBaseStreamService,
            ]
        });

        spyOn(EventSourceFactory, 'createEventSource').and.callFake(
            (url: string) => {
                mockEventSource = createMockEventSource(url);
                return mockEventSource;
            }
        );
        httpMock = TestBed.get(HttpTestingController);

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



    it("should send http GET on sendRequest", fakeAsync(() => {
        // Connect the service
        baseStreamService.notifyConnected();
        tick();

        let subscriberIndex = 0;
        baseStreamService.sendRequest("/server/request").subscribe({
            next: reaction => {
                subscriberIndex++;
                expect(reaction.success).toBe(true);
            }
        });
        httpMock.expectOne("/server/request").flush("success");

        expect(subscriberIndex).toBe(1);
        httpMock.verify();
    }));

    it("should return correct data on sendRequest", fakeAsync(() => {
        // Connect the service
        baseStreamService.notifyConnected();
        tick();

        let subscriberIndex = 0;
        baseStreamService.sendRequest("/server/request").subscribe({
            next: reaction => {
                subscriberIndex++;
                expect(reaction.success).toBe(true);
                expect(reaction.data).toBe("this is some data");
            }
        });
        httpMock.expectOne("/server/request").flush("this is some data");

        expect(subscriberIndex).toBe(1);
        httpMock.verify();
    }));

    it("should get error message on sendRequest error 404", fakeAsync(() => {
        // Connect the service
        baseStreamService.notifyConnected();
        tick();

        let subscriberIndex = 0;
        baseStreamService.sendRequest("/server/request").subscribe({
            next: reaction => {
                subscriberIndex++;
                expect(reaction.success).toBe(false);
                expect(reaction.errorMessage).toBe("Not found");
            }
        });
        httpMock.expectOne("/server/request").flush(
        "Not found",
        {status: 404, statusText: "Bad Request"}
        );

        expect(subscriberIndex).toBe(1);
        httpMock.verify();
    }));

    it("should get error message on sendRequest network error", fakeAsync(() => {
        // Connect the service
        baseStreamService.notifyConnected();
        tick();

        let subscriberIndex = 0;
        baseStreamService.sendRequest("/server/request").subscribe({
            next: reaction => {
                subscriberIndex++;
                expect(reaction.success).toBe(false);
                expect(reaction.errorMessage).toBe("mock error");
            }
        });
        httpMock.expectOne("/server/request").error(new ErrorEvent("mock error"));

        expect(subscriberIndex).toBe(1);
        httpMock.verify();
    }));

    it("should get error message on sendRequest when disconnected", fakeAsync(() => {
        // Keep service disconnected
        let subscriberIndex = 0;
        baseStreamService.sendRequest("/server/request").subscribe({
            next: reaction => {
                subscriberIndex++;
                expect(reaction.success).toBe(false);
            }
        });
        expect(subscriberIndex).toBe(1);
    }));

    it("should NOT issue a GET for sendRequest when disconnected", fakeAsync(() => {
        // Keep service disconnected
        baseStreamService.sendRequest("/server/request").subscribe({next: () => {}});
        httpMock.expectNone("/server/request");
        httpMock.verify();
    }));

});
