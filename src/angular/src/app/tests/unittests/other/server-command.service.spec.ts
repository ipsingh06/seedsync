import {fakeAsync, TestBed, tick} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";

import {LoggerService} from "../../../common/logger.service";
import {ServerCommandService} from "../../../other/server-command.service";
import {EventSourceFactory} from "../../../common/base-stream.service";
import {createMockEventSource, MockEventSource} from "../../mocks/common/mock-event-source.ts";


describe("Testing server command service", () => {
    let httpMock: HttpTestingController;
    let commandService: ServerCommandService;

    let mockEventSource: MockEventSource;

    beforeEach(fakeAsync(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                LoggerService,
                ServerCommandService,
            ]
        });

        spyOn(EventSourceFactory, 'createEventSource').and.callFake(
            (url: string) => {
                mockEventSource = createMockEventSource(url);
                return mockEventSource;
            }
        );

        httpMock = TestBed.get(HttpTestingController);
        commandService = TestBed.get(ServerCommandService);

        // Finish test config init
        commandService.onInit();

        // Connect the service
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
    }));

    it("should create an instance", () => {
        expect(commandService).toBeDefined();
    });


    it("should send a GET restart command", () => {
        let count = 0;
        commandService.restart().subscribe({
           next: reaction => {
               count++;
               expect(reaction.success).toBe(true);
           }
        });

        // set request
        httpMock.expectOne("/server/command/restart").flush("{}");

        expect(count).toBe(1);
        httpMock.verify();
    });
});
