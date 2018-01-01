import {Component, OnInit} from "@angular/core";
import {Observable} from "rxjs/Observable";

import * as Immutable from "immutable";

import {LoggerService} from "../../common/logger.service";
import {ServerStatusService} from "../../other/server-status.service";
import {Notification} from "../../other/notification";
import {NotificationService} from "../../other/notification.service";
import {StreamServiceRegistry} from "../../common/stream-service.registry";

@Component({
    selector: "app-header",
    templateUrl: "./header.component.html",
    styleUrls: ["./header.component.scss"],
})

export class HeaderComponent implements OnInit {
    // expose Notification type to template
    public Notification = Notification;

    public notifications: Observable<Immutable.List<Notification>>;

    private _serverStatusService: ServerStatusService;

    private _prevServerNotification: Notification;

    constructor(private _logger: LoggerService,
                _streamServiceRegistry: StreamServiceRegistry,
                private _notificationService: NotificationService) {
        this._serverStatusService = _streamServiceRegistry.serverStatusService;
        this.notifications = this._notificationService.notifications;
        this._prevServerNotification = null;
    }

    public dismiss(notif: Notification) {
        this._notificationService.hide(notif);
    }

    ngOnInit() {
        // Set up a subscriber to show server status notifications
        this._serverStatusService.status.subscribe({
            next: status => {
                if (status.server.up) {
                    // Remove any server notifications we may have added
                    if (this._prevServerNotification != null) {
                        this._notificationService.hide(this._prevServerNotification);
                        this._prevServerNotification = null;
                    }
                } else {
                    // Create a notification
                    const notification = new Notification({
                        level: Notification.Level.DANGER,
                        text: status.server.errorMessage
                    });
                    // Show it, if different from the existing one
                    if (
                            this._prevServerNotification == null ||
                            this._prevServerNotification.text !== notification.text
                    ) {
                        // Hide existing, if any
                        if (this._prevServerNotification != null) {
                            this._notificationService.hide(this._prevServerNotification);
                        }
                        this._prevServerNotification = notification;
                        this._notificationService.show(this._prevServerNotification);
                        this._logger.debug("New server notification: %O", this._prevServerNotification);
                    }
                }
            }
        });
    }
}
