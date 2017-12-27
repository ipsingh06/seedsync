import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";
import {HttpClient} from "@angular/common/http";

import * as Immutable from "immutable";

import {LoggerService} from "../common/logger.service";
import {BaseWebService, WebReaction} from "../common/base-web.service";
import {ServerStatusService} from "./server-status.service";
import {AutoQueuePattern, AutoQueuePatternJson} from "./autoqueue-pattern";
import {Localization} from "../common/localization";


/**
 * AutoQueueService provides the store for the autoqueue patterns
 */
@Injectable()
export class AutoQueueService extends BaseWebService {

    private readonly AUTOQUEUE_GET_URL = "/server/autoqueue/get";
    private readonly AUTOQUEUE_ADD_URL = (pattern) => `/server/autoqueue/add/${pattern}`;
    private readonly AUTOQUEUE_REMOVE_URL = (pattern) => `/server/autoqueue/remove/${pattern}`;

    private _patterns: BehaviorSubject<Immutable.List<AutoQueuePattern>> =
            new BehaviorSubject(Immutable.List([]));

    constructor(_statusService: ServerStatusService,
                _logger: LoggerService,
                _http: HttpClient) {
        super(_statusService, _logger, _http);
    }

    /**
     * Returns an observable that provides that latest patterns
     * @returns {Observable<Immutable.List<AutoQueuePattern>>}
     */
    get patterns(): Observable<Immutable.List<AutoQueuePattern>> {
        return this._patterns.asObservable();
    }

    private getPatterns() {
        this._logger.debug("Getting autoqueue patterns...");
        this.sendRequest(this.AUTOQUEUE_GET_URL).subscribe({
            next: reaction => {
                if (reaction.success) {
                    const parsed: AutoQueuePatternJson[] = JSON.parse(reaction.data);
                    const newPatterns: AutoQueuePattern[] = [];
                    for (const patternJson of parsed) {
                        newPatterns.push(new AutoQueuePattern({
                            pattern: patternJson.pattern
                        }));
                    }
                    this._patterns.next(Immutable.List(newPatterns));
                } else {
                    this._patterns.next(Immutable.List([]));
                }
            }
        });
    }

    /**
     * Add a pattern
     * @param {string} pattern
     * @returns {Observable<WebReaction>}
     */
    public add(pattern: string): Observable<WebReaction> {
        this._logger.debug("add pattern %O", pattern);

        // Value check
        if (pattern == null || pattern.trim().length == 0) {
            return Observable.create(observer => {
                observer.next(new WebReaction(false, null, Localization.Notification.AUTOQUEUE_PATTERN_EMPTY));
            });
        }

        const currentPatterns = this._patterns.getValue();
        const index = currentPatterns.findIndex(pat => pat.pattern == pattern);
        if (index >= 0) {
            return Observable.create(observer => {
                observer.next(new WebReaction(false, null, `Pattern '${pattern}' already exists.`));
            });
        } else {
            // Double-encode the value
            const patternEncoded = encodeURIComponent(encodeURIComponent(pattern));
            const url = this.AUTOQUEUE_ADD_URL(patternEncoded);
            const obs = this.sendRequest(url);
            obs.subscribe({
                next: reaction => {
                    if (reaction.success) {
                        // Update our copy and notify clients
                        const patterns = this._patterns.getValue();
                        const newPatterns = patterns.push(
                            new AutoQueuePattern({
                                pattern: pattern
                            })
                        );
                        this._patterns.next(newPatterns);
                    }
                }
            });
            return obs;
        }
    }

    /**
     * Remove a pattern
     * @param {string} pattern
     * @returns {Observable<WebReaction>}
     */
    public remove(pattern: string): Observable<WebReaction> {
        this._logger.debug("remove pattern %O", pattern);

        const currentPatterns = this._patterns.getValue();
        const index = currentPatterns.findIndex(pat => pat.pattern == pattern);
        if (index < 0) {
            return Observable.create(observer => {
                observer.next(new WebReaction(false, null, `Pattern '${pattern}' not found.`));
            });
        } else {
            // Double-encode the value
            const patternEncoded = encodeURIComponent(encodeURIComponent(pattern));
            const url = this.AUTOQUEUE_REMOVE_URL(patternEncoded);
            const obs = this.sendRequest(url);
            obs.subscribe({
                next: reaction => {
                    if (reaction.success) {
                        // Update our copy and notify clients
                        const patterns = this._patterns.getValue();
                        const finalIndex = currentPatterns.findIndex(pat => pat.pattern == pattern);
                        const newPatterns = patterns.remove(finalIndex);
                        this._patterns.next(newPatterns);
                    }
                }
            });
            return obs;
        }
    }

    protected onConnectedChanged(connected: boolean): void {
        if (connected) {
            // Retry the get
            this.getPatterns();
        } else {
            // Send empty list
            this._patterns.next(Immutable.List([]));
        }
    }
}

/**
 * AutoQueueService factory and provider
 */
export let autoQueueServiceFactory = (
    _statusService: ServerStatusService,
    _logger: LoggerService,
    _http: HttpClient) =>
{
  const autoQueueService = new AutoQueueService(_statusService, _logger, _http);
  autoQueueService.onInit();
  return autoQueueService;
};

export let AutoQueueServiceProvider = {
    provide: AutoQueueService,
    useFactory: autoQueueServiceFactory,
    deps: [ServerStatusService, LoggerService, HttpClient]
};
