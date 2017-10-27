import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {HttpClientModule} from '@angular/common/http';
import {FormsModule}   from '@angular/forms';

import {AppComponent} from './app.component';
import {environment}    from '../environments/environment';
import {LoggerService} from "./common/logger.service"
import {FileListComponent} from "./file-list.component"
import {FileComponent} from "./file.component"
import {ModelFileService} from "./model/model-file.service"
import {ViewFileService} from "./view/view-file.service";
import {FileSizePipe} from "./common/file-size.pipe";
import {EtaPipe} from "./common/eta.pipe";
import {CapitalizePipe} from "./common/capitalize.pipe";
import {ClickStopPropagation} from "./common/click-stop-propagation.directive";
import {FileListFilterComponent} from "./file-list-filter.component";
import {ViewFileFilterService} from "./view/view-file-filter.service";

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
        HttpClientModule,
        FormsModule
    ],
    providers: [LoggerService,
                ModelFileService,
                ViewFileService,
                ViewFileFilterService],
    bootstrap: [AppComponent]
})
export class AppModule {
    constructor(private logger: LoggerService) {
        this.logger.level = environment.logger.level;
    }
}
