import {Injectable, NgZone} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {HttpClient, HttpErrorResponse} from "@angular/common/http";

import {LoggerService} from "./logger.service";
import {Localization} from "./localization";


export class EventSourceFactory {
    static createEventSource(url: string) {
        return new EventSource(url);
    }
}


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
export abstract class BaseStreamService {

    private readonly STREAM_RETRY_INTERVAL_MS = 3000;

    private _streamUrl: string;
    private _eventNames: string[] = [];
    private _connected: boolean = false;

    constructor(protected _logger: LoggerService,
                private _http: HttpClient,
                private _zone: NgZone) {
    }

    protected set streamUrl(url: string) {
        this._streamUrl = url;
    }

    protected registerEvent(eventName: string) {
        this._eventNames.push(eventName);
    }

    /**
     * Call this method to finish initialization
     */
    public onInit() {
        this.createSseObserver();
    }

    private createSseObserver() {
        const observable = Observable.create(observer => {
            const eventSource = EventSourceFactory.createEventSource(this._streamUrl);
            for(let eventName of this._eventNames) {
                eventSource.addEventListener(eventName, event => observer.next(
                    {
                        "event": eventName,
                        "data": event.data
                    }
                ));
            }

            eventSource.onerror = x => this._zone.run(() => observer.error(x));

            return () => {
                eventSource.close();
            };
        });
        observable.subscribe({
            next: (x) => {
                // TODO: move to onopen
                this._connected = true;
                this.onEvent(x["event"], x["data"])
            },
            error: err => {
                this._connected = false;
                this.onError(err);
                setTimeout(() => {this.createSseObserver(); }, this.STREAM_RETRY_INTERVAL_MS);
            }
        });
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
                this._logger.debug("%s failed: not connected to server", url);
                observer.next(new WebReaction(false, null, Localization.Error.SERVER_DISCONNECTED));
            }
        }).shareReplay(1);
        // shareReplay is needed to:
        //      prevent duplicate http requests
        //      share result with those that subscribe after the value was published
        // More info: https://blog.thoughtram.io/angular/2016/06/16/cold-vs-hot-observables.html
    }

    /**
     * Callback for a new event
     * @param {string} eventName
     * @param {string} data
     */
    protected abstract onEvent(eventName: string, data: string);

    /**
     * Callback for error
     * @param err
     */
    protected abstract onError(err);
}
