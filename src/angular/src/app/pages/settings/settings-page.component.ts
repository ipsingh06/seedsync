import {ChangeDetectionStrategy, Component} from '@angular/core';
import {Observable} from "rxjs/Observable";

import {LoggerService} from "../../common/logger.service";
import {ConfigService} from "../../other/config.service";
import {Config} from "../../other/config";
import {OptionType} from "./option.component";
import {Notification} from "../../other/notification";
import {Localization} from "../../common/localization";
import {NotificationService} from "../../other/notification.service";
import {ServerStatusService} from "../../other/server-status.service";
import {ServerCommandService} from "../../other/server-command.service";
import {ServerStatus} from "../../other/server-status";

@Component({
    selector: 'settings-page',
    templateUrl: './settings-page.component.html',
    styleUrls: ['./settings-page.component.scss'],
    providers: [],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class SettingsPageComponent {
    public config: Observable<Config>;

    public commandsEnabled: boolean;

    public optionsLeft: IOption[] = [
        {
            type: OptionType.Text,
            label: "Server Address",
            valuePath: ["lftp", "remote_address"],
            description: null
        },
        {
            type: OptionType.Text,
            label: "Server User",
            valuePath: ["lftp", "remote_username"],
            description: null
        },
        {
            type: OptionType.Text,
            label: "Server Directory",
            valuePath: ["lftp", "remote_path"],
            description: "Path on the remote server from which to download files and directories."
        },
        {
            type: OptionType.Text,
            label: "Local Directory",
            valuePath: ["lftp", "local_path"],
            description: "Path on the local machine where downloaded files and directories " +
                         "are placed."
        },
        {
            type: OptionType.Text,
            label: "Server Script Path",
            valuePath: ["lftp", "remote_path_to_scan_script"],
            description: "Path on remote server where the scanner script is placed."
        },
        {
            type: OptionType.Text,
            label: "Remote Scan Interval (ms)",
            valuePath: ["controller", "interval_ms_remote_scan"],
            description: "How often the remote server is scanned for new files."
        },
        {
            type: OptionType.Text,
            label: "Local Scan Interval (ms)",
            valuePath: ["controller", "interval_ms_local_scan"],
            description: "How often the local directory is scanned."
        },
        {
            type: OptionType.Text,
            label: "Downloading Scan Interval (ms)",
            valuePath: ["controller", "interval_ms_downloading_scan"],
            description: "How often the downloading information is updated."
        },
    ];


    public optionsRight: IOption[] = [
        {
            type: OptionType.Text,
            label: "Max Parallel Downloads",
            valuePath: ["lftp", "num_max_parallel_downloads"],
            description: "Maximum number of concurrent downloads.\n" +
                         "Corresponds to the 'cmd:queue-parallel' setting in Lftp."
        },
        {
            type: OptionType.Text,
            label: "Max Total Connections",
            valuePath: ["lftp", "num_max_total_connections"],
            description: "Maximum number of connections across all downloads.\n" +
                         "Corresponds to the 'net:connection-limit' setting in Lftp."
        },
        {
            type: OptionType.Text,
            label: "Max Connections Per File (For File Download)",
            valuePath: ["lftp", "num_max_connections_per_root_file"],
            description: "Number of connections for a single-file download.\n" +
                         "Corresponds to the 'pget:default-n' setting in Lftp."
        },
        {
            type: OptionType.Text,
            label: "Max Connections Per File (For Directory Download)",
            valuePath: ["lftp", "num_max_connections_per_dir_file"],
            description: "Number of per-file connections for a directory download.\n" +
                         "Corresponds to the 'mirror:use-pget-n' setting in Lftp."
        },
        {
            type: OptionType.Text,
            label: "Max Parallel Files (For Directory Download)",
            valuePath: ["lftp", "num_max_parallel_files_per_download"],
            description: "Maximum number of files to fetch in parallel for a single directory download.\n" +
                         "Corresponds to the 'mirror:parallel-transfer-count' setting in Lftp."
        },
        {
            type: OptionType.Text,
            label: "Web GUI Port",
            valuePath: ["web", "port"],
            description: null
        },
        {
            type: OptionType.Checkbox,
            label: "Enable Debug",
            valuePath: ["general", "debug"],
            description: "Enables debug logging."
        },
    ];

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

export interface IOption {
    type: OptionType;
    label: string;
    valuePath: [string, string];
    description: string;
}
