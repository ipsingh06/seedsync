import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';

import { ROUTE_INFOS } from '../../routes';
import { ServerCommandService } from '../../services/server/server-command.service';
import { LoggerService } from '../../services/utils/logger.service';
import { ConnectedService } from '../../services/utils/connected.service';
import { StreamServiceRegistry } from '../../services/base/stream-service.registry';

@Component({
    selector: 'app-sidebar',
    standalone: true,
    imports: [CommonModule, RouterLink, RouterLinkActive],
    templateUrl: './sidebar.component.html',
    styleUrl: './sidebar.component.scss'
})
export class SidebarComponent implements OnInit {
    routeInfos = ROUTE_INFOS;

    public commandsEnabled = false;

    private connectedService: ConnectedService;

    private logger = inject(LoggerService);
    private streamServiceRegistry = inject(StreamServiceRegistry);
    private commandService = inject(ServerCommandService);

    constructor() {
        this.connectedService = this.streamServiceRegistry.connectedService;
    }

    ngOnInit(): void {
        this.connectedService.connected.subscribe({
            next: (connected: boolean) => {
                this.commandsEnabled = connected;
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
}
