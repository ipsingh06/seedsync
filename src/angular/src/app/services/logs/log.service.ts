import { Injectable } from '@angular/core';
import { Observable, ReplaySubject } from 'rxjs';

import { BaseStreamService } from '../base/base-stream.service';
import { LogRecord, LogRecordJson } from './log-record';

@Injectable({
    providedIn: 'root'
})
export class LogService extends BaseStreamService {
    private logsSubject = new ReplaySubject<LogRecord>();

    constructor() {
        super();
        this.registerEventName('log-record');
    }

    /**
     * Logs is a hot observable (i.e. no caching)
     */
    get logs(): Observable<LogRecord> {
        return this.logsSubject.asObservable();
    }

    protected onEvent(_eventName: string, data: string): void {
        const json: LogRecordJson = JSON.parse(data);
        this.logsSubject.next(LogRecord.fromJson(json));
    }

    protected onConnected(): void {
        // nothing to do
    }

    protected onDisconnected(): void {
        // nothing to do
    }
}
