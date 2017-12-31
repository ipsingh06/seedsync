import {Injectable, NgZone} from "@angular/core";
import {Observable} from "rxjs/Observable";

import {StreamServiceRegistry} from "./stream-service.registry";
import {RestService} from "../other/rest.service";
import {WebReaction} from "./base-stream.service";
import {ConnectedService} from "../other/connected.service";


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

    private _restService: RestService;
    private _connectedService: ConnectedService;

    constructor(_streamServiceProvider: StreamServiceRegistry) {
        this._restService = _streamServiceProvider.restService;
        this._connectedService = _streamServiceProvider.connectedService;
    }

    /**
     * Call this method to finish initialization
     */
    public onInit() {
        this._connectedService.connected.subscribe({
            next: connected => {
                if(connected) {
                    this.onConnected();
                } else {
                    this.onDisconnected();
                }
            }
        });
    }


    protected sendRequest(url: string): Observable<WebReaction> {
        return this._restService.sendRequest(url);
    }


    /**
     * Callback for connected
     */
    protected abstract onConnected(): void;

    /**
     * Callback for disconnected
     */
    protected abstract onDisconnected(): void;
}
