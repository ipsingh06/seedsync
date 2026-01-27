import { Component, ElementRef, ViewChild, OnInit, AfterViewInit, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';

import { ROUTE_INFOS, RouteInfo } from './routes';
import { DomService } from './services/utils/dom.service';
import { HeaderComponent } from './pages/main/header.component';
import { SidebarComponent } from './pages/main/sidebar.component';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterOutlet, HeaderComponent, SidebarComponent],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit, AfterViewInit {
    @ViewChild('topHeader') topHeader!: ElementRef<HTMLDivElement>;

    showSidebar = false;
    activeRoute: RouteInfo | undefined;

    private router = inject(Router);
    private domService = inject(DomService);

    constructor() {
        // Navigation listener
        //    Close the sidebar
        //    Store the active route
        this.router.events.subscribe(() => {
            this.showSidebar = false;
            this.activeRoute = ROUTE_INFOS.find(value => '/' + value.path === this.router.url);
        });
    }

    ngOnInit(): void {
        // Scroll to top on route changes
        this.router.events.subscribe((evt) => {
            if (!(evt instanceof NavigationEnd)) {
                return;
            }
            window.scrollTo(0, 0);
        });
    }

    ngAfterViewInit(): void {
        // Use ResizeObserver instead of css-element-queries
        if (this.topHeader?.nativeElement) {
            const resizeObserver = new ResizeObserver(() => {
                this.domService.setHeaderHeight(this.topHeader.nativeElement.clientHeight);
            });
            resizeObserver.observe(this.topHeader.nativeElement);
        }
    }
}
