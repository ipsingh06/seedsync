import {Component} from '@angular/core';
import {ROUTE_INFOS} from "./routes";

@Component({
    selector: 'sidebar',
    templateUrl: './sidebar.component.html',
    styleUrls: ['./sidebar.component.scss']
})

export class SidebarComponent {
    routeInfos = ROUTE_INFOS;
}
