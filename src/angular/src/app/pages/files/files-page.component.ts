import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { FileListComponent } from './file-list.component';
import { FileOptionsComponent } from './file-options.component';
import { StreamServiceRegistry } from '../../services/base/stream-service.registry';
import { ViewFileService } from '../../services/files/view-file.service';
import { ViewFileFilterService } from '../../services/files/view-file-filter.service';
import { ViewFileSortService } from '../../services/files/view-file-sort.service';

@Component({
    selector: 'app-files-page',
    standalone: true,
    imports: [CommonModule, FileListComponent, FileOptionsComponent],
    templateUrl: './files-page.component.html'
})
export class FilesPageComponent implements OnInit {
    private streamServiceRegistry = inject(StreamServiceRegistry);
    private viewFileService = inject(ViewFileService);
    private viewFileFilterService = inject(ViewFileFilterService);
    private viewFileSortService = inject(ViewFileSortService);

    ngOnInit(): void {
        // Initialize the stream service registry
        this.streamServiceRegistry.onInit();

        // Initialize services
        this.viewFileService.init();
        this.viewFileFilterService.init();
        this.viewFileSortService.init();
    }
}
