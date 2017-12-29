import {Injectable, NgZone} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {HttpClient} from "@angular/common/http";

import {BaseWebService, WebReaction} from "../common/base-web.service";
import {LoggerService} from "../common/logger.service";


/**
 * ServerCommandService handles sending commands to the backend server
 */
@Injectable()
export class ServerCommandService extends BaseWebService {
    private readonly RESTART_URL = "/server/command/restart";

    constructor(_logger: LoggerService,
                _http: HttpClient,
                _zone: NgZone) {
        super(_logger, _http, _zone);
    }

    // noinspection JSUnusedLocalSymbols
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
    _logger: LoggerService,
    _http: HttpClient,
    _zone: NgZone) => {
  const serverCommandService = new ServerCommandService(_logger, _http, _zone);
  serverCommandService.onInit();
  return serverCommandService;
};

// noinspection JSUnusedGlobalSymbols
export let ServerCommandServiceProvider = {
    provide: ServerCommandService,
    useFactory: serverCommandServiceFactory,
    deps: [LoggerService, HttpClient, NgZone]
};
