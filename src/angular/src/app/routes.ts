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
        icon: "glyphicon-dashboard",
        component: FilesPageComponent
    },
    {
        path: "settings",
        name: "Settings",
        icon: "glyphicon-cog",
        component: SettingsPageComponent
    },
    {
        path: "autoqueue",
        name: "AutoQueue",
        icon: "glyphicon-list",
        component: AutoQueuePageComponent
    },
    {
        path: "logs",
        name: "Logs",
        icon: "glyphicon-list-alt",
        component: LogsPageComponent
    },
    {
        path: "about",
        name: "About",
        icon: "glyphicon-heart",
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
