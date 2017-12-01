import {Injectable} from '@angular/core';
import {Observable} from "rxjs/Observable";
import {HttpClient} from "@angular/common/http";

import {BaseWebService, WebReaction} from "../common/base-web.service";
import {LoggerService} from "../common/logger.service";
import {ServerStatusService} from "./server-status.service";


/**
 * ServerCommandService handles sending commands to the backend server
 */
@Injectable()
export class ServerCommandService extends BaseWebService {
    private readonly RESTART_URL = "/server/command/restart";

    constructor(_statusService: ServerStatusService,
                _logger: LoggerService,
                _http: HttpClient) {
        super(_statusService, _logger, _http);
    }

    protected onConnectedChanged(connected: boolean): void {
        // Nothing to do
    }

    /**
     * Send a restart command to the server
     * @returns {Observable<WebReaction>}
     */
    public restart(): Observable<WebReaction> {
        return this.sendRequest(this.RESTART_URL);
    }
}

/**
 * ConfigService factory and provider
 */
export let serverCommandServiceFactory = (
    _statusService: ServerStatusService,
    _logger: LoggerService,
    _http: HttpClient) =>
{
  let serverCommandService = new ServerCommandService(_statusService, _logger, _http);
  serverCommandService.onInit();
  return serverCommandService;
};

export let ServerCommandServiceProvider = {
    provide: ServerCommandService,
    useFactory: serverCommandServiceFactory,
    deps: [ServerStatusService, LoggerService, HttpClient]
};
