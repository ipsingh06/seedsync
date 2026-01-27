import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, RouteReuseStrategy } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';

import { ROUTES } from './routes';
import { CachedReuseStrategy } from './common/cached-reuse-strategy';

export const appConfig: ApplicationConfig = {
    providers: [
        provideZoneChangeDetection({ eventCoalescing: true }),
        provideRouter(ROUTES),
        provideHttpClient(),
        provideAnimations(),
        { provide: RouteReuseStrategy, useClass: CachedReuseStrategy }
    ]
};
