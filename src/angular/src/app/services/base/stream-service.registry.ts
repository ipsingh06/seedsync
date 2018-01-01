import {Injectable, NgZone} from "@angular/core";
import {Observable} from "rxjs/Observable";

import {ModelFileService} from "../files/model-file.service";
import {ServerStatusService} from "../server/server-status.service";
import {LoggerService} from "../utils/logger.service";
import {ConnectedService} from "../utils/connected.service";


export class EventSourceFactory {
    static createEventSource(url: string) {
        return new EventSource(url);
    }
}


export interface IStreamService {
    /**
     * Returns the event names supported by this stream service
     * @returns {string[]}
     */
    getEventNames(): string[];

    /**
     * Notifies the stream service that it is now connected
     */
    notifyConnected();

    /**
     * Notifies the stream service that it is now disconnected
     */
    notifyDisconnected();

    /**
     * Notifies the stream service of an event
     * @param {string} eventName
     * @param {string} data
     */
    notifyEvent(eventName: string, data: string);
}


/**
 * StreamDispatchService is the top-level service that connects to
 * the multiplexed SSE stream. It listens for SSE events and dispatches
 * them to whichever IStreamService that requested them.
 */
@Injectable()
export class StreamDispatchService {
    private readonly STREAM_URL = "/server/stream";

    private readonly STREAM_RETRY_INTERVAL_MS = 3000;

    private _eventNameToServiceMap: Map<string, IStreamService> = new Map();
    private _services: IStreamService[] = [];

    constructor(private _logger: LoggerService,
                private _zone: NgZone) {
    }

    /**
     * Call this method to finish initialization
     */
    public onInit() {
        this.createSseObserver();
    }

    /**
     * Register an IStreamService with the dispatch
     * @param {IStreamService} service
     * @returns {IStreamService}
     */
    public registerService(service: IStreamService) {
        for(let eventName of service.getEventNames()) {
            this._eventNameToServiceMap.set(eventName, service);
        }
        this._services.push(service);
        return service;
    }

    private createSseObserver() {
        const observable = Observable.create(observer => {
            const eventSource = EventSourceFactory.createEventSource(this.STREAM_URL);
            for (let eventName of Array.from(this._eventNameToServiceMap.keys())) {
                eventSource.addEventListener(eventName, event => observer.next(
                    {
                        "event": eventName,
                        "data": event.data
                    }
                ));
            }

            // noinspection SpellCheckingInspection
            // noinspection JSUnusedLocalSymbols
            eventSource.onopen = event => {
                this._logger.info("Connected to server stream");

                // Notify all services of connection
                for (let service of this._services) {
                    service.notifyConnected();
                }
            };

            eventSource.onerror = x => this._zone.run(() => observer.error(x));

            return () => {
                eventSource.close();
            };
        });
        observable.subscribe({
            next: (x) => {
                let eventName = x["event"];
                let eventData = x["data"];
                // this._logger.debug("Received event:", eventName);
                this._eventNameToServiceMap.get(eventName).notifyEvent(eventName, eventData);
            },
            error: err => {
                this._logger.error("Error in stream: %O", err);

                // Notify all services of disconnection
                for (let service of this._services) {
                    service.notifyDisconnected();
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
@Injectable()
export class StreamServiceRegistry {

    constructor(private _dispatch: StreamDispatchService,
                private _modelFileService: ModelFileService,
                private _serverStatusService: ServerStatusService,
                private _connectedService: ConnectedService) {
        // Register all services
        _dispatch.registerService(_connectedService);
        _dispatch.registerService(_serverStatusService);
        _dispatch.registerService(_modelFileService);
    }

    /**
     * Call this method to finish initialization
     */
    public onInit() {
        this._dispatch.onInit();
    }

    get modelFileService(): ModelFileService { return this._modelFileService; }
    get serverStatusService(): ServerStatusService { return this._serverStatusService; }
    get connectedService(): ConnectedService { return this._connectedService; }
}

/**
 * StreamServiceRegistry factory and provider
 */
export let streamServiceRegistryFactory = (
        _dispatch: StreamDispatchService,
        _modelFileService: ModelFileService,
        _serverStatusService: ServerStatusService,
        _connectedService: ConnectedService
) => {
    let streamServiceRegistry = new StreamServiceRegistry(
        _dispatch,
        _modelFileService,
        _serverStatusService,
        _connectedService
    );
    streamServiceRegistry.onInit();
    return streamServiceRegistry;
};

// noinspection JSUnusedGlobalSymbols
export let StreamServiceRegistryProvider = {
    provide: StreamServiceRegistry,
    useFactory: streamServiceRegistryFactory,
    deps: [
        StreamDispatchService,
        ModelFileService,
        ServerStatusService,
        ConnectedService
    ]
};
