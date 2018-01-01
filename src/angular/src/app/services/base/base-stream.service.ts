import {Injectable} from "@angular/core";

import {IStreamService} from "./stream-service.registry";


/**
 * BaseStreamService represents a web services that fetches data
 * from a SSE stream. This class provides utilities to register
 * for event notifications from a multiplexed stream.
 *
 * Note: services derived from this class SHOULD NOT be created
 *       directly. They need to be added to StreamServiceRegistry
 *       and fetched from an instance of that registry class.
 */
@Injectable()
export abstract class BaseStreamService implements IStreamService {

    private _eventNames: string[] = [];


    constructor() {}

    getEventNames(): string[] {
        return this._eventNames;
    }

    notifyConnected() {
        this.onConnected();
    }

    notifyDisconnected() {
        this.onDisconnected();
    }

    notifyEvent(eventName: string, data: string) {
        this.onEvent(eventName, data);
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
