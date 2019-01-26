import {ChangeDetectionStrategy, Component} from "@angular/core";
import {Observable} from "rxjs/Observable";

import {ViewFileFilterService} from "../../services/files/view-file-filter.service";
import {ViewFileFilter} from "../../services/files/view-file-filter";
import {ViewFileOptionsService} from "../../services/files/view-file-options.service";
import {ViewFileOptions} from "../../services/files/view-file-options";
import {ViewFile} from "../../services/files/view-file";

@Component({
    selector: "app-file-options",
    providers: [],
    templateUrl: "./file-options.component.html",
    styleUrls: ["./file-options.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FileOptionsComponent {
    public filter: Observable<ViewFileFilter>;
    public options: Observable<ViewFileOptions>;

    public filterName = "";

    private _latestOptions: ViewFileOptions;

    constructor(private viewFileFilterService: ViewFileFilterService,
                private viewFileOptionsService: ViewFileOptionsService) {
        this.filter = this.viewFileFilterService.filter;
        this.options = this.viewFileOptionsService.options;

        // Keep the latest options for toggle behaviour implementation
        this.viewFileOptionsService.options.subscribe(options => this._latestOptions = options);
    }

    onFilterAll() {
        this.viewFileFilterService.filterStatus(null);
    }

    onFilterExtracted() {
        this.viewFileFilterService.filterStatus(ViewFile.Status.EXTRACTED);
    }

    onFilterExtracting() {
        this.viewFileFilterService.filterStatus(ViewFile.Status.EXTRACTING);
    }

    onFilterDownloaded() {
        this.viewFileFilterService.filterStatus(ViewFile.Status.DOWNLOADED);
    }

    onFilterDownloading() {
        this.viewFileFilterService.filterStatus(ViewFile.Status.DOWNLOADING);
    }

    onFilterQueued() {
        this.viewFileFilterService.filterStatus(ViewFile.Status.QUEUED);
    }

    onFilterStopped() {
        this.viewFileFilterService.filterStatus(ViewFile.Status.STOPPED);
    }

    // noinspection JSUnusedGlobalSymbols
    onFilterDefault() {
        this.viewFileFilterService.filterStatus(ViewFile.Status.DEFAULT);
    }

    onFilterByName(name: string) {
        this.filterName = name;
        this.viewFileFilterService.filterName(this.filterName);
    }

    onToggleShowDetails(){
        this.viewFileOptionsService.setShowDetails(!this._latestOptions.showDetails);
    }
}
