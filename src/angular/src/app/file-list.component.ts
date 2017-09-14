import {Component} from '@angular/core';
import {Observable} from "rxjs/Observable";

import {List} from "immutable";

import {ViewFileService} from "./view-file.service";
import {ViewFile} from "./view-file";

@Component({
    selector: 'file-list',
    providers: [],
    templateUrl: './file-list.component.html',
    styleUrls: ['./file-list.component.css']
})
export class FileListComponent {
    public files: Observable<List<ViewFile>>;

    constructor(private viewFileService: ViewFileService) {
        this.files = viewFileService.files;
    }
}
