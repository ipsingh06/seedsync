import {Component, Input, Output, ChangeDetectionStrategy, EventEmitter} from "@angular/core";

import {ViewFile} from "../../services/files/view-file";

@Component({
    selector: "app-file",
    providers: [],
    templateUrl: "./file.component.html",
    styleUrls: ["./file.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FileComponent {
    // Make ViewFile optionType accessible from template
    ViewFile = ViewFile;

    // Expose min function for template
    min = Math.min;

    @Input() file: ViewFile;

    @Output() queueEvent = new EventEmitter<ViewFile>();
    @Output() stopEvent = new EventEmitter<ViewFile>();
    @Output() extractEvent = new EventEmitter<ViewFile>();
    @Output() deleteLocalEvent = new EventEmitter<ViewFile>();
    @Output() deleteRemoteEvent = new EventEmitter<ViewFile>();

    onQueue(file: ViewFile) {
        // Pass to parent component
        this.queueEvent.emit(file);
    }

    onStop(file: ViewFile) {
        // Pass to parent component
        this.stopEvent.emit(file);
    }

    onExtract(file: ViewFile) {
        // Pass to parent component
        this.extractEvent.emit(file);
    }

    onDeleteLocal(file: ViewFile) {
        // Pass to parent component
        this.deleteLocalEvent.emit(file);
    }

    onDeleteRemote(file: ViewFile) {
        // Pass to parent component
        this.deleteRemoteEvent.emit(file);
    }
}
