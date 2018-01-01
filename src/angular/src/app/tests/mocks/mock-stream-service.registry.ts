import {TestBed} from "@angular/core/testing";

import {ConnectedService} from "../../services/utils/connected.service";


export class MockStreamServiceRegistry {
    // Real connected service
    connectedService = TestBed.get(ConnectedService);

    connect() {
        this.connectedService.notifyConnected();
    }

    disconnect() {
        this.connectedService.notifyDisconnected();
    }
}
