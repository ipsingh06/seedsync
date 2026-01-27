import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';

import { LoggerService } from '../../services/utils/logger.service';
import { ServerStatusService } from '../../services/server/server-status.service';
import { Notification, NotificationLevel } from '../../services/utils/notification';
import { NotificationService } from '../../services/utils/notification.service';
import { StreamServiceRegistry } from '../../services/base/stream-service.registry';
import { Localization } from '../../common/localization';

@Component({
    selector: 'app-header',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './header.component.html',
    styleUrl: './header.component.scss'
})
export class HeaderComponent implements OnInit {
    // Expose NotificationLevel type to template
    public NotificationLevel = NotificationLevel;

    public notifications: Observable<readonly Notification[]>;

    private serverStatusService: ServerStatusService;

    private prevServerNotification: Notification | null = null;
    private prevWaitingForRemoteScanNotification: Notification | null = null;
    private prevRemoteServerErrorNotification: Notification | null = null;

    private logger = inject(LoggerService);
    private streamServiceRegistry = inject(StreamServiceRegistry);
    private notificationService = inject(NotificationService);

    constructor() {
        this.serverStatusService = this.streamServiceRegistry.serverStatusService;
        this.notifications = this.notificationService.notifications;
    }

    public dismiss(notif: Notification): void {
        this.notificationService.hide(notif);
    }

    ngOnInit(): void {
        // Set up a subscriber to show server status notifications
        this.serverStatusService.status.subscribe({
            next: status => {
                if (status.server.up) {
                    // Remove any server notifications we may have added
                    if (this.prevServerNotification != null) {
                        this.notificationService.hide(this.prevServerNotification);
                        this.prevServerNotification = null;
                    }
                } else {
                    // Create a notification
                    const notification = Notification.danger(status.server.errorMessage ?? '', false);

                    // Show it, if different from the existing one
                    if (
                        this.prevServerNotification == null ||
                        this.prevServerNotification.text !== notification.text
                    ) {
                        // Hide existing, if any
                        if (this.prevServerNotification != null) {
                            this.notificationService.hide(this.prevServerNotification);
                        }
                        this.prevServerNotification = notification;
                        this.notificationService.show(this.prevServerNotification);
                        this.logger.debug('New server notification: %O', this.prevServerNotification);
                    }
                }
            }
        });

        // Set up a subscriber to show waiting for remote scan notification
        this.serverStatusService.status.subscribe({
            next: status => {
                if (status.server.up && status.controller.latestRemoteScanTime == null) {
                    // Server up and no remote scan - show notification if not already shown
                    if (this.prevWaitingForRemoteScanNotification == null) {
                        this.prevWaitingForRemoteScanNotification = Notification.info(
                            Localization.Notification.STATUS_REMOTE_SCAN_WAITING,
                            false
                        );
                        this.notificationService.show(this.prevWaitingForRemoteScanNotification);
                    }
                } else {
                    // Server down or remote scan available - hide notification if showing
                    if (this.prevWaitingForRemoteScanNotification != null) {
                        this.notificationService.hide(this.prevWaitingForRemoteScanNotification);
                        this.prevWaitingForRemoteScanNotification = null;
                    }
                }
            }
        });

        // Set up a subscriber to show remote server error notifications
        this.serverStatusService.status.subscribe({
            next: status => {
                if (status.server.up && status.controller.latestRemoteScanFailed === true) {
                    // Server up and remote scan failed - show notification if not already shown
                    const text = Localization.Notification.STATUS_REMOTE_SERVER_ERROR(
                        status.controller.latestRemoteScanError ?? ''
                    );
                    if (this.prevRemoteServerErrorNotification != null
                           && this.prevRemoteServerErrorNotification.text !== text) {
                        // Text changed, hide old notification
                        this.notificationService.hide(this.prevRemoteServerErrorNotification);
                        this.prevRemoteServerErrorNotification = null;
                    }
                    if (this.prevRemoteServerErrorNotification == null) {
                        this.prevRemoteServerErrorNotification = Notification.warning(text, false);
                        this.notificationService.show(this.prevRemoteServerErrorNotification);
                    }
                } else {
                    // Server down or error is gone - hide notification if showing
                    if (this.prevRemoteServerErrorNotification != null) {
                        this.notificationService.hide(this.prevRemoteServerErrorNotification);
                        this.prevRemoteServerErrorNotification = null;
                    }
                }
            }
        });
    }
}
