import {fakeAsync, TestBed, tick} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";
import {Observable} from "rxjs/Observable";

import {BaseWebService, WebReaction} from "../../../common/base-web.service";
import {LoggerService} from "../../../common/logger.service";
import {createMockEventSource, MockEventSource} from "../../mocks/common/mock-event-source.ts";
import {EventSourceFactory} from "../../../common/base-stream.service";


class TestBaseWebService extends BaseWebService {
    onConnectedChangedCallOrder = [];

    public onConnectedChanged(connected: boolean): void {
        this.onConnectedChangedCallOrder.push(connected);
    }

    public sendRequest(url: string): Observable<WebReaction> {
        return super.sendRequest(url);
    }
}

describe("Testing base web service", () => {
    let baseWebService: TestBaseWebService;
    let httpMock: HttpTestingController;

    let mockEventSource: MockEventSource;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                TestBaseWebService,
                LoggerService,
            ]
        });

        spyOn(EventSourceFactory, 'createEventSource').and.callFake(
            (url: string) => {
                mockEventSource = createMockEventSource(url);
                return mockEventSource;
            }
        );

        baseWebService = TestBed.get(TestBaseWebService);
        httpMock = TestBed.get(HttpTestingController);

        // Initialize base web service
        baseWebService.onInit();
    });

    it("should create an instance", () => {
        expect(baseWebService).toBeDefined();
    });

    it("should use server status for connection stream", () => {
        expect(mockEventSource.url).toBe("/server/status-stream");
        expect(mockEventSource.eventListeners.size).toBe(1);
        expect(mockEventSource.eventListeners.has("status")).toBe(true);
    });

    it("should notify on first connection success", fakeAsync(() => {
        spyOn(baseWebService, "onConnectedChanged");

        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();

        expect(baseWebService.onConnectedChanged).toHaveBeenCalledTimes(1);
        expect(baseWebService.onConnectedChanged).toHaveBeenCalledWith(true);
    }));

    it("should NOT notify on first connection failure", fakeAsync(() => {
        spyOn(baseWebService, "onConnectedChanged");

        mockEventSource.onerror(new Event("bad event"));
        tick();

        expect(baseWebService.onConnectedChanged).toHaveBeenCalledTimes(0);
        tick(4000);
    }));

    it("should notify on disconnection", fakeAsync(() => {
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        mockEventSource.onerror(new Event("bad event"));
        tick();
        expect(baseWebService.onConnectedChangedCallOrder).toEqual([true, false]);
        tick(4000);
    }));

    it("should notify on re-connection", fakeAsync(() => {
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        mockEventSource.onerror(new Event("bad event"));
        tick(4000);
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        expect(baseWebService.onConnectedChangedCallOrder).toEqual([true, false, true]);
        tick(4000);
    }));

    it("should NOT notify on repeated disconnection", fakeAsync(() => {
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        mockEventSource.onerror(new Event("bad event"));
        tick();
        mockEventSource.onerror(new Event("bad event"));
        tick();
        expect(baseWebService.onConnectedChangedCallOrder).toEqual([true, false]);
        tick(4000);
    }));

    it("should NOT notify on repeated re-connection", fakeAsync(() => {
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
        expect(baseWebService.onConnectedChangedCallOrder).toEqual([true]);
    }));

    it("should send http GET on sendRequest", fakeAsync(() => {
        // Connect the service
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();

        let subscriberIndex = 0;
        baseWebService.sendRequest("/server/request").subscribe({
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
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();

        let subscriberIndex = 0;
        baseWebService.sendRequest("/server/request").subscribe({
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
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();

        let subscriberIndex = 0;
        baseWebService.sendRequest("/server/request").subscribe({
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
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();

        let subscriberIndex = 0;
        baseWebService.sendRequest("/server/request").subscribe({
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
        baseWebService.sendRequest("/server/request").subscribe({
            next: reaction => {
                subscriberIndex++;
                expect(reaction.success).toBe(false);
            }
        });
        expect(subscriberIndex).toBe(1);
    }));

    it("should NOT issue a GET for sendRequest when disconnected", fakeAsync(() => {
        // Keep service disconnected
        baseWebService.sendRequest("/server/request").subscribe({next: () => {}});
        httpMock.expectNone("/server/request");
        httpMock.verify();
    }));
});
