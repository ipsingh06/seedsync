import {Component} from '@angular/core';
import {Observable} from "rxjs/Observable";

import {List} from "immutable";

import {ModelFileService} from "./model-file.service"
import {ViewFileService} from "./view-file.service";
import {ViewFile} from "./view-file";

@Component({
    selector: 'file-list',
    providers: [ViewFileService,
                ModelFileService],
    templateUrl: './file-list.component.html',
    styleUrls: ['./file-list.component.css']
})
export class FileListComponent {
    public files: Observable<List<ViewFile>>;

    constructor(private viewFileService: ViewFileService) {
        this.files = viewFileService.files;
    }
}
