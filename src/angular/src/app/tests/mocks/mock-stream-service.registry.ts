import {TestBed} from "@angular/core/testing";

import {ConnectedService} from "../../services/utils/connected.service";
import {MockModelFileService} from "./mock-model-file.service";


export class MockStreamServiceRegistry {
    // Real connected service
    connectedService = TestBed.get(ConnectedService);

    // Fake model file service
    modelFileService = new MockModelFileService();

    connect() {
        this.connectedService.notifyConnected();
    }

    disconnect() {
        this.connectedService.notifyDisconnected();
    }
}
