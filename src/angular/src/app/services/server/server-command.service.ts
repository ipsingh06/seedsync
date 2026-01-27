import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { BaseWebService } from '../base/base-web.service';
import { RestService, WebReaction } from '../utils/rest.service';

/**
 * ServerCommandService handles sending commands to the backend server
 */
@Injectable({
    providedIn: 'root'
})
export class ServerCommandService extends BaseWebService {
    private readonly RESTART_URL = '/server/command/restart';

    private restService = inject(RestService);

    /**
     * Send a restart command to the server
     */
    public restart(): Observable<WebReaction> {
        return this.restService.sendRequest(this.RESTART_URL);
    }

    protected onConnected(): void {
        // Nothing to do
    }

    protected onDisconnected(): void {
        // Nothing to do
    }
}
