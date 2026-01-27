import { Injectable } from '@angular/core';

import { IStreamService } from './stream-service.registry';

/**
 * BaseStreamService represents a web services that fetches data
 * from a SSE stream. This class provides utilities to register
 * for event notifications from a multiplexed stream.
 *
 * Note: services derived from this class SHOULD NOT be created
 *       directly. They need to be added to StreamServiceRegistry
 *       and fetched from an instance of that registry class.
 */
@Injectable()
export abstract class BaseStreamService implements IStreamService {
    private eventNames: string[] = [];

    getEventNames(): string[] {
        return this.eventNames;
    }

    notifyConnected(): void {
        this.onConnected();
    }

    notifyDisconnected(): void {
        this.onDisconnected();
    }

    notifyEvent(eventName: string, data: string): void {
        this.onEvent(eventName, data);
    }

    protected registerEventName(eventName: string): void {
        this.eventNames.push(eventName);
    }

    /**
     * Callback for a new event
     */
    protected abstract onEvent(eventName: string, data: string): void;

    /**
     * Callback for connected
     */
    protected abstract onConnected(): void;

    /**
     * Callback for disconnected
     */
    protected abstract onDisconnected(): void;
}
