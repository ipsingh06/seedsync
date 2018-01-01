import {TestBed} from "@angular/core/testing";

import {BaseWebService} from "../../../../services/base/base-web.service";
import {StreamServiceRegistry} from "../../../../services/base/stream-service.registry";
import {MockStreamServiceRegistry} from "../../../mocks/mock-stream-service.registry";
import {LoggerService} from "../../../../services/utils/logger.service";
import {ConnectedService} from "../../../../services/utils/connected.service";


// noinspection JSUnusedLocalSymbols
const DoNothing = {next: reaction => {}};


class TestBaseWebService extends BaseWebService {
    public onConnected(): void {}

    public onDisconnected(): void {}
}

describe("Testing base web service", () => {
    let baseWebService: TestBaseWebService;

    let mockRegistry: MockStreamServiceRegistry;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                TestBaseWebService,
                LoggerService,
                ConnectedService,
                {provide: StreamServiceRegistry, useClass: MockStreamServiceRegistry}
            ]
        });

        mockRegistry = TestBed.get(StreamServiceRegistry);

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
});
