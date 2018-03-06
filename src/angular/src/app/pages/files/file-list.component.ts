import {Component, ChangeDetectionStrategy} from "@angular/core";
import {Observable} from "rxjs/Observable";

import {List} from "immutable";
import {Modal} from 'ngx-modialog/plugins/bootstrap';

import {ViewFileService} from "../../services/files/view-file.service";
import {ViewFile} from "../../services/files/view-file";
import {LoggerService} from "../../services/utils/logger.service";
import {Localization} from "../../common/localization";

@Component({
    selector: "app-file-list",
    providers: [],
    templateUrl: "./file-list.component.html",
    styleUrls: ["./file-list.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FileListComponent {
    public files: Observable<List<ViewFile>>;
    public identify = FileListComponent.identify;

    constructor(private _logger: LoggerService,
                private viewFileService: ViewFileService,
                private modal: Modal) {
        this.files = viewFileService.filteredFiles;
    }

    showDeleteConfirmation(title: string, message: string, callback: () => void) {
        const dialogRef = this.modal.confirm()
            .title(title)
            .okBtn('Delete')
            .okBtnClass('btn btn-danger')
            .cancelBtn('Cancel')
            .cancelBtnClass('btn btn-secondary')
            .isBlocking(false)
            .showClose(false)
            .body(message)
            .open();

        dialogRef.then( dialogRef => {
           dialogRef.result.then(
               () => {callback()},
               () => {return}
           );
        });
    }

    // noinspection JSUnusedLocalSymbols
    /**
     * Used for trackBy in ngFor
     * @param index
     * @param item
     */
    static identify(index: number, item: ViewFile): string {
        return item.name;
    }

    onSelect(file: ViewFile): void {
        if (file.isSelected) {
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

    onExtract(file: ViewFile) {
        this.viewFileService.extract(file).subscribe(data => {
            this._logger.info(data);
        });
    }

    onDeleteLocal(file: ViewFile) {
        this.showDeleteConfirmation(
            Localization.Modal.DELETE_LOCAL_TITLE,
            Localization.Modal.DELETE_LOCAL_MESSAGE(file.name),
            () => {
                this.viewFileService.deleteLocal(file).subscribe(data => {
                    this._logger.info(data);
                });
            }
        );
    }

    onDeleteRemote(file: ViewFile) {
        this.showDeleteConfirmation(
            Localization.Modal.DELETE_REMOTE_TITLE,
            Localization.Modal.DELETE_REMOTE_MESSAGE(file.name),
            () => {
                this.viewFileService.deleteRemote(file).subscribe(data => {
                    this._logger.info(data);
                });
            }
        );
    }
}
