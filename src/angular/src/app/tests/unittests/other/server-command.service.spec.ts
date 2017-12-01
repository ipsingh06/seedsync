import {fakeAsync, TestBed} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';
import {Subject} from "rxjs/Subject";

import {LoggerService} from "../../../common/logger.service";
import {ServerStatus} from "../../../other/server-status";
import {ServerStatusService} from "../../../other/server-status.service";
import {ServerCommandService} from "../../../other/server-command.service";

class ServerStatusServiceStub {
    status: Subject<ServerStatus> = new Subject();
}



describe('Testing server command service', () => {
    let httpMock: HttpTestingController;
    let statusService: ServerStatusServiceStub;
    let commandService: ServerCommandService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                LoggerService,
                ServerCommandService,
                {provide: ServerStatusService, useClass: ServerStatusServiceStub},
            ]
        });

        httpMock = TestBed.get(HttpTestingController);
        commandService = TestBed.get(ServerCommandService);
        statusService = TestBed.get(ServerStatusService);

        // Finish test config init
        commandService.onInit();

        // Connect the service
        statusService.status.next(new ServerStatus({connected: true}));
    });

    it('should create an instance', () => {
        expect(commandService).toBeDefined();
    });


    it('should send a GET restart command', () => {
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
