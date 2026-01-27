import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';

export enum LogLevel {
    ERROR = 0,
    WARN = 1,
    INFO = 2,
    DEBUG = 3
}

@Injectable({
    providedIn: 'root'
})
export class LoggerService {
    public level: LogLevel;

    constructor() {
        this.level = environment.logger.level as LogLevel;
    }

    get debug(): (...args: unknown[]) => void {
        if (this.level >= LogLevel.DEBUG) {
            return console.debug.bind(console);
        }
        return () => { /* noop */ };
    }

    get info(): (...args: unknown[]) => void {
        if (this.level >= LogLevel.INFO) {
            return console.log.bind(console);
        }
        return () => { /* noop */ };
    }

    get warn(): (...args: unknown[]) => void {
        if (this.level >= LogLevel.WARN) {
            return console.warn.bind(console);
        }
        return () => { /* noop */ };
    }

    get error(): (...args: unknown[]) => void {
        if (this.level >= LogLevel.ERROR) {
            return console.error.bind(console);
        }
        return () => { /* noop */ };
    }
}
