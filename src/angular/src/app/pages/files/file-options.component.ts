import {ChangeDetectionStrategy, ChangeDetectorRef, Component, OnInit} from "@angular/core";
import {Observable} from "rxjs/Observable";

import * as Immutable from "immutable";

import {ViewFileOptionsService} from "../../services/files/view-file-options.service";
import {ViewFileOptions} from "../../services/files/view-file-options";
import {ViewFile} from "../../services/files/view-file";
import {ViewFileService} from "../../services/files/view-file.service";

@Component({
    selector: "app-file-options",
    providers: [],
    templateUrl: "./file-options.component.html",
    styleUrls: ["./file-options.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FileOptionsComponent implements OnInit {
    public ViewFile = ViewFile;
    public ViewFileOptions = ViewFileOptions;

    public options: Observable<ViewFileOptions>;

    // These track which status filters are enabled
    public isExtractedStatusEnabled = false;
    public isExtractingStatusEnabled = false;
    public isDownloadedStatusEnabled = false;
    public isDownloadingStatusEnabled = false;
    public isQueuedStatusEnabled = false;
    public isStoppedStatusEnabled = false;

    private _latestOptions: ViewFileOptions;

    constructor(private _changeDetector: ChangeDetectorRef,
                private viewFileOptionsService: ViewFileOptionsService,
                private _viewFileService: ViewFileService) {
        this.options = this.viewFileOptionsService.options;
    }

    ngOnInit() {
        // Use the unfiltered files to enable/disable the filter status buttons
        this._viewFileService.files.subscribe(files => {
            this.isExtractedStatusEnabled = FileOptionsComponent.isStatusEnabled(
                files, ViewFile.Status.EXTRACTED
            );
            this.isExtractingStatusEnabled = FileOptionsComponent.isStatusEnabled(
                files, ViewFile.Status.EXTRACTING
            );
            this.isDownloadedStatusEnabled = FileOptionsComponent.isStatusEnabled(
                files, ViewFile.Status.DOWNLOADED
            );
            this.isDownloadingStatusEnabled = FileOptionsComponent.isStatusEnabled(
                files, ViewFile.Status.DOWNLOADING
            );
            this.isQueuedStatusEnabled = FileOptionsComponent.isStatusEnabled(
                files, ViewFile.Status.QUEUED
            );
            this.isStoppedStatusEnabled = FileOptionsComponent.isStatusEnabled(
                files, ViewFile.Status.STOPPED
            );
            this._changeDetector.detectChanges();
        });

        // Keep the latest options for toggle behaviour implementation
        this.viewFileOptionsService.options.subscribe(options => this._latestOptions = options);
    }

    onFilterByName(name: string) {
        this.viewFileOptionsService.setNameFilter(name);
    }

    onFilterByStatus(status: ViewFile.Status) {
        this.viewFileOptionsService.setSelectedStatusFilter(status);
    }

    onSort(sortMethod: ViewFileOptions.SortMethod) {
        this.viewFileOptionsService.setSortMethod(sortMethod);
    }

    onToggleShowDetails(){
        this.viewFileOptionsService.setShowDetails(!this._latestOptions.showDetails);
    }

    private static isStatusEnabled(files: Immutable.List<ViewFile>, status: ViewFile.Status) {
        return files.findIndex(f => f.status === status) >= 0;
    }
}
