import {ChangeDetectionStrategy, Component, OnInit} from "@angular/core";
import {Observable} from "rxjs/Observable";

import {LoggerService} from "../../services/utils/logger.service";
import {ConfigService} from "../../services/settings/config.service";
import {Config} from "../../services/settings/config";
import {Notification} from "../../services/utils/notification";
import {Localization} from "../../common/localization";
import {NotificationService} from "../../services/utils/notification.service";
import {ServerCommandService} from "../../services/server/server-command.service";
import {
    OPTIONS_CONTEXT_CONNECTIONS, OPTIONS_CONTEXT_DISCOVERY, OPTIONS_CONTEXT_OTHER,
    OPTIONS_CONTEXT_SERVER, OPTIONS_CONTEXT_AUTOQUEUE
} from "./options-list";
import {ConnectedService} from "../../services/utils/connected.service";
import {StreamServiceRegistry} from "../../services/base/stream-service.registry";

@Component({
    selector: "app-settings-page",
    templateUrl: "./settings-page.component.html",
    styleUrls: ["./settings-page.component.scss"],
    providers: [],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class SettingsPageComponent implements OnInit {
    public OPTIONS_CONTEXT_SERVER = OPTIONS_CONTEXT_SERVER;
    public OPTIONS_CONTEXT_DISCOVERY = OPTIONS_CONTEXT_DISCOVERY;
    public OPTIONS_CONTEXT_CONNECTIONS = OPTIONS_CONTEXT_CONNECTIONS;
    public OPTIONS_CONTEXT_OTHER = OPTIONS_CONTEXT_OTHER;
    public OPTIONS_CONTEXT_AUTOQUEUE = OPTIONS_CONTEXT_AUTOQUEUE;

    public config: Observable<Config>;

    public commandsEnabled: boolean;

    private _connectedService: ConnectedService;

    private _configRestartNotif: Notification;
    private _badValueNotifs: Map<string, Notification>;

    constructor(private _logger: LoggerService,
                _streamServiceRegistry: StreamServiceRegistry,
                private _configService: ConfigService,
                private _notifService: NotificationService,
                private _commandService: ServerCommandService) {
        this._connectedService = _streamServiceRegistry.connectedService;
        this.config = _configService.config;
        this.commandsEnabled = false;
        this._configRestartNotif = new Notification({
            level: Notification.Level.INFO,
            text: Localization.Notification.CONFIG_RESTART
        });
        this._badValueNotifs = new Map();
    }

    // noinspection JSUnusedGlobalSymbols
    ngOnInit() {
        this._connectedService.connected.subscribe({
            next: (connected: boolean) => {
                if (!connected) {
                    // Server went down, hide the config restart notification
                    this._notifService.hide(this._configRestartNotif);
                }

                // Enable/disable commands based on server connection
                this.commandsEnabled = connected;
            }
        });
    }

    onSetConfig(section: string, option: string, value: any) {
        this._configService.set(section, option, value).subscribe({
            next: reaction => {
                const notifKey = section + "." + option;
                if (reaction.success) {
                    this._logger.info(reaction.data);

                    // Hide bad value notification, if any
                    if (this._badValueNotifs.has(notifKey)) {
                        this._notifService.hide(this._badValueNotifs.get(notifKey));
                        this._badValueNotifs.delete(notifKey);
                    }

                    // Show the restart notification
                    this._notifService.show(this._configRestartNotif);
                } else {
                    // Show bad value notification
                    const notif = new Notification({
                        level: Notification.Level.DANGER,
                        dismissible: true,
                        text: reaction.errorMessage
                    });
                    if (this._badValueNotifs.has(notifKey)) {
                        this._notifService.hide(this._badValueNotifs.get(notifKey));
                    }
                    this._notifService.show(notif);
                    this._badValueNotifs.set(notifKey, notif);

                    this._logger.error(reaction.errorMessage);
                }
            }
        });
    }

    onCommandRestart() {
        this._commandService.restart().subscribe({
            next: reaction => {
                if (reaction.success) {
                    this._logger.info(reaction.data);
                } else {
                    this._logger.error(reaction.errorMessage);
                }
            }
        });
    }
}
