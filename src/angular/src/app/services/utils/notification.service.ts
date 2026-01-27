import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';

import { Notification, NotificationLevel } from './notification';

/**
 * NotificationService manages which notifications are shown or hidden
 */
@Injectable({
    providedIn: 'root'
})
export class NotificationService {
    private _notifications: Notification[] = [];
    private notificationsSubject = new BehaviorSubject<readonly Notification[]>([]);

    private comparator = (a: Notification, b: Notification): number => {
        // First sort by level
        if (a.level !== b.level) {
            const statusPriorities: Record<NotificationLevel, number> = {
                [NotificationLevel.DANGER]: 0,
                [NotificationLevel.WARNING]: 1,
                [NotificationLevel.INFO]: 2,
                [NotificationLevel.SUCCESS]: 3
            };
            if (statusPriorities[a.level] !== statusPriorities[b.level]) {
                return statusPriorities[a.level] - statusPriorities[b.level];
            }
        }
        // Then sort by timestamp
        return b.timestamp - a.timestamp;
    };

    get notifications(): Observable<readonly Notification[]> {
        return this.notificationsSubject.asObservable();
    }

    public show(notification: Notification): void {
        const index = this._notifications.findIndex(value =>
            value.text === notification.text && value.level === notification.level
        );
        if (index < 0) {
            this._notifications = [...this._notifications, notification];
            this._notifications.sort(this.comparator);
            this.notificationsSubject.next(Object.freeze([...this._notifications]));
        }
    }

    public hide(notification: Notification): void {
        const index = this._notifications.findIndex(value =>
            value.text === notification.text && value.level === notification.level
        );
        if (index >= 0) {
            this._notifications = [
                ...this._notifications.slice(0, index),
                ...this._notifications.slice(index + 1)
            ];
            this.notificationsSubject.next(Object.freeze([...this._notifications]));
        }
    }
}
