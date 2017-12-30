import {Injectable, NgZone} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";
import {HttpClient} from "@angular/common/http";

import {LoggerService} from "../common/logger.service";
import {Localization} from "../common/localization";
import {ServerStatus, ServerStatusJson} from "./server-status";
import {BaseStreamService} from "../common/base-stream.service";


@Injectable()
export class ServerStatusService extends BaseStreamService {

    private readonly STATUS_STREAM_URL = "/server/status-stream";

    private _status: BehaviorSubject<ServerStatus> =
        new BehaviorSubject(new ServerStatus({
            server: {
                up: false
            }
        }));

    constructor(_logger: LoggerService,
                _http: HttpClient,
                _zone: NgZone) {
        super(_logger, _http, _zone);

        this.streamUrl = this.STATUS_STREAM_URL;

        super.registerEvent("status");
    }

    protected onEvent(eventName: string, data: string) {
        this.parseStatus(data);
    }

    protected onError(err: any) {
        // Log the error
        this._logger.error("Error in status stream: %O", err);

        // Notify the clients
        this._status.next(new ServerStatus({
            server: {
                up: false,
                errorMessage: Localization.Error.SERVER_DISCONNECTED
            }
        }));
    }

    /**
     * Parse an event and notify subscribers
     * @param {string} data
     */
    private parseStatus(data: string) {
        const statusJson: ServerStatusJson = JSON.parse(data);
        const status = new ServerStatus({
            server: {
                up: statusJson.server.up,
                errorMessage: statusJson.server.error_msg
            }
        });
        this._status.next(status);
    }

    get status(): Observable<ServerStatus> {
        return this._status.asObservable();
    }
}

/**
 * ServerStatusService factory and provider
 */
export let serverStatusServiceFactory = (
        _logger: LoggerService,
        _http: HttpClient,
        _zone: NgZone) => {
    const serverStatusService = new ServerStatusService(_logger, _http, _zone);
    serverStatusService.onInit();
    return serverStatusService;
};

// noinspection JSUnusedGlobalSymbols
export let ServerStatusServiceProvider = {
    provide: ServerStatusService,
    useFactory: serverStatusServiceFactory,
    deps: [LoggerService, HttpClient, NgZone]
};
