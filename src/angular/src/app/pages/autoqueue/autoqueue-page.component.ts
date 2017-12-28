import {ChangeDetectionStrategy, Component, OnInit} from "@angular/core";
import {Observable} from "rxjs/Observable";

import * as Immutable from "immutable";

import {LoggerService} from "../../common/logger.service";
import {AutoQueueService} from "../../other/autoqueue.service";
import {AutoQueuePattern} from "../../other/autoqueue-pattern";
import {Notification} from "../../other/notification";
import {NotificationService} from "../../other/notification.service";
import {ServerStatusService} from "../../other/server-status.service";
import {ServerStatus} from "../../other/server-status";


@Component({
    selector: "app-autoqueue-page",
    templateUrl: "./autoqueue-page.component.html",
    styleUrls: ["./autoqueue-page.component.scss"],
    providers: [],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class AutoQueuePageComponent implements OnInit {

    public patterns: Observable<Immutable.List<AutoQueuePattern>>;
    public newPattern: string;

    public enabled: boolean;

    constructor(private _logger: LoggerService,
                private _autoqueueService: AutoQueueService,
                private _notifService: NotificationService,
                private _statusService: ServerStatusService) {
        this.patterns = _autoqueueService.patterns;
        this.newPattern = "";
        this.enabled = false;
    }

    // noinspection JSUnusedGlobalSymbols
    ngOnInit() {
        this._statusService.status.subscribe({
            next: (status: ServerStatus) => {
                this.enabled = status.connected;
                if (!this.enabled) {
                    // Clear the input box
                    this.newPattern = "";
                }
            }
        });
    }

    onAddPattern() {
        this._autoqueueService.add(this.newPattern).subscribe({
            next: reaction => {
                if (reaction.success) {
                    // Clear the input box
                    this.newPattern = "";
                } else {
                    // Show dismissible notification
                    const notif = new Notification({
                        level: Notification.Level.DANGER,
                        dismissible: true,
                        text: reaction.errorMessage
                    });
                    this._notifService.show(notif);
                }
            }
        });
    }

    onRemovePattern(pattern: AutoQueuePattern) {
        this._autoqueueService.remove(pattern.pattern).subscribe({
            next: reaction => {
                if (reaction.success) {
                    // Nothing to do
                } else {
                    // Show dismissible notification
                    const notif = new Notification({
                        level: Notification.Level.DANGER,
                        dismissible: true,
                        text: reaction.errorMessage
                    });
                    this._notifService.show(notif);
                }
            }
        });
    }
}
