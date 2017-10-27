import {Component, Input, Output, ChangeDetectionStrategy, EventEmitter} from '@angular/core';

import {ViewFile} from "../../view/view-file";

@Component({
    selector: '[file]',
    providers: [],
    templateUrl: './file.component.html',
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FileComponent {
    // Make ViewFile type accessible from template
    ViewFile = ViewFile;

    @Input() file: ViewFile;

    @Output() queueEvent = new EventEmitter<ViewFile>();
    @Output() stopEvent = new EventEmitter<ViewFile>();

    onQueue(file: ViewFile) {
        // Pass to parent component
        this.queueEvent.emit(file);
    }

    onStop(file: ViewFile) {
        // Pass to parent component
        this.stopEvent.emit(file);
    }
}
