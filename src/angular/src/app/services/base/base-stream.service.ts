import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";

import {LoggerService} from "../utils/logger.service";
import {IStreamService} from "./stream-service.registry";
import {RestService} from "../utils/rest.service";


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
