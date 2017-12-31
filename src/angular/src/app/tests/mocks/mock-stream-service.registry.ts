import {TestBed} from "@angular/core/testing";

import {RestService} from "../../other/rest.service";
import {ConnectedService} from "../../other/connected.service";


export class MockStreamServiceRegistry {
    // Real connected service
    connectedService = TestBed.get(ConnectedService);

    // Real rest service
    restService = TestBed.get(RestService);

    connect() {
        this.restService.notifyConnected();
        this.connectedService.notifyConnected();
    }

    disconnect() {
        this.restService.notifyDisconnected();
        this.connectedService.notifyDisconnected();
    }
}
