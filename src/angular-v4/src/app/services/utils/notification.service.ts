import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import * as Immutable from "immutable";

import {Notification} from "./notification";


/**
 * NotificationService manages which notifications are shown or hidden
 */
@Injectable()
export class NotificationService {

    private _notifications: Immutable.List<Notification> = Immutable.List([]);
    private _notificationsSubject: BehaviorSubject<Immutable.List<Notification>> =
            new BehaviorSubject(this._notifications);

    // noinspection UnterminatedStatementJS
    private _comparator = (a: Notification, b: Notification): number => {
        // First sort by level
        if (a.level !== b.level) {
            const statusPriorities = {
                [Notification.Level.DANGER]: 0,
                [Notification.Level.WARNING]: 1,
                [Notification.Level.INFO]: 2,
                [Notification.Level.SUCCESS]: 3,
            };
            if (statusPriorities[a.level] !== statusPriorities[b.level]) {
                return statusPriorities[a.level] - statusPriorities[b.level];
            }
        }
        // Then sort by timestamp
        return b.timestamp - a.timestamp;
    }

    constructor() {}

    get notifications(): Observable<Immutable.List<Notification>> {
        return this._notificationsSubject.asObservable();
    }

    public show(notification: Notification) {
        const index = this._notifications.findIndex(value => Immutable.is(value, notification));
        if (index < 0) {
            const notifications = this._notifications.push(notification);
            this._notifications = notifications.sort(this._comparator).toList();
            this._notificationsSubject.next(this._notifications);
        }
    }

    public hide(notification: Notification) {
        const index = this._notifications.findIndex(value => Immutable.is(value, notification));
        if (index >= 0) {
            this._notifications = this._notifications.remove(index);
            this._notificationsSubject.next(this._notifications);
        }
    }
}
