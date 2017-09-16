import {Component, ChangeDetectionStrategy} from '@angular/core';
import {Observable} from "rxjs/Observable";

import {List} from "immutable";

import {ViewFileService} from "./view-file.service";
import {ViewFile} from "./view-file";

@Component({
    selector: 'file-list',
    providers: [],
    templateUrl: './file-list.component.html',
    styleUrls: ['./file-list.component.css'],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FileListComponent {
    public files: Observable<List<ViewFile>>;
    public identify = FileListComponent.identify;

    constructor(private viewFileService: ViewFileService) {
        this.files = viewFileService.files;
    }

    /**
     * Used for trackBy in ngFor
     * @param index
     * @param item
     */
    static identify(index: number, item: ViewFile): string {
        return item.name
    }
}
