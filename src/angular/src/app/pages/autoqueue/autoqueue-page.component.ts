import {ChangeDetectionStrategy, Component, OnInit} from "@angular/core";
import {Observable} from "rxjs/Observable";

import * as Immutable from "immutable";

import {AutoQueueService} from "../../services/autoqueue/autoqueue.service";
import {AutoQueuePattern} from "../../services/autoqueue/autoqueue-pattern";
import {Notification} from "../../services/utils/notification";
import {NotificationService} from "../../services/utils/notification.service";
import {ConnectedService} from "../../services/utils/connected.service";
import {StreamServiceRegistry} from "../../services/base/stream-service.registry";


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

    private _connectedService: ConnectedService;

    constructor(private _autoqueueService: AutoQueueService,
                private _notifService: NotificationService,
                _streamServiceRegistry: StreamServiceRegistry) {
        this._connectedService = _streamServiceRegistry.connectedService;
        this.patterns = _autoqueueService.patterns;
        this.newPattern = "";
        this.enabled = false;
    }

    // noinspection JSUnusedGlobalSymbols
    ngOnInit() {
        this._connectedService.connected.subscribe({
            next: (connected: boolean) => {
                this.enabled = connected;
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
