import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {Observable} from "rxjs/Observable";

import {LoggerService} from "../common/logger.service";
import {BaseStreamService, WebReaction} from "../common/base-stream.service";


/**
 * RestService exposes the HTTP REST API to clients
 */
@Injectable()
export class RestService extends BaseStreamService {

    constructor(_logger: LoggerService,
                _http: HttpClient) {
        super(_logger, _http);
        // No events to register
    }

    public sendRequest(url: string): Observable<WebReaction> {
        return super.sendRequest(url);
    }

    protected onEvent(eventName: string, data: string) {
        // Nothing to do
    }

    protected onConnected() {
        // Nothing to do
    }

    protected onDisconnected() {
        // Nothing to do
    }
}
