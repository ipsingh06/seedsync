import {Component, Input, ChangeDetectionStrategy} from '@angular/core';

import {ViewFile} from "./view-file";

@Component({
    selector: 'file',
    providers: [],
    templateUrl: './file.component.html',
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FileComponent {
    @Input() file: ViewFile;
}
