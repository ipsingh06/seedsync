import { Component, ChangeDetectionStrategy, ChangeDetectorRef, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';

import { ViewFileOptionsService } from '../../services/files/view-file-options.service';
import { ViewFileOptions, ViewFileOptionsSortMethod } from '../../services/files/view-file-options';
import { ViewFile, ViewFileStatus } from '../../services/files/view-file';
import { ViewFileService } from '../../services/files/view-file.service';
import { DomService } from '../../services/utils/dom.service';

@Component({
    selector: 'app-file-options',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './file-options.component.html',
    styleUrl: './file-options.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FileOptionsComponent implements OnInit {
    ViewFileStatus = ViewFileStatus;
    ViewFileOptionsSortMethod = ViewFileOptionsSortMethod;

    public options: Observable<ViewFileOptions>;
    public headerHeight: Observable<number>;

    public isExtractedStatusEnabled = false;
    public isExtractingStatusEnabled = false;
    public isDownloadedStatusEnabled = false;
    public isDownloadingStatusEnabled = false;
    public isQueuedStatusEnabled = false;
    public isStoppedStatusEnabled = false;

    private latestOptions: ViewFileOptions | null = null;

    private changeDetector = inject(ChangeDetectorRef);
    private viewFileOptionsService = inject(ViewFileOptionsService);
    private viewFileService = inject(ViewFileService);
    private domService = inject(DomService);

    constructor() {
        this.options = this.viewFileOptionsService.options;
        this.headerHeight = this.domService.headerHeight;
    }

    ngOnInit(): void {
        this.viewFileService.files.subscribe(files => {
            this.isExtractedStatusEnabled = this.isStatusEnabled(files, ViewFileStatus.EXTRACTED);
            this.isExtractingStatusEnabled = this.isStatusEnabled(files, ViewFileStatus.EXTRACTING);
            this.isDownloadedStatusEnabled = this.isStatusEnabled(files, ViewFileStatus.DOWNLOADED);
            this.isDownloadingStatusEnabled = this.isStatusEnabled(files, ViewFileStatus.DOWNLOADING);
            this.isQueuedStatusEnabled = this.isStatusEnabled(files, ViewFileStatus.QUEUED);
            this.isStoppedStatusEnabled = this.isStatusEnabled(files, ViewFileStatus.STOPPED);
            this.changeDetector.detectChanges();
        });

        this.viewFileOptionsService.options.subscribe(options => this.latestOptions = options);
    }

    onFilterByName(name: string): void {
        this.viewFileOptionsService.setNameFilter(name);
    }

    onFilterByStatus(status: ViewFileStatus | null): void {
        this.viewFileOptionsService.setSelectedStatusFilter(status);
    }

    onSort(sortMethod: ViewFileOptionsSortMethod): void {
        this.viewFileOptionsService.setSortMethod(sortMethod);
    }

    onToggleShowDetails(): void {
        if (this.latestOptions) {
            this.viewFileOptionsService.setShowDetails(!this.latestOptions.showDetails);
        }
    }

    onTogglePinFilter(): void {
        if (this.latestOptions) {
            this.viewFileOptionsService.setPinFilter(!this.latestOptions.pinFilter);
        }
    }

    private isStatusEnabled(files: readonly ViewFile[], status: ViewFileStatus): boolean {
        return files.findIndex(f => f.status === status) >= 0;
    }
}
