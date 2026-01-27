import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, shareReplay, of, map, catchError } from 'rxjs';

import { LoggerService } from './logger.service';

/**
 * WebReaction encapsulates the response for an action
 * executed on a BaseWebService
 */
export class WebReaction {
    constructor(
        public readonly success: boolean,
        public readonly data: string | null,
        public readonly errorMessage: string | null
    ) {}
}

/**
 * RestService exposes the HTTP REST API to clients
 */
@Injectable({
    providedIn: 'root'
})
export class RestService {
    constructor(
        private logger: LoggerService,
        private http: HttpClient
    ) {}

    /**
     * Send backend a request and generate a WebReaction response
     */
    public sendRequest(url: string): Observable<WebReaction> {
        return this.http.get(url, { responseType: 'text' }).pipe(
            map(data => {
                this.logger.debug('%s http response: %s', url, data);
                return new WebReaction(true, data, null);
            }),
            catchError((err: HttpErrorResponse) => {
                let errorMessage: string;
                this.logger.debug('%s error: %O', url, err);
                if (err.error instanceof Event) {
                    errorMessage = err.error.type;
                } else {
                    errorMessage = err.error;
                }
                return of(new WebReaction(false, null, errorMessage));
            }),
            // shareReplay is needed to:
            //      prevent duplicate http requests
            //      share result with those that subscribe after the value was published
            shareReplay(1)
        );
    }
}
