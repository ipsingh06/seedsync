import {Injectable, NgZone} from "@angular/core";
import {Observable} from "rxjs/Observable";


export class EventSourceFactory {
    static createEventSource(url: string) {
        return new EventSource(url);
    }
}


@Injectable()
export abstract class BaseStreamService {

    private readonly STREAM_RETRY_INTERVAL_MS = 3000;

    private _streamUrl: string;
    private _eventNames: string[] = [];

    constructor(private _zone: NgZone) {
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
            next: (x) => this.onEvent(x["event"], x["data"]),
            error: err => {
                this.onError(err);
                setTimeout(() => {this.createSseObserver(); }, this.STREAM_RETRY_INTERVAL_MS);
            }
        });
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
