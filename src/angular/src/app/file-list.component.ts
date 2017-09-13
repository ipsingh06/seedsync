import {Component} from '@angular/core';

import {ModelFileService} from "./model-file.service";

@Component({
    selector: 'file-list',
    providers: [ModelFileService],
    templateUrl: './file-list.component.html',
    styleUrls: ['./file-list.component.css']
})
export class FileListComponent {
    public files;

    constructor(private fileService: ModelFileService) {
        this.files = fileService.files;
    }
}
