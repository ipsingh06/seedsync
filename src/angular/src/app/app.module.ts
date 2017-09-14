import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppComponent} from './app.component';
import {FileListComponent} from "./file-list.component"
import {ModelFileService} from "./model-file.service"
import {ViewFileService} from "./view-file.service";

@NgModule({
    declarations: [
        AppComponent,
        FileListComponent
    ],
    imports: [
        BrowserModule
    ],
    providers: [ModelFileService,
                ViewFileService],
    bootstrap: [AppComponent]
})
export class AppModule {
}
