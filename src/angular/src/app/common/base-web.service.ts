import {Injectable, NgZone} from "@angular/core";
import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import {Observable} from "rxjs/Observable";

import {LoggerService} from "./logger.service";
import {Localization} from "./localization";
import {BaseStreamService} from "./base-stream.service";

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
export abstract class BaseWebService extends BaseStreamService {

    // Use this stream to check for connection status
    private readonly STATUS_STREAM_URL = "/server/status-stream";

    private _connected: boolean;

    constructor(protected _logger: LoggerService,
                private _http: HttpClient,
                _zone: NgZone) {
        super(_zone);

        // We start off assuming we are not connected
        this._connected = false;

        this.streamUrl = this.STATUS_STREAM_URL;
        super.registerEvent("status");
    }

    /**
     * Call this method to finish initialization
     */
    public onInit() {
        super.onInit();
    }


    protected onEvent(eventName: string, data: string) {
        if(!this._connected) {
            // Change the status BEFORE notifying derived class so that if
            // it calls any methods on us, we have the latest state
            this._connected = true;
            this.onConnectedChanged(this._connected);
        }
    }

    protected onError(err: any) {
        if(this._connected) {
            // Change the status BEFORE notifying derived class so that if
            // it calls any methods on us, we have the latest state
            this._connected = false;
            this.onConnectedChanged(this._connected);
        }
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
