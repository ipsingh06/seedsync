import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {HttpClientModule} from '@angular/common/http';

import {AppComponent} from './app.component';
import {environment}    from '../environments/environment';
import {LoggerService} from "./logger.service"
import {FileListComponent} from "./file-list.component"
import {FileComponent} from "./file.component"
import {ModelFileService} from "./model-file.service"
import {ViewFileService} from "./view-file.service";
import {FileSizePipe} from "./file-size.pipe";
import {EtaPipe} from "./eta.pipe";
import {CapitalizePipe} from "./capitalize.pipe";
import {ClickStopPropagation} from "./click-stop-propagation.directive";
import {FileListFilterComponent} from "./file-list-filter.component";

@NgModule({
    declarations: [
        FileSizePipe,
        EtaPipe,
        CapitalizePipe,
        ClickStopPropagation,
        AppComponent,
        FileListComponent,
        FileComponent,
        FileListFilterComponent
    ],
    imports: [
        BrowserModule,
        HttpClientModule
    ],
    providers: [LoggerService,
                ModelFileService,
                ViewFileService],
    bootstrap: [AppComponent]
})
export class AppModule {
    constructor(private logger: LoggerService) {
        this.logger.level = environment.logger.level;
    }
}
