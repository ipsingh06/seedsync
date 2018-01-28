import {Routes} from "@angular/router";

import * as Immutable from "immutable";

import {FilesPageComponent} from "./pages/files/files-page.component";
import {SettingsPageComponent} from "./pages/settings/settings-page.component";
import {AutoQueuePageComponent} from "./pages/autoqueue/autoqueue-page.component";
import {LogsPageComponent} from "./pages/logs/logs-page.component";
import {AboutPageComponent} from "./pages/about/about-page.component";

export interface RouteInfo {
    path: string;
    name: string;
    icon: string;
    component: any;
}

export const ROUTE_INFOS: Immutable.List<RouteInfo> = Immutable.List([
    {
        path: "dashboard",
        name: "Dashboard",
        icon: "assets/icons/dashboard.svg",
        component: FilesPageComponent
    },
    {
        path: "settings",
        name: "Settings",
        icon: "assets/icons/settings.svg",
        component: SettingsPageComponent
    },
    {
        path: "autoqueue",
        name: "AutoQueue",
        icon: "assets/icons/autoqueue.svg",
        component: AutoQueuePageComponent
    },
    {
        path: "logs",
        name: "Logs",
        icon: "assets/icons/logs.svg",
        component: LogsPageComponent
    },
    {
        path: "about",
        name: "About",
        icon: "assets/icons/about.svg",
        component: AboutPageComponent
    }
]);

export const ROUTES: Routes = [
    {
        path: "",
        redirectTo: "/dashboard",
        pathMatch: "full"
    },
    {
        path: "dashboard",
        component: FilesPageComponent
    },
    {
        path: "settings",
        component: SettingsPageComponent
    },
    {
        path: "autoqueue",
        component: AutoQueuePageComponent
    },
    {
        path: "logs",
        component: LogsPageComponent
    },
    {
        path: "about",
        component: AboutPageComponent
    }
];
