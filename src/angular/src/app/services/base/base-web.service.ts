import {Injectable} from "@angular/core";

import {StreamServiceRegistry} from "./stream-service.registry";
import {ConnectedService} from "../utils/connected.service";


/**
 * BaseWebService provides utility to be notified when connection to
 * the backend server is lost and regained. Non-streaming web services
 * can use these notifications to re-issue get requests.
 */
@Injectable()
export abstract class BaseWebService {

    private _connectedService: ConnectedService;

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

    constructor(_streamServiceProvider: StreamServiceRegistry) {
        this._connectedService = _streamServiceProvider.connectedService;
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
