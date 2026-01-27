import { Injectable, inject } from '@angular/core';
import { Observable, BehaviorSubject, of } from 'rxjs';

import { LoggerService } from '../utils/logger.service';
import { BaseWebService } from '../base/base-web.service';
import { AutoQueuePattern, AutoQueuePatternJson } from './autoqueue-pattern';
import { Localization } from '../../common/localization';
import { RestService, WebReaction } from '../utils/rest.service';

/**
 * AutoQueueService provides the store for the autoqueue patterns
 */
@Injectable({
    providedIn: 'root'
})
export class AutoQueueService extends BaseWebService {
    private readonly AUTOQUEUE_GET_URL = '/server/autoqueue/get';
    private readonly AUTOQUEUE_ADD_URL = (pattern: string) => `/server/autoqueue/add/${pattern}`;
    private readonly AUTOQUEUE_REMOVE_URL = (pattern: string) => `/server/autoqueue/remove/${pattern}`;

    private patternsSubject = new BehaviorSubject<readonly AutoQueuePattern[]>([]);

    private restService = inject(RestService);
    private logger = inject(LoggerService);

    /**
     * Returns an observable that provides that latest patterns
     */
    get patterns(): Observable<readonly AutoQueuePattern[]> {
        return this.patternsSubject.asObservable();
    }

    /**
     * Add a pattern
     */
    public add(pattern: string): Observable<WebReaction> {
        this.logger.debug('add pattern %O', pattern);

        // Value check
        if (pattern == null || pattern.trim().length === 0) {
            return of(new WebReaction(false, null, Localization.Notification.AUTOQUEUE_PATTERN_EMPTY));
        }

        const currentPatterns = this.patternsSubject.getValue();
        const index = currentPatterns.findIndex(pat => pat.pattern === pattern);
        if (index >= 0) {
            return of(new WebReaction(false, null, `Pattern '${pattern}' already exists.`));
        }

        // Double-encode the value
        const patternEncoded = encodeURIComponent(encodeURIComponent(pattern));
        const url = this.AUTOQUEUE_ADD_URL(patternEncoded);
        const obs = this.restService.sendRequest(url);

        obs.subscribe({
            next: reaction => {
                if (reaction.success) {
                    // Update our copy and notify clients
                    const patterns = this.patternsSubject.getValue();
                    const newPatterns = [...patterns, new AutoQueuePattern({ pattern })];
                    this.patternsSubject.next(Object.freeze(newPatterns));
                }
            }
        });

        return obs;
    }

    /**
     * Remove a pattern
     */
    public remove(pattern: string): Observable<WebReaction> {
        this.logger.debug('remove pattern %O', pattern);

        const currentPatterns = this.patternsSubject.getValue();
        const index = currentPatterns.findIndex(pat => pat.pattern === pattern);
        if (index < 0) {
            return of(new WebReaction(false, null, `Pattern '${pattern}' not found.`));
        }

        // Double-encode the value
        const patternEncoded = encodeURIComponent(encodeURIComponent(pattern));
        const url = this.AUTOQUEUE_REMOVE_URL(patternEncoded);
        const obs = this.restService.sendRequest(url);

        obs.subscribe({
            next: reaction => {
                if (reaction.success) {
                    // Update our copy and notify clients
                    const patterns = this.patternsSubject.getValue();
                    const finalIndex = patterns.findIndex(pat => pat.pattern === pattern);
                    const newPatterns = [
                        ...patterns.slice(0, finalIndex),
                        ...patterns.slice(finalIndex + 1)
                    ];
                    this.patternsSubject.next(Object.freeze(newPatterns));
                }
            }
        });

        return obs;
    }

    protected onConnected(): void {
        // Retry the get
        this.getPatterns();
    }

    protected onDisconnected(): void {
        // Send empty list
        this.patternsSubject.next([]);
    }

    private getPatterns(): void {
        this.logger.debug('Getting autoqueue patterns...');
        this.restService.sendRequest(this.AUTOQUEUE_GET_URL).subscribe({
            next: reaction => {
                if (reaction.success && reaction.data) {
                    const parsed: AutoQueuePatternJson[] = JSON.parse(reaction.data);
                    const newPatterns = parsed.map(
                        patternJson => new AutoQueuePattern({ pattern: patternJson.pattern })
                    );
                    this.patternsSubject.next(Object.freeze(newPatterns));
                } else {
                    this.patternsSubject.next([]);
                }
            }
        });
    }
}
