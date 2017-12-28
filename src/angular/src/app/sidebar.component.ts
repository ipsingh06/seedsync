import {Component, OnInit} from "@angular/core";

import {ROUTE_INFOS} from "./routes";
import {ServerStatusService} from "./other/server-status.service";
import {ServerStatus} from "./other/server-status";
import {ServerCommandService} from "./other/server-command.service";
import {LoggerService} from "./common/logger.service";

@Component({
    selector: "app-sidebar",
    templateUrl: "./sidebar.component.html",
    styleUrls: ["./sidebar.component.scss"]
})

export class SidebarComponent implements OnInit {
    routeInfos = ROUTE_INFOS;

    public commandsEnabled: boolean;

    constructor(private _logger: LoggerService,
                private _statusService: ServerStatusService,
                private _commandService: ServerCommandService) {
        this.commandsEnabled = false;
    }

    // noinspection JSUnusedGlobalSymbols
    ngOnInit() {
        this._statusService.status.subscribe({
            next: (status: ServerStatus) => {
                this.commandsEnabled = status.connected;
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
