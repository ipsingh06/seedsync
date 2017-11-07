import {Injectable} from '@angular/core';
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";
import {HttpClient, HttpErrorResponse} from '@angular/common/http';

import {LoggerService} from "../common/logger.service";
import {SseUtil} from "../common/sse.util";

/**
 * ServerStatus
 */
export class ServerStatus {
    readonly up: boolean;
    readonly errorMessage: string;

    constructor(up: boolean, errorMessage: string) {
        this.up = up;
        this.errorMessage = errorMessage;
    }
}
/**
 * ServerStatus as serialized by the backend.
 * Note: naming convention matches that used in JSON
 */
interface ServerStatusJson {
    up: boolean;
    error_msg: string;
}


@Injectable()
export class ServerStatusService {

    private readonly STATUS_STREAM_URL = "/server/status-stream";

    private _status: BehaviorSubject<ServerStatus> =
        new BehaviorSubject(new ServerStatus(true, null));

    constructor(private _logger: LoggerService,
                private _http: HttpClient) {
        this.init();
    }

    private init() {
        // Add a EventSource observable to receive file list and updates
        // from the backend
        // Observable-SSE code from https://stackoverflow.com/a/36827897/8571324
        let _serverStatusService = this;

        const observable = Observable.create(observer => {
            const eventSource = new EventSource(this.STATUS_STREAM_URL);
            SseUtil.addSseListener("status", eventSource, observer);

            eventSource.onerror = x => observer.error(x);

            return () => {
                eventSource.close();
            };
        });
        observable.subscribe({
            next: (x) => _serverStatusService.parseStatus(x["data"]),
            error: err => this._logger.error("SSE Error: " + err)
        });
    }

    /**
     * Parse an event and notify subscribers
     * @param {string} data
     */
    private parseStatus(data: string) {
        let statusJson: ServerStatusJson = JSON.parse(data);
        let status = new ServerStatus(statusJson.up, statusJson.error_msg);
        this._status.next(status);
    }

    get status() : Observable<ServerStatus> {
        return this._status.asObservable();
    }
}
