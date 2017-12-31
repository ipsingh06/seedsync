import {fakeAsync, TestBed, tick} from "@angular/core/testing";
import {Observable} from "rxjs/Observable";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";

import {BaseWebService} from "../../../common/base-web.service";
import {WebReaction} from "../../../common/base-stream.service";
import {StreamServiceRegistry} from "../../../common/stream-service.registry";
import {MockStreamServiceRegistry} from "../../mocks/mock-stream-service.registry";
import {LoggerService} from "../../../common/logger.service";
import {RestService} from "../../../other/rest.service";
import {ConnectedService} from "../../../other/connected.service";


// noinspection JSUnusedLocalSymbols
const DoNothing = {next: reaction => {}};


class TestBaseWebService extends BaseWebService {

    public sendRequest(url: string): Observable<WebReaction> {
        return super.sendRequest(url);
    }

    public onConnected(): void {}

    public onDisconnected(): void {}
}

describe("Testing base web service", () => {
    let baseWebService: TestBaseWebService;

    let mockRegistry: MockStreamServiceRegistry;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                TestBaseWebService,
                LoggerService,
                RestService,
                ConnectedService,
                {provide: StreamServiceRegistry, useClass: MockStreamServiceRegistry}
            ]
        });

        mockRegistry = TestBed.get(StreamServiceRegistry);
        httpMock = TestBed.get(HttpTestingController);

        baseWebService = TestBed.get(TestBaseWebService);
        spyOn(baseWebService, "onConnected");
        spyOn(baseWebService, "onDisconnected");

        // Initialize base web service
        baseWebService.onInit();
    });

    it("should create an instance", () => {
        expect(baseWebService).toBeDefined();
    });

    it("should forward the connected notification", () => {
        mockRegistry.connectedService.notifyConnected();
        expect(baseWebService.onConnected).toHaveBeenCalledTimes(1);
    });

    it("should forward the disconnected notification", () => {
        mockRegistry.connectedService.notifyDisconnected();
        expect(baseWebService.onDisconnected).toHaveBeenCalledTimes(1);
    });

    it("should forward the send request call", fakeAsync(() => {
        // Connect the services
        mockRegistry.connect();
        tick();

        baseWebService.sendRequest("/test").subscribe(DoNothing);
        httpMock.expectOne("/test").flush("done");
        baseWebService.sendRequest("/test/another").subscribe(DoNothing);
        httpMock.expectOne("/test/another").flush("done");
    }));
});
