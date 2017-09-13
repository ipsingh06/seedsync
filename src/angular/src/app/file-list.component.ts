import {Component} from '@angular/core';

import {FileService} from "./file.service";

@Component({
    selector: 'file-list',
    providers: [FileService],
    templateUrl: './file-list.component.html',
    styleUrls: ['./file-list.component.css']
})
export class FileListComponent {
    public files;

    constructor(private fileService: FileService) {
        this.files = fileService.files;
    }
}
