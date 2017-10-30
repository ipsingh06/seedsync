import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {ROUTE_INFOS, RouteInfo} from "./routes";

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent {
    showSidebar: boolean = false;
    activeRoute: RouteInfo;

    constructor(router:Router) {
        // Navigation listener
        //    Close the sidebar
        //    Store the active route
        router.events.subscribe(() => {
            this.showSidebar = false;
            this.activeRoute = ROUTE_INFOS.find(value => value.path == router.url);
        });
    }

    title = 'app';
}
