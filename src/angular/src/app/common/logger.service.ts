import {Injectable} from '@angular/core';

@Injectable()
export class LoggerService {

    public level: LoggerService.Level;

    constructor() {
        this.level = LoggerService.Level.DEBUG;
    }

    get debug() {
        if(this.level >= LoggerService.Level.DEBUG) {
            return console.debug.bind(console);
        } else {
            return () => {};
        }
    }

    get info() {
        if(this.level >= LoggerService.Level.INFO) {
            return console.log.bind(console);
        } else {
            return () => {};
        }
    }

    get warn() {
        if(this.level >= LoggerService.Level.WARN) {
            return console.warn.bind(console);
        } else {
            return () => {};
        }
    }

    get error() {
        if(this.level >= LoggerService.Level.ERROR) {
            return console.error.bind(console);
        } else {
            return () => {};
        }
    }
}

export module LoggerService {
    export enum Level {
        ERROR,
        WARN,
        INFO,
        DEBUG,
    }
}
