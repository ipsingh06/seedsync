import {BrowserModule} from "@angular/platform-browser";
import {NgModule} from "@angular/core";
import {HttpClientModule} from "@angular/common/http";
import {FormsModule} from "@angular/forms";
import {RouteReuseStrategy, RouterModule} from "@angular/router";

import {AppComponent} from "./pages/main/app.component";
import {environment} from "../environments/environment";
import {LoggerService} from "./services/utils/logger.service";
import {FileListComponent} from "./pages/files/file-list.component";
import {FileComponent} from "./pages/files/file.component";
import {ModelFileService} from "./services/files/model-file.service";
import {ViewFileService} from "./services/files/view-file.service";
import {FileSizePipe} from "./common/file-size.pipe";
import {EtaPipe} from "./common/eta.pipe";
import {CapitalizePipe} from "./common/capitalize.pipe";
import {ClickStopPropagationDirective} from "./common/click-stop-propagation.directive";
import {FileListFilterComponent} from "./pages/files/file-list-filter.component";
import {ViewFileFilterService} from "./services/files/view-file-filter.service";
import {FilesPageComponent} from "./pages/files/files-page.component";
import {HeaderComponent} from "./pages/main/header.component";
import {SidebarComponent} from "./pages/main/sidebar.component";
import {SettingsPageComponent} from "./pages/settings/settings-page.component";
import {ServerStatusService} from "./services/server/server-status.service";
import {ConfigServiceProvider} from "./services/settings/config.service";
import {OptionComponent} from "./pages/settings/option.component";
import {NotificationService} from "./services/utils/notification.service";
import {ServerCommandServiceProvider} from "./services/server/server-command.service";
import {AutoQueuePageComponent} from "./pages/autoqueue/autoqueue-page.component";
import {AutoQueueServiceProvider} from "./services/autoqueue/autoqueue.service";
import {CachedReuseStrategy} from "./common/cached-reuse-strategy";
import {ConnectedService} from "./services/utils/connected.service";
import {RestService} from "./services/utils/rest.service";
import {StreamDispatchService, StreamServiceRegistryProvider} from "./services/base/stream-service.registry";
import {LogsPageComponent} from "./pages/logs/logs-page.component";
import {LogService} from "./services/logs/log.service";
import {AboutPageComponent} from "./pages/about/about-page.component";
import {ROUTES} from "./routes";

@NgModule({
    declarations: [
        FileSizePipe,
        EtaPipe,
        CapitalizePipe,
        ClickStopPropagationDirective,
        AppComponent,
        FileListComponent,
        FileComponent,
        FileListFilterComponent,
        FilesPageComponent,
        HeaderComponent,
        SidebarComponent,
        SettingsPageComponent,
        OptionComponent,
        AutoQueuePageComponent,
        LogsPageComponent,
        AboutPageComponent
    ],
    imports: [
        BrowserModule,
        HttpClientModule,
        FormsModule,
        RouterModule.forRoot(ROUTES)
    ],
    providers: [
        {provide: RouteReuseStrategy, useClass: CachedReuseStrategy},
        LoggerService,
        NotificationService,
        RestService,
        ViewFileService,
        ViewFileFilterService,

        StreamDispatchService,
        StreamServiceRegistryProvider,
        ServerStatusService,
        ModelFileService,
        ConnectedService,
        LogService,

        AutoQueueServiceProvider,
        ConfigServiceProvider,
        ServerCommandServiceProvider,
    ],
    bootstrap: [AppComponent]
})
export class AppModule {
    constructor(private logger: LoggerService) {
        this.logger.level = environment.logger.level;
    }
}
