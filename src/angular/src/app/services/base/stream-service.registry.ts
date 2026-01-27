import { Injectable, NgZone, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ModelFileService } from '../files/model-file.service';
import { ServerStatusService } from '../server/server-status.service';
import { LoggerService } from '../utils/logger.service';
import { ConnectedService } from '../utils/connected.service';
import { LogService } from '../logs/log.service';

export interface IStreamService {
    /**
     * Returns the event names supported by this stream service
     */
    getEventNames(): string[];

    /**
     * Notifies the stream service that it is now connected
     */
    notifyConnected(): void;

    /**
     * Notifies the stream service that it is now disconnected
     */
    notifyDisconnected(): void;

    /**
     * Notifies the stream service of an event
     */
    notifyEvent(eventName: string, data: string): void;
}

/**
 * StreamDispatchService is the top-level service that connects to
 * the multiplexed SSE stream. It listens for SSE events and dispatches
 * them to whichever IStreamService that requested them.
 */
@Injectable({
    providedIn: 'root'
})
export class StreamDispatchService {
    private readonly STREAM_URL = '/server/stream';
    private readonly STREAM_RETRY_INTERVAL_MS = 3000;

    private eventNameToServiceMap = new Map<string, IStreamService>();
    private services: IStreamService[] = [];

    private logger = inject(LoggerService);
    private zone = inject(NgZone);

    /**
     * Call this method to finish initialization
     */
    public onInit(): void {
        this.createSseObserver();
    }

    /**
     * Register an IStreamService with the dispatch
     */
    public registerService(service: IStreamService): IStreamService {
        for (const eventName of service.getEventNames()) {
            this.eventNameToServiceMap.set(eventName, service);
        }
        this.services.push(service);
        return service;
    }

    private createSseObserver(): void {
        const observable = new Observable<{ event: string; data: string }>(observer => {
            const eventSource = new EventSource(this.STREAM_URL);

            for (const eventName of Array.from(this.eventNameToServiceMap.keys())) {
                eventSource.addEventListener(eventName, event => observer.next({
                    event: eventName,
                    data: (event as MessageEvent).data
                }));
            }

            eventSource.onopen = () => {
                this.logger.info('Connected to server stream');

                // Notify all services of connection
                for (const service of this.services) {
                    this.zone.run(() => {
                        service.notifyConnected();
                    });
                }
            };

            eventSource.onerror = x => observer.error(x);

            return () => {
                eventSource.close();
            };
        });

        observable.subscribe({
            next: (x) => {
                const eventName = x.event;
                const eventData = x.data;
                this.zone.run(() => {
                    const service = this.eventNameToServiceMap.get(eventName);
                    if (service) {
                        service.notifyEvent(eventName, eventData);
                    }
                });
            },
            error: err => {
                this.logger.error('Error in stream: %O', err);

                // Notify all services of disconnection
                for (const service of this.services) {
                    this.zone.run(() => {
                        service.notifyDisconnected();
                    });
                }

                setTimeout(() => { this.createSseObserver(); }, this.STREAM_RETRY_INTERVAL_MS);
            }
        });
    }
}

/**
 * StreamServiceRegistry is responsible for initializing all
 * Stream Services. All services created by the registry
 * will be connected to a single stream via the DispatchService
 */
@Injectable({
    providedIn: 'root'
})
export class StreamServiceRegistry {
    private dispatch = inject(StreamDispatchService);
    private _modelFileService = inject(ModelFileService);
    private _serverStatusService = inject(ServerStatusService);
    private _connectedService = inject(ConnectedService);
    private _logService = inject(LogService);

    private initialized = false;

    /**
     * Call this method to finish initialization
     */
    public onInit(): void {
        if (this.initialized) {
            return;
        }
        this.initialized = true;

        // Register all services
        this.dispatch.registerService(this._connectedService);
        this.dispatch.registerService(this._serverStatusService);
        this.dispatch.registerService(this._modelFileService);
        this.dispatch.registerService(this._logService);

        this.dispatch.onInit();
    }

    get modelFileService(): ModelFileService { return this._modelFileService; }
    get serverStatusService(): ServerStatusService { return this._serverStatusService; }
    get connectedService(): ConnectedService { return this._connectedService; }
    get logService(): LogService { return this._logService; }
}
