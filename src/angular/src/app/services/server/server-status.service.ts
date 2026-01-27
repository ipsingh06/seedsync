import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';

import { Localization } from '../../common/localization';
import { ServerStatus, ServerStatusJson } from './server-status';
import { BaseStreamService } from '../base/base-stream.service';

@Injectable({
    providedIn: 'root'
})
export class ServerStatusService extends BaseStreamService {
    private statusSubject = new BehaviorSubject<ServerStatus>(
        new ServerStatus({
            server: {
                up: false,
                errorMessage: Localization.Notification.STATUS_CONNECTION_WAITING
            },
            controller: {
                latestLocalScanTime: null,
                latestRemoteScanTime: null,
                latestRemoteScanFailed: false,
                latestRemoteScanError: null
            }
        })
    );

    constructor() {
        super();
        this.registerEventName('status');
    }

    get status(): Observable<ServerStatus> {
        return this.statusSubject.asObservable();
    }

    protected onEvent(_eventName: string, data: string): void {
        this.parseStatus(data);
    }

    protected onConnected(): void {
        // nothing to do
    }

    protected onDisconnected(): void {
        // Notify the clients
        this.statusSubject.next(new ServerStatus({
            server: {
                up: false,
                errorMessage: Localization.Error.SERVER_DISCONNECTED
            },
            controller: {
                latestLocalScanTime: null,
                latestRemoteScanTime: null,
                latestRemoteScanFailed: false,
                latestRemoteScanError: null
            }
        }));
    }

    /**
     * Parse an event and notify subscribers
     */
    private parseStatus(data: string): void {
        const statusJson: ServerStatusJson = JSON.parse(data);
        const status = ServerStatus.fromJson(statusJson);
        this.statusSubject.next(status);
    }
}
