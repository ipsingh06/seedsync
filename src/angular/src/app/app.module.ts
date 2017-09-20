import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppComponent} from './app.component';
import {environment}    from '../environments/environment';
import {LoggerService} from "./logger.service"
import {FileListComponent} from "./file-list.component"
import {FileComponent} from "./file.component"
import {ModelFileService} from "./model-file.service"
import {ViewFileService} from "./view-file.service";
import {FileSizePipe} from "./file-size.pipe";
import {EtaPipe} from "./eta.pipe";

@NgModule({
    declarations: [
        FileSizePipe,
        EtaPipe,
        AppComponent,
        FileListComponent,
        FileComponent
    ],
    imports: [
        BrowserModule
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
