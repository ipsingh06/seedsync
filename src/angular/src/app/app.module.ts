import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {HttpClientModule} from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {RouterModule} from '@angular/router';

import {AppComponent} from './app.component';
import {environment}    from '../environments/environment';
import {LoggerService} from "./common/logger.service"
import {FileListComponent} from "./pages/files/file-list.component"
import {FileComponent} from "./pages/files/file.component"
import {ModelFileService} from "./model/model-file.service"
import {ViewFileService} from "./view/view-file.service";
import {FileSizePipe} from "./common/file-size.pipe";
import {EtaPipe} from "./common/eta.pipe";
import {CapitalizePipe} from "./common/capitalize.pipe";
import {ClickStopPropagation} from "./common/click-stop-propagation.directive";
import {FileListFilterComponent} from "./pages/files/file-list-filter.component";
import {ViewFileFilterService} from "./view/view-file-filter.service";
import {FilesPageComponent} from "./pages/files/files-page.component";
import {HeaderComponent} from "./header.component";
import {SidebarComponent} from "./sidebar.component";
import {SettingsPageComponent} from "./pages/settings/settings-page.component";
import {ServerStatusService} from "./other/server-status.service";
import {ConfigServiceProvider} from "./other/config.service";
import {OptionComponent} from "./pages/settings/option.component";
import {NotificationService} from "./other/notification.service";

@NgModule({
    declarations: [
        FileSizePipe,
        EtaPipe,
        CapitalizePipe,
        ClickStopPropagation,
        AppComponent,
        FileListComponent,
        FileComponent,
        FileListFilterComponent,
        FilesPageComponent,
        HeaderComponent,
        SidebarComponent,
        SettingsPageComponent,
        OptionComponent
    ],
    imports: [
        BrowserModule,
        HttpClientModule,
        FormsModule,
        RouterModule.forRoot([
            {
                path: '',
                redirectTo: '/dashboard',
                pathMatch: 'full'
            },
            {
                path: 'dashboard',
                component: FilesPageComponent
            },
            {
                path: 'settings',
                component: SettingsPageComponent
            }
        ])
    ],
    providers: [LoggerService,
                ModelFileService,
                ViewFileService,
                ViewFileFilterService,
                ServerStatusService,
                ConfigServiceProvider,
                NotificationService],
    bootstrap: [AppComponent]
})
export class AppModule {
    constructor(private logger: LoggerService) {
        this.logger.level = environment.logger.level;
    }
}
