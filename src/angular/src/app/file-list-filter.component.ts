import {Component} from '@angular/core';
import {Observable} from "rxjs/Observable";

import {LoggerService} from "./logger.service"
import {ViewFileService} from "./view-file.service"
import {ViewFile} from "./view-file";

@Component({
    selector: 'file-list-filter',
    providers: [],
    templateUrl: './file-list-filter.component.html',
})

export class FileListFilterComponent {

    constructor(private _logger: LoggerService,
                private viewFileService: ViewFileService) {
    }
}
