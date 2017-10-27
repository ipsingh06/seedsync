import {Component, ChangeDetectionStrategy} from '@angular/core';
import {Observable} from "rxjs/Observable";

import {List} from "immutable";

import {ViewFileService} from "../../view/view-file.service";
import {ViewFile} from "../../view/view-file";
import {LoggerService} from "../../common/logger.service";

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

    constructor(private _logger: LoggerService,
                private viewFileService: ViewFileService) {
        this.files = viewFileService.filteredFiles;
    }

    /**
     * Used for trackBy in ngFor
     * @param index
     * @param item
     */
    static identify(index: number, item: ViewFile): string {
        return item.name
    }

    onSelect(file: ViewFile): void {
        if(file.isSelected) {
            this.viewFileService.unsetSelected();
        } else {
            this.viewFileService.setSelected(file);
        }
    }

    onQueue(file: ViewFile) {
        this.viewFileService.queue(file).subscribe(data => {
            this._logger.info(data);
        });
    }

    onStop(file: ViewFile) {
        this.viewFileService.stop(file).subscribe(data => {
            this._logger.info(data);
        });
    }
}
