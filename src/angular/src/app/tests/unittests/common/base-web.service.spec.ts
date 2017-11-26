import {TestBed} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';
import {Subject} from "rxjs/Subject";
import {Observable} from "rxjs/Observable";

import {BaseWebService, WebReaction} from "../../../common/base-web.service";
import {ServerStatusService} from "../../../other/server-status.service";
import {LoggerService} from "../../../common/logger.service";
import {ServerStatus} from "../../../other/server-status";

class ServerStatusServiceStub {
    status: Subject<ServerStatus> = new Subject();
}

class TestBaseWebService extends BaseWebService {
    onConnectedChangedCallOrder = [];

    public onConnectedChanged(connected: boolean): void {
        this.onConnectedChangedCallOrder.push(connected);
    }

    public sendRequest(url: string): Observable<WebReaction> {
        return super.sendRequest(url);
    }
}

describe('Testing base web service', () => {
    let baseWebService: TestBaseWebService;
    let statusServiceStub: ServerStatusServiceStub;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                TestBaseWebService,
                LoggerService,
                { provide: ServerStatusService, useClass: ServerStatusServiceStub },
            ]
        });

        baseWebService = TestBed.get(TestBaseWebService);
        statusServiceStub = TestBed.get(ServerStatusService);
        httpMock = TestBed.get(HttpTestingController);
    });

    it('should create an instance', () => {
        expect(baseWebService).toBeDefined();
    });

    it('should notify on first connection success', () => {
        spyOn(baseWebService, "onConnectedChanged");

        statusServiceStub.status.next(new ServerStatus({connected: true}));
        expect(baseWebService.onConnectedChanged).toHaveBeenCalledTimes(1);
        expect(baseWebService.onConnectedChanged).toHaveBeenCalledWith(true);
    });

    it('should NOT notify on first connection failure', () => {
        spyOn(baseWebService, "onConnectedChanged");

        statusServiceStub.status.next(new ServerStatus({connected: false}));
        expect(baseWebService.onConnectedChanged).toHaveBeenCalledTimes(0);
    });

    it('should notify on disconnection', () => {
        statusServiceStub.status.next(new ServerStatus({connected: true}));
        statusServiceStub.status.next(new ServerStatus({connected: false}));
        expect(baseWebService.onConnectedChangedCallOrder).toEqual([true, false]);
    });

    it('should notify on re-connection', () => {
        statusServiceStub.status.next(new ServerStatus({connected: true}));
        statusServiceStub.status.next(new ServerStatus({connected: false}));
        statusServiceStub.status.next(new ServerStatus({connected: true}));
        expect(baseWebService.onConnectedChangedCallOrder).toEqual([true, false, true]);
    });

    it('should NOT notify on repeated disconnection', () => {
        statusServiceStub.status.next(new ServerStatus({connected: true}));
        statusServiceStub.status.next(new ServerStatus({connected: false}));
        statusServiceStub.status.next(new ServerStatus({connected: false}));
        expect(baseWebService.onConnectedChangedCallOrder).toEqual([true, false]);
    });

    it('should NOT notify on repeated re-connection', () => {
        statusServiceStub.status.next(new ServerStatus({connected: true}));
        statusServiceStub.status.next(new ServerStatus({connected: true}));
        expect(baseWebService.onConnectedChangedCallOrder).toEqual([true]);
    });

    it('should send http GET on sendRequest', () => {
        // Connect the service
        statusServiceStub.status.next(new ServerStatus({connected: true}));

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
    });

    it('should return correct data on sendRequest', () => {
        // Connect the service
        statusServiceStub.status.next(new ServerStatus({connected: true}));

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
    });

    it('should get error message on sendRequest error 404', () => {
        // Connect the service
        statusServiceStub.status.next(new ServerStatus({connected: true}));

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
    });

    it('should get error message on sendRequest network error', () => {
        // Connect the service
        statusServiceStub.status.next(new ServerStatus({connected: true}));

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
    });

    it('should get error message on sendRequest when disconnected', () => {
        // Keep service disconnected
        let subscriberIndex = 0;
        baseWebService.sendRequest("/server/request").subscribe({
            next: reaction => {
                subscriberIndex++;
                expect(reaction.success).toBe(false);
            }
        });
        expect(subscriberIndex).toBe(1);
    });

    it('should NOT issue a GET for sendRequest when disconnected', () => {
        // Keep service disconnected
        baseWebService.sendRequest("/server/request").subscribe({next: value => {}});
        httpMock.expectNone("/server/request");
        httpMock.verify();
    });
});
