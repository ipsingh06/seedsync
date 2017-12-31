import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";

import {BaseWebService} from "../common/base-web.service";
import {WebReaction} from "../common/base-stream.service";
import {StreamServiceRegistry} from "../common/stream-service.registry";


/**
 * ServerCommandService handles sending commands to the backend server
 */
@Injectable()
export class ServerCommandService extends BaseWebService {
    private readonly RESTART_URL = "/server/command/restart";

    constructor(_streamServiceProvider: StreamServiceRegistry) {
        super(_streamServiceProvider);
    }

    /**
     * Send a restart command to the server
     * @returns {Observable<WebReaction>}
     */
    public restart(): Observable<WebReaction> {
        return this.sendRequest(this.RESTART_URL);
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
    _streamServiceRegistry: StreamServiceRegistry
) => {
  const serverCommandService = new ServerCommandService(_streamServiceRegistry);
  serverCommandService.onInit();
  return serverCommandService;
};

// noinspection JSUnusedGlobalSymbols
export let ServerCommandServiceProvider = {
    provide: ServerCommandService,
    useFactory: serverCommandServiceFactory,
    deps: [StreamServiceRegistry]
};
