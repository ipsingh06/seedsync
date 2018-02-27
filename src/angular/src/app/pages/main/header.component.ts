import {Component, OnInit} from "@angular/core";
import {Observable} from "rxjs/Observable";

import * as Immutable from "immutable";

import {LoggerService} from "../../services/utils/logger.service";
import {ServerStatusService} from "../../services/server/server-status.service";
import {Notification} from "../../services/utils/notification";
import {NotificationService} from "../../services/utils/notification.service";
import {StreamServiceRegistry} from "../../services/base/stream-service.registry";
import {Localization} from "../../common/localization";

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
    private _prevWaitingForRemoteScanNotification: Notification;

    constructor(private _logger: LoggerService,
                _streamServiceRegistry: StreamServiceRegistry,
                private _notificationService: NotificationService) {
        this._serverStatusService = _streamServiceRegistry.serverStatusService;
        this.notifications = this._notificationService.notifications;
        this._prevServerNotification = null;
        this._prevWaitingForRemoteScanNotification = null;
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

        // Set up a subscriber to show waiting for remote scan notification
        this._serverStatusService.status.subscribe({
            next: status => {
                if (status.server.up && status.controller.latestRemoteScanTime == null) {
                    // Server up and no remote scan - show notification if not already shown
                    if(this._prevWaitingForRemoteScanNotification == null) {
                        this._prevWaitingForRemoteScanNotification = new Notification({
                            level: Notification.Level.INFO,
                            text: Localization.Notification.STATUS_REMOTE_SCAN_WAITING
                        });
                        this._notificationService.show(this._prevWaitingForRemoteScanNotification);
                    }
                } else {
                    // Server down or remote scan available - hide notification if showing
                    if(this._prevWaitingForRemoteScanNotification != null) {
                        this._notificationService.hide(this._prevWaitingForRemoteScanNotification);
                        this._prevWaitingForRemoteScanNotification = null;
                    }
                }
            }
        });
    }
}
