import {Injectable, NgZone} from "@angular/core";
import {HttpClient} from "@angular/common/http";

import {LoggerService} from "./logger.service";
import {BaseStreamService} from "./base-stream.service";


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

    private _streamConnected: boolean;

    constructor(_logger: LoggerService,
                _http: HttpClient,
                _zone: NgZone) {
        super(_logger, _http, _zone);

        // We start off assuming we are not connected
        this._streamConnected = false;

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
        if(!this._streamConnected) {
            // Change the status BEFORE notifying derived class so that if
            // it calls any methods on us, we have the latest state
            this._streamConnected = true;
            this.onConnectedChanged(this._streamConnected);
        }
    }

    protected onError(err: any) {
        if(this._streamConnected) {
            // Change the status BEFORE notifying derived class so that if
            // it calls any methods on us, we have the latest state
            this._streamConnected = false;
            this.onConnectedChanged(this._streamConnected);
        }
    }

    /**
     * Indicates a change in connection status
     * @param {boolean} connected   New status
     */
    protected abstract onConnectedChanged(connected: boolean): void;
}
