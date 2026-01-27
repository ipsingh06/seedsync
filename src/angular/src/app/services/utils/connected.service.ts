import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';

import { BaseStreamService } from '../base/base-stream.service';

/**
 * ConnectedService exposes the connection status to clients
 * as an Observable
 */
@Injectable({
    providedIn: 'root'
})
export class ConnectedService extends BaseStreamService {
    private connectedSubject = new BehaviorSubject<boolean>(false);

    constructor() {
        super();
        // No events to register
    }

    get connected(): Observable<boolean> {
        return this.connectedSubject.asObservable();
    }

    protected onEvent(_eventName: string, _data: string): void {
        // Nothing to do
    }

    protected onConnected(): void {
        if (this.connectedSubject.getValue() === false) {
            this.connectedSubject.next(true);
        }
    }

    protected onDisconnected(): void {
        if (this.connectedSubject.getValue() === true) {
            this.connectedSubject.next(false);
        }
    }
}
