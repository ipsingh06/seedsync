import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {HttpClient, HttpErrorResponse} from "@angular/common/http";

import {LoggerService} from "./logger.service";
import {Localization} from "./localization";
import {IStreamService} from "./stream-service.registry";


/**
 * WebReaction encapsulates the response for an action
 * executed on a BaseWebService
 */
export class WebReaction {
    readonly success: boolean;
    readonly data: string;
    readonly errorMessage: string;

    constructor(success: boolean, data: string, errorMessage: string) {
        this.success = success;
        this.data = data;
        this.errorMessage = errorMessage;
    }
}


@Injectable()
export abstract class BaseStreamService implements IStreamService {

    private _eventNames: string[] = [];
    private _connected = false;


    constructor(protected _logger: LoggerService,
                private _http: HttpClient) {
    }

    getEventNames(): string[] {
        return this._eventNames;
    }

    notifyConnected() {
        this._connected = true;
        this.onConnected();
    }

    notifyDisconnected() {
        this._connected = false;
        this.onDisconnected();
    }

    notifyEvent(eventName: string, data: string) {
        this.onEvent(eventName, data);
    }

    /**
     * Helper method to send backend a request and generate a WebReaction response
     * @param {string} url
     * @returns {Observable<WebReaction>}
     */
    protected sendRequest(url: string): Observable<WebReaction> {
        return Observable.create(observer => {
            if (this._connected) {
                // We are connected to server, send the request
                this._http.get(url, {responseType: "text"})
                    .subscribe(
                    data => {
                        this._logger.debug("%s http response: %s", url, data);
                        observer.next(new WebReaction(true, data, null));
                    },
                    (err: HttpErrorResponse) => {
                        let errorMessage = null;
                        this._logger.debug("%s error: %O", url, err);
                        if (err.error instanceof Event) {
                            errorMessage = err.error.type;
                        } else {
                            errorMessage = err.error;
                        }
                        observer.next(new WebReaction(false, null, errorMessage));
                    }
                );
            } else {
                // We are NOT connected, don't bother sending a request
                this._logger.error("%s failed: not connected to server", url);
                observer.next(new WebReaction(false, null, Localization.Error.SERVER_DISCONNECTED));
            }
        }).shareReplay(1);
        // shareReplay is needed to:
        //      prevent duplicate http requests
        //      share result with those that subscribe after the value was published
        // More info: https://blog.thoughtram.io/angular/2016/06/16/cold-vs-hot-observables.html
    }

    protected registerEventName(eventName: string) {
        this._eventNames.push(eventName);
    }

    /**
     * Callback for a new event
     * @param {string} eventName
     * @param {string} data
     */
    protected abstract onEvent(eventName: string, data: string);

    /**
     * Callback for connected
     */
    protected abstract onConnected();

    /**
     * Callback for disconnected
     */
    protected abstract onDisconnected();
}
