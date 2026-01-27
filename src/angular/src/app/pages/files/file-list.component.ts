import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';

import { ViewFileService } from '../../services/files/view-file.service';
import { ViewFile } from '../../services/files/view-file';
import { LoggerService } from '../../services/utils/logger.service';
import { ViewFileOptions } from '../../services/files/view-file-options';
import { ViewFileOptionsService } from '../../services/files/view-file-options.service';
import { FileComponent } from './file.component';

@Component({
    selector: 'app-file-list',
    standalone: true,
    imports: [CommonModule, FileComponent],
    templateUrl: './file-list.component.html',
    styleUrl: './file-list.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FileListComponent {
    public files: Observable<readonly ViewFile[]>;
    public options: Observable<ViewFileOptions>;

    private logger = inject(LoggerService);
    private viewFileService = inject(ViewFileService);
    private viewFileOptionsService = inject(ViewFileOptionsService);

    constructor() {
        this.files = this.viewFileService.filteredFiles;
        this.options = this.viewFileOptionsService.options;
    }

    trackByName(_index: number, item: ViewFile): string {
        return item.name;
    }

    onSelect(file: ViewFile): void {
        if (file.isSelected) {
            this.viewFileService.unsetSelected();
        } else {
            this.viewFileService.setSelected(file);
        }
    }

    onQueue(file: ViewFile): void {
        this.viewFileService.queue(file).subscribe(data => {
            this.logger.info(data);
        });
    }

    onStop(file: ViewFile): void {
        this.viewFileService.stop(file).subscribe(data => {
            this.logger.info(data);
        });
    }

    onExtract(file: ViewFile): void {
        this.viewFileService.extract(file).subscribe(data => {
            this.logger.info(data);
        });
    }

    onDeleteLocal(file: ViewFile): void {
        this.viewFileService.deleteLocal(file).subscribe(data => {
            this.logger.info(data);
        });
    }

    onDeleteRemote(file: ViewFile): void {
        this.viewFileService.deleteRemote(file).subscribe(data => {
            this.logger.info(data);
        });
    }
}
