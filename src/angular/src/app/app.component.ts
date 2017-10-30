import {Component} from '@angular/core';
import {Router} from '@angular/router';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent {
    showSidebar: boolean = false;

    constructor(router:Router) {
        // Close the sidebar on navigation
        router.events.subscribe(() => {this.showSidebar=false});
    }

    title = 'app';
}
