import {Component} from '@angular/core';
import {Observable} from "rxjs/Observable";

import {LoggerService} from "./common/logger.service"
import {ServerStatusService} from "./other/server-status.service";
import {ServerStatus} from "./other/server-status";

@Component({
    selector: 'header',
    templateUrl: './header.component.html',
    styleUrls: ['./header.component.scss'],
})

export class HeaderComponent {
    public serverStatus: Observable<ServerStatus>;

    constructor(private _logger: LoggerService,
                private serverStatusService: ServerStatusService) {
        this.serverStatus = this.serverStatusService.status;
    }
}
