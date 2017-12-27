import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import * as Immutable from "immutable";

import {NotificationService} from "../../../other/notification.service";
import {LoggerService} from "../../../common/logger.service";
import {Notification} from "../../../other/notification";

class TestNotificationService extends NotificationService {

}

describe("Testing notification service", () => {
    let notificationService: TestNotificationService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                LoggerService,
                {provide: NotificationService, useClass: TestNotificationService},
            ]
        });

        notificationService = TestBed.get(NotificationService);
    });


    it("should create an instance", () => {
        expect(notificationService).toBeDefined();
    });

    it("should show notification", fakeAsync(() => {
        const expectedNotification = new Notification({level: Notification.Level.DANGER, text: "danger"});

        notificationService.show(expectedNotification);

        let actualCount = 0;
        notificationService.notifications.subscribe({
            next: list => {
                expect(list.size).toBe(1);
                expect(Immutable.is(expectedNotification, list.get(0))).toBe(true);
                actualCount++;
            }
        });

        tick();
        expect(actualCount).toBe(1);
    }));

    it("should hide notification", fakeAsync(() => {
        const expectedNotification = new Notification({level: Notification.Level.DANGER, text: "danger"});

        notificationService.show(expectedNotification);
        tick();
        notificationService.hide(expectedNotification);

        let actualCount = 0;
        notificationService.notifications.subscribe({
            next: list => {
                expect(list.size).toBe(0);
                actualCount++;
            }
        });

        tick();
        expect(actualCount).toBe(1);
    }));


    it("should only send one update if show is called twice", fakeAsync(() => {
        const expectedNotification = new Notification({level: Notification.Level.DANGER, text: "danger"});

        notificationService.show(expectedNotification);

        let actualCount = 0;
        notificationService.notifications.subscribe({
            next: list => {
                actualCount++;
            }
        });
        tick();
        notificationService.show(expectedNotification);
        tick();

        expect(actualCount).toBe(1);
    }));

    it("should only send one update if hide is called twice", fakeAsync(() => {
        const expectedNotification = new Notification({level: Notification.Level.DANGER, text: "danger"});

        notificationService.show(expectedNotification);
        tick();
        notificationService.hide(expectedNotification);

        let actualCount = 0;
        notificationService.notifications.subscribe({
            next: list => {
                actualCount++;
            }
        });

        tick();
        notificationService.hide(expectedNotification);
        tick();

        expect(actualCount).toBe(1);
    }));

    it("should sort notifications by level", fakeAsync(() => {
        const noteDanger = new Notification({level: Notification.Level.DANGER, text: "danger"});
        const noteInfo = new Notification({level: Notification.Level.INFO, text: "info"});
        const noteWarning = new Notification({level: Notification.Level.WARNING, text: "warning"});
        const noteSuccess = new Notification({level: Notification.Level.SUCCESS, text: "success"});

        notificationService.show(noteDanger);
        notificationService.show(noteInfo);
        notificationService.show(noteWarning);
        notificationService.show(noteSuccess);

        let actualCount = 0;
        notificationService.notifications.subscribe({
            next: list => {
                expect(list.size).toBe(4);
                expect(Immutable.is(noteDanger, list.get(0))).toBe(true);
                expect(Immutable.is(noteWarning, list.get(1))).toBe(true);
                expect(Immutable.is(noteInfo, list.get(2))).toBe(true);
                expect(Immutable.is(noteSuccess, list.get(3))).toBe(true);
                actualCount++;
            }
        });

        tick();
        expect(actualCount).toBe(1);
    }));

    it("should sort notifications by timestamp", fakeAsync(() => {
        function sleepFor( sleepDuration ) {
            const now = new Date().getTime();
            while (new Date().getTime() < now + sleepDuration) { /* do nothing */ }
        }

        // Sleep a little between inits
        const noteOlder = new Notification({level: Notification.Level.DANGER, text: "older"});
        sleepFor(10);
        const noteNewer = new Notification({level: Notification.Level.DANGER, text: "newer"});
        sleepFor(10);
        const noteNewest = new Notification({level: Notification.Level.DANGER, text: "newest"});

        notificationService.show(noteNewer);
        notificationService.show(noteNewest);
        notificationService.show(noteOlder);

        let actualCount = 0;
        notificationService.notifications.subscribe({
            next: list => {
                expect(list.size).toBe(3);
                expect(Immutable.is(noteNewest, list.get(0))).toBe(true);
                expect(Immutable.is(noteNewer, list.get(1))).toBe(true);
                expect(Immutable.is(noteOlder, list.get(2))).toBe(true);
                actualCount++;
            }
        });

        tick();
        expect(actualCount).toBe(1);
    }));

    it("should sort notifications by level first, then timestamp", fakeAsync(() => {
        function sleepFor( sleepDuration ) {
            const now = new Date().getTime();
            while (new Date().getTime() < now + sleepDuration) { /* do nothing */ }
        }

        // Sleep a little between inits
        const noteOlder = new Notification({level: Notification.Level.DANGER, text: "older"});
        sleepFor(10);
        const noteNewer = new Notification({level: Notification.Level.INFO, text: "newer"});
        sleepFor(10);
        const noteNewest = new Notification({level: Notification.Level.INFO, text: "newest"});

        notificationService.show(noteNewer);
        notificationService.show(noteNewest);
        notificationService.show(noteOlder);

        let actualCount = 0;
        notificationService.notifications.subscribe({
            next: list => {
                expect(list.size).toBe(3);
                expect(Immutable.is(noteOlder, list.get(0))).toBe(true);
                expect(Immutable.is(noteNewest, list.get(1))).toBe(true);
                expect(Immutable.is(noteNewer, list.get(2))).toBe(true);
                actualCount++;
            }
        });

        tick();
        expect(actualCount).toBe(1);
    }));
});
