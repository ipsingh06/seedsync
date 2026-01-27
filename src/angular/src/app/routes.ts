import { Routes } from '@angular/router';
import { Type } from '@angular/core';

export interface RouteInfo {
    path: string;
    name: string;
    icon: string;
    component: Type<unknown>;
}

// Lazy loaded route components - defined here for sidebar navigation
export const ROUTE_INFOS: readonly RouteInfo[] = Object.freeze([
    {
        path: 'dashboard',
        name: 'Dashboard',
        icon: 'assets/icons/dashboard.svg',
        component: null as unknown as Type<unknown> // Will be lazy loaded
    },
    {
        path: 'settings',
        name: 'Settings',
        icon: 'assets/icons/settings.svg',
        component: null as unknown as Type<unknown>
    },
    {
        path: 'autoqueue',
        name: 'AutoQueue',
        icon: 'assets/icons/autoqueue.svg',
        component: null as unknown as Type<unknown>
    },
    {
        path: 'logs',
        name: 'Logs',
        icon: 'assets/icons/logs.svg',
        component: null as unknown as Type<unknown>
    },
    {
        path: 'about',
        name: 'About',
        icon: 'assets/icons/about.svg',
        component: null as unknown as Type<unknown>
    }
]);

export const ROUTES: Routes = [
    {
        path: '',
        redirectTo: '/dashboard',
        pathMatch: 'full'
    },
    {
        path: 'dashboard',
        loadComponent: () => import('./pages/files/files-page.component').then(m => m.FilesPageComponent)
    },
    {
        path: 'settings',
        loadComponent: () => import('./pages/settings/settings-page.component').then(m => m.SettingsPageComponent)
    },
    {
        path: 'autoqueue',
        loadComponent: () => import('./pages/autoqueue/autoqueue-page.component').then(m => m.AutoQueuePageComponent)
    },
    {
        path: 'logs',
        loadComponent: () => import('./pages/logs/logs-page.component').then(m => m.LogsPageComponent)
    },
    {
        path: 'about',
        loadComponent: () => import('./pages/about/about-page.component').then(m => m.AboutPageComponent)
    }
];
