import {AfterViewInit, Component, ElementRef, OnInit, ViewChild} from "@angular/core";
import {NavigationEnd, Router} from "@angular/router";
import {ROUTE_INFOS, RouteInfo} from "../../routes";

import {ElementQueries, ResizeSensor} from "css-element-queries";
import {DomService} from "../../services/utils/dom.service";

@Component({
    selector: "app-root",
    templateUrl: "./app.component.html",
    styleUrls: ["./app.component.scss"]
})
export class AppComponent implements OnInit, AfterViewInit {
    @ViewChild("topHeader") topHeader: ElementRef;

    showSidebar = false;
    activeRoute: RouteInfo;

    constructor(private router: Router,
                private _domService: DomService) {
        // Navigation listener
        //    Close the sidebar
        //    Store the active route
        router.events.subscribe(() => {
            this.showSidebar = false;
            this.activeRoute = ROUTE_INFOS.find(value => "/" + value.path === router.url);
        });
    }

    ngOnInit() {
        // Scroll to top on route changes
        this.router.events.subscribe((evt) => {
            if (!(evt instanceof NavigationEnd)) {
                return;
            }
            window.scrollTo(0, 0);
        });
    }

    ngAfterViewInit() {
        ElementQueries.listen();
        ElementQueries.init();
        // noinspection TsLint
        new ResizeSensor(this.topHeader.nativeElement, () => {
            this._domService.setHeaderHeight(this.topHeader.nativeElement.clientHeight);
        });
    }

    title = "app";
}
