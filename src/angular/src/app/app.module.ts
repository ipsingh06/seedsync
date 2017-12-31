import {BrowserModule} from "@angular/platform-browser";
import {NgModule} from "@angular/core";
import {HttpClientModule} from "@angular/common/http";
import {FormsModule} from "@angular/forms";
import {RouteReuseStrategy, RouterModule} from "@angular/router";

import {AppComponent} from "./app.component";
import {environment} from "../environments/environment";
import {LoggerService} from "./common/logger.service";
import {FileListComponent} from "./pages/files/file-list.component";
import {FileComponent} from "./pages/files/file.component";
import {ModelFileService} from "./model/model-file.service";
import {ViewFileService} from "./view/view-file.service";
import {FileSizePipe} from "./common/file-size.pipe";
import {EtaPipe} from "./common/eta.pipe";
import {CapitalizePipe} from "./common/capitalize.pipe";
import {ClickStopPropagationDirective} from "./common/click-stop-propagation.directive";
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
import {ServerCommandServiceProvider} from "./other/server-command.service";
import {AutoQueuePageComponent} from "./pages/autoqueue/autoqueue-page.component";
import {AutoQueueServiceProvider} from "./other/autoqueue.service";
import {CachedReuseStrategy} from "./common/cached-reuse-strategy";
import {ConnectedService} from "./other/connected.service";
import {RestService} from "./other/rest.service";
import {StreamDispatchService, StreamServiceRegistryProvider} from "./common/stream-service.registry";

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
        AutoQueuePageComponent
    ],
    imports: [
        BrowserModule,
        HttpClientModule,
        FormsModule,
        RouterModule.forRoot([
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
            }
        ])
    ],
    providers: [
        {provide: RouteReuseStrategy, useClass: CachedReuseStrategy},
        LoggerService,
        NotificationService,
        ViewFileService,
        ViewFileFilterService,

        StreamDispatchService,
        StreamServiceRegistryProvider,
        ServerStatusService,
        ModelFileService,
        ConnectedService,
        RestService,

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
