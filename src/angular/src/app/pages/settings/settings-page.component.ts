import {ChangeDetectionStrategy, Component} from '@angular/core';
import {Observable} from "rxjs/Observable";

import {LoggerService} from "../../common/logger.service";
import {ConfigService} from "../../other/config.service";
import {Config} from "../../other/config";
import {Notification} from "../../other/notification";
import {Localization} from "../../common/localization";
import {NotificationService} from "../../other/notification.service";
import {ServerStatusService} from "../../other/server-status.service";
import {ServerCommandService} from "../../other/server-command.service";
import {ServerStatus} from "../../other/server-status";
import {
    OPTIONS_CONTEXT_CONNECTIONS, OPTIONS_CONTEXT_DISCOVERY, OPTIONS_CONTEXT_OTHER,
    OPTIONS_CONTEXT_SERVER
} from "./options-list";

@Component({
    selector: 'settings-page',
    templateUrl: './settings-page.component.html',
    styleUrls: ['./settings-page.component.scss'],
    providers: [],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class SettingsPageComponent {
    public OPTIONS_CONTEXT_SERVER = OPTIONS_CONTEXT_SERVER;
    public OPTIONS_CONTEXT_DISCOVERY = OPTIONS_CONTEXT_DISCOVERY;
    public OPTIONS_CONTEXT_CONNECTIONS = OPTIONS_CONTEXT_CONNECTIONS;
    public OPTIONS_CONTEXT_OTHER = OPTIONS_CONTEXT_OTHER;

    public config: Observable<Config>;

    public commandsEnabled: boolean;

    private _configRestartNotif: Notification;
    private _badValueNotifs: Map<string, Notification>;

    constructor(private _logger: LoggerService,
                private _configService: ConfigService,
                private _notifService: NotificationService,
                private _statusService: ServerStatusService,
                private _commandService: ServerCommandService) {
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
        this._statusService.status.subscribe({
            next: (status: ServerStatus) => {
                if(!status.connected) {
                    // Server went down, hide the config restart notification
                    this._notifService.hide(this._configRestartNotif);
                }

                // Enable/disable commands based on server connection
                this.commandsEnabled = status.connected;
            }
        });
    }

    onSetConfig(section: string, option: string, value: any) {
        this._configService.set(section, option, value).subscribe({
            next: reaction => {
                const notifKey = section + "." + option;
                if(reaction.success) {
                    this._logger.info(reaction.data);

                    // Hide bad value notification, if any
                    if(this._badValueNotifs.has(notifKey)) {
                        this._notifService.hide(this._badValueNotifs.get(notifKey));
                        this._badValueNotifs.delete(notifKey);
                    }

                    // Show the restart notification
                    this._notifService.show(this._configRestartNotif);
                } else {
                    // Show bad value notification
                    let notif = new Notification({
                        level: Notification.Level.DANGER,
                        dismissible: true,
                        text: reaction.errorMessage
                    });
                    if(this._badValueNotifs.has(notifKey)) {
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
                if(reaction.success) {
                    this._logger.info(reaction.data);
                } else {
                    this._logger.error(reaction.errorMessage);
                }
            }
        });
    }
}
