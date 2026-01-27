import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";

import {BaseWebService} from "../base/base-web.service";
import {StreamServiceRegistry} from "../base/stream-service.registry";
import {RestService, WebReaction} from "../utils/rest.service";


/**
 * ServerCommandService handles sending commands to the backend server
 */
@Injectable()
export class ServerCommandService extends BaseWebService {
    private readonly RESTART_URL = "/server/command/restart";

    constructor(_streamServiceProvider: StreamServiceRegistry,
                private _restService: RestService) {
        super(_streamServiceProvider);
    }

    /**
     * Send a restart command to the server
     * @returns {Observable<WebReaction>}
     */
    public restart(): Observable<WebReaction> {
        return this._restService.sendRequest(this.RESTART_URL);
    }

    protected onConnected() {
        // Nothing to do
    }

    protected onDisconnected() {
        // Nothing to do
    }
}

/**
 * ConfigService factory and provider
 */
export let serverCommandServiceFactory = (
    _streamServiceRegistry: StreamServiceRegistry,
    _restService: RestService
) => {
  const serverCommandService = new ServerCommandService(_streamServiceRegistry, _restService);
  serverCommandService.onInit();
  return serverCommandService;
};

// noinspection JSUnusedGlobalSymbols
export let ServerCommandServiceProvider = {
    provide: ServerCommandService,
    useFactory: serverCommandServiceFactory,
    deps: [StreamServiceRegistry, RestService]
};
