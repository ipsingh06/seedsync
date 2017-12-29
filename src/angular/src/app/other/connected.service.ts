import {Injectable, NgZone} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";
import {HttpClient} from "@angular/common/http";

import {LoggerService} from "../common/logger.service";
import {BaseWebService} from "../common/base-web.service";


/**
 * ConnectedService exposes the connection status to clients
 * as an Observable
 */
@Injectable()
export class ConnectedService extends BaseWebService {

    // For clients
    private _connectedSubject: BehaviorSubject<boolean> = new BehaviorSubject(false);

    constructor(_logger: LoggerService,
                _http: HttpClient,
                _zone: NgZone) {
        super(_logger, _http, _zone);
    }

    protected onConnectedChanged(connected: boolean): void {
        this._connectedSubject.next(connected);
    }

    get connected(): Observable<boolean> {
        return this._connectedSubject.asObservable();
    }
}

/**
 * ConnectedService factory and provider
 */
export let connectedServiceFactory = (
    _logger: LoggerService,
    _http: HttpClient,
    _zone: NgZone) => {
  const connectedService = new ConnectedService(_logger, _http, _zone);
  connectedService.onInit();
  return connectedService;
};

// noinspection JSUnusedGlobalSymbols
export let ConnectedServiceProvider = {
    provide: ConnectedService,
    useFactory: connectedServiceFactory,
    deps: [LoggerService, HttpClient, NgZone]
};
