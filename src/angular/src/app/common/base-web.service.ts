import {Injectable} from "@angular/core";
import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import {Observable} from "rxjs/Observable";

import {ServerStatusService} from "../other/server-status.service";
import {LoggerService} from "./logger.service";
import {Localization} from "./localization";

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


/**
 * BaseWebService provides utility to be notified when connection to
 * the backend server is lost and regained. Non-streaming web services
 * can use these notifications to re-issue get requests.
 *
 * The service starts off assuming there is no connection. The
 * onConnectionChanged() will always be called quickly if there
 * is a connection.
 */
@Injectable()
export abstract class BaseWebService {

    private _connected: boolean;

    constructor(private _statusService: ServerStatusService,
                protected _logger: LoggerService,
                private _http: HttpClient) {
        // We start off assuming we are not connected
        this._connected = false;
    }

    /**
     * Call this method to finish initialization
     */
    public onInit() {
        this._statusService.status.subscribe({
            next: status => {
                // Change the status BEFORE notifying derived class so that if
                // it calls any methods on us, we have the latest state
                const prevConnected = this._connected;
                this._connected = status.connected;

                if (prevConnected !== status.connected) {
                    // Connection status changed
                    this.onConnectedChanged(status.connected);
                }
            }
        });
    }

    /**
     * Indicates a change in connection status
     * @param {boolean} connected   New status
     */
    protected abstract onConnectedChanged(connected: boolean): void;


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
                this._logger.debug("%s failed: not connected to server", url);
                observer.next(new WebReaction(false, null, Localization.Error.SERVER_DISCONNECTED));
            }
        }).shareReplay(1);
        // shareReplay is needed to:
        //      prevent duplicate http requests
        //      share result with those that subscribe after the value was published
        // More info: https://blog.thoughtram.io/angular/2016/06/16/cold-vs-hot-observables.html
    }
}
