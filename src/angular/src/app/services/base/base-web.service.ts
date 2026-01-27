import { Injectable, inject } from '@angular/core';

import { ConnectedService } from '../utils/connected.service';

/**
 * BaseWebService provides utility to be notified when connection to
 * the backend server is lost and regained. Non-streaming web services
 * can use these notifications to re-issue get requests.
 */
@Injectable()
export abstract class BaseWebService {
    private connectedService = inject(ConnectedService);

    /**
     * Call this method to finish initialization
     */
    public onInit(): void {
        this.connectedService.connected.subscribe({
            next: connected => {
                if (connected) {
                    this.onConnected();
                } else {
                    this.onDisconnected();
                }
            }
        });
    }

    /**
     * Callback for connected
     */
    protected abstract onConnected(): void;

    /**
     * Callback for disconnected
     */
    protected abstract onDisconnected(): void;
}
