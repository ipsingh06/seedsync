import { Component, ChangeDetectionStrategy, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';

import { LoggerService } from '../../services/utils/logger.service';
import { ConfigService } from '../../services/settings/config.service';
import { Config } from '../../services/settings/config';
import { Notification } from '../../services/utils/notification';
import { Localization } from '../../common/localization';
import { NotificationService } from '../../services/utils/notification.service';
import { ServerCommandService } from '../../services/server/server-command.service';
import { ConnectedService } from '../../services/utils/connected.service';
import { StreamServiceRegistry } from '../../services/base/stream-service.registry';
import { OptionComponent, OptionType } from './option.component';
import { ClickStopPropagationDirective } from '../../common/click-stop-propagation.directive';

interface IOption {
    type: OptionType;
    label: string;
    valuePath: [string, string];
    description: string | null;
}

interface IOptionsContext {
    header: string;
    id: string;
    options: IOption[];
}

@Component({
    selector: 'app-settings-page',
    standalone: true,
    imports: [CommonModule, OptionComponent, ClickStopPropagationDirective],
    templateUrl: './settings-page.component.html',
    styleUrl: './settings-page.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class SettingsPageComponent implements OnInit {
    public OPTIONS_CONTEXT_SERVER: IOptionsContext = {
        header: 'Server',
        id: 'server',
        options: [
            { type: OptionType.Text, label: 'Server Address', valuePath: ['lftp', 'remote_address'], description: null },
            { type: OptionType.Text, label: 'Server User', valuePath: ['lftp', 'remote_username'], description: null },
            { type: OptionType.Password, label: 'Server Password', valuePath: ['lftp', 'remote_password'], description: null },
            { type: OptionType.Checkbox, label: 'Use password-less key-based authentication', valuePath: ['lftp', 'use_ssh_key'], description: null },
            { type: OptionType.Text, label: 'Server Directory', valuePath: ['lftp', 'remote_path'], description: 'Path to your files on the remote server' },
            { type: OptionType.Text, label: 'Local Directory', valuePath: ['lftp', 'local_path'], description: 'Downloaded files are placed here' },
            { type: OptionType.Text, label: 'Remote SSH Port', valuePath: ['lftp', 'remote_port'], description: null },
        ]
    };

    public OPTIONS_CONTEXT_AUTOQUEUE: IOptionsContext = {
        header: 'AutoQueue',
        id: 'autoqueue',
        options: [
            { type: OptionType.Checkbox, label: 'Enable AutoQueue', valuePath: ['autoqueue', 'enabled'], description: null },
            { type: OptionType.Checkbox, label: 'Restrict to patterns', valuePath: ['autoqueue', 'patterns_only'], description: 'Only autoqueue files that match a pattern' },
            { type: OptionType.Checkbox, label: 'Enable auto extraction', valuePath: ['autoqueue', 'auto_extract'], description: 'Automatically extract files' },
        ]
    };

    public OPTIONS_CONTEXT_CONNECTIONS: IOptionsContext = {
        header: 'Connections',
        id: 'connections',
        options: [
            { type: OptionType.Text, label: 'Max Parallel Downloads', valuePath: ['lftp', 'num_max_parallel_downloads'], description: 'How many items download in parallel' },
            { type: OptionType.Text, label: 'Max Total Connections', valuePath: ['lftp', 'num_max_total_connections'], description: 'Maximum number of connections' },
        ]
    };

    public config: Observable<Config | null>;
    public commandsEnabled = false;

    private connectedService: ConnectedService;
    private configRestartNotif: Notification;
    private badValueNotifs = new Map<string, Notification>();

    private logger = inject(LoggerService);
    private streamServiceRegistry = inject(StreamServiceRegistry);
    private configService = inject(ConfigService);
    private notifService = inject(NotificationService);
    private commandService = inject(ServerCommandService);

    constructor() {
        this.connectedService = this.streamServiceRegistry.connectedService;
        this.config = this.configService.config;
        this.configRestartNotif = Notification.info(Localization.Notification.CONFIG_RESTART, false);
    }

    ngOnInit(): void {
        this.connectedService.connected.subscribe({
            next: (connected: boolean) => {
                if (!connected) {
                    this.notifService.hide(this.configRestartNotif);
                }
                this.commandsEnabled = connected;
            }
        });

        // Initialize services
        this.configService.onInit();
    }

    onSetConfig(section: string, option: string, value: unknown): void {
        this.configService.set(section, option, value).subscribe({
            next: reaction => {
                const notifKey = section + '.' + option;
                if (reaction.success) {
                    this.logger.info(reaction.data);

                    if (this.badValueNotifs.has(notifKey)) {
                        this.notifService.hide(this.badValueNotifs.get(notifKey)!);
                        this.badValueNotifs.delete(notifKey);
                    }

                    this.notifService.show(this.configRestartNotif);
                } else {
                    const notif = Notification.danger(reaction.errorMessage ?? 'Error', true);
                    if (this.badValueNotifs.has(notifKey)) {
                        this.notifService.hide(this.badValueNotifs.get(notifKey)!);
                    }
                    this.notifService.show(notif);
                    this.badValueNotifs.set(notifKey, notif);

                    this.logger.error(reaction.errorMessage);
                }
            }
        });
    }

    onCommandRestart(): void {
        this.commandService.restart().subscribe({
            next: reaction => {
                if (reaction.success) {
                    this.logger.info(reaction.data);
                } else {
                    this.logger.error(reaction.errorMessage);
                }
            }
        });
    }

    getConfigValue(config: Config | null, section: string, option: string): unknown {
        if (!config) return null;
        const configData = config as unknown as Record<string, Record<string, unknown>>;
        const sectionObj = configData[section];
        return sectionObj && typeof sectionObj === 'object' ? sectionObj[option] : null;
    }
}
