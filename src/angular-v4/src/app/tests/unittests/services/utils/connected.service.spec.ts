import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {ConnectedService} from "../../../../services/utils/connected.service";


describe("Testing connected service", () => {
    let connectedService: ConnectedService;

    let connectedResults: boolean[];

    beforeEach(fakeAsync(() => {
        TestBed.configureTestingModule({
            providers: [
                ConnectedService
            ]
        });

        connectedService = TestBed.get(ConnectedService);

        connectedResults = [];
        connectedService.connected.subscribe({
            next: connected => {
                connectedResults.push(connected);
            }
        });
        tick();
    }));

    it("should create an instance", () => {
        expect(connectedService).toBeDefined();
    });

    it("should start off unconnected", () => {
        expect(connectedResults).toEqual([false]);
    });

    it("should notify on first connection success", fakeAsync(() => {
        connectedService.notifyConnected();
        tick();

        expect(connectedResults).toEqual([false, true]);
    }));

    it("should NOT notify on first connection failure", fakeAsync(() => {
        connectedService.notifyDisconnected();
        tick();

        expect(connectedResults).toEqual([false]);
    }));

    it("should notify on disconnection", fakeAsync(() => {
        connectedService.notifyConnected();
        tick();
        connectedService.notifyDisconnected();
        tick();
        expect(connectedResults).toEqual([false, true, false]);
        tick();
    }));

    it("should notify on re-connection", fakeAsync(() => {
        connectedService.notifyConnected();
        tick();
        connectedService.notifyDisconnected();
        tick();
        connectedService.notifyConnected();
        tick();
        expect(connectedResults).toEqual([false, true, false, true]);
    }));

    it("should NOT notify on repeated disconnection", fakeAsync(() => {
        connectedService.notifyConnected();
        tick();
        connectedService.notifyDisconnected();
        tick();
        connectedService.notifyDisconnected();
        tick();
        expect(connectedResults).toEqual([false, true, false]);
    }));

    it("should NOT notify on repeated re-connection", fakeAsync(() => {
        connectedService.notifyConnected();
        tick();
        connectedService.notifyConnected();
        tick();
        expect(connectedResults).toEqual([false, true]);
    }));

});
