import * as Immutable from "immutable";

export interface RouteInfo {
    path: string;
    name: string;
    icon: string;
}

export const ROUTE_INFOS: Immutable.List<RouteInfo> = Immutable.List([
    {
        path: "/dashboard",
        name: "Dashboard",
        icon: "glyphicon-dashboard"
    },
    {
        path: "/settings",
        name: "Settings",
        icon: "glyphicon-cog"
    },
    {
        path: "/autoqueue",
        name: "AutoQueue",
        icon: "glyphicon-list"
    },
    {
        path: "/logs",
        name: "Logs",
        icon: "glyphicon-list-alt"
    },
    {
        path: "/about",
        name: "About",
        icon: "glyphicon-heart"
    }
]);
