import {
    Component, Input, Output, ChangeDetectionStrategy,
    EventEmitter, OnChanges, SimpleChanges
} from "@angular/core";

import {ViewFile} from "../../services/files/view-file";

@Component({
    selector: "app-file",
    providers: [],
    templateUrl: "./file.component.html",
    styleUrls: ["./file.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FileComponent implements OnChanges {
    // Make ViewFile optionType accessible from template
    ViewFile = ViewFile;

    // Make FileAction accessible from template
    FileAction = FileAction;

    // Expose min function for template
    min = Math.min;

    @Input() file: ViewFile;

    @Output() queueEvent = new EventEmitter<ViewFile>();
    @Output() stopEvent = new EventEmitter<ViewFile>();
    @Output() extractEvent = new EventEmitter<ViewFile>();
    @Output() deleteLocalEvent = new EventEmitter<ViewFile>();
    @Output() deleteRemoteEvent = new EventEmitter<ViewFile>();

    // Indicates an active action on-going
    activeAction: FileAction = null;

    ngOnChanges(changes: SimpleChanges): void {
        // Reset active action if the status changes
        let oldFile: ViewFile = changes.file.previousValue;
        let newFile: ViewFile = changes.file.currentValue;
        if(oldFile != null && newFile != null && oldFile.status != newFile.status) {
            this.activeAction = null;
        }
    }

    isQueueable() {
        return this.activeAction == null && this.file.isQueueable;
    }

    isStoppable() {
        return this.activeAction == null && this.file.isStoppable;
    }

    isExtractable() {
        return this.activeAction == null && this.file.isExtractable && this.file.isArchive;
    }

    isLocallyDeletable() {
        return this.activeAction == null && this.file.isLocallyDeletable;
    }

    isRemotelyDeletable() {
        return this.activeAction == null && this.file.isRemotelyDeletable;
    }

    onQueue(file: ViewFile) {
        this.activeAction = FileAction.QUEUE;
        // Pass to parent component
        this.queueEvent.emit(file);
    }

    onStop(file: ViewFile) {
        this.activeAction = FileAction.STOP;
        // Pass to parent component
        this.stopEvent.emit(file);
    }

    onExtract(file: ViewFile) {
        this.activeAction = FileAction.EXTRACT;
        // Pass to parent component
        this.extractEvent.emit(file);
    }

    onDeleteLocal(file: ViewFile) {
        this.activeAction = FileAction.DELETE_LOCAL;
        // Pass to parent component
        this.deleteLocalEvent.emit(file);
    }

    onDeleteRemote(file: ViewFile) {
        this.activeAction = FileAction.DELETE_REMOTE;
        // Pass to parent component
        this.deleteRemoteEvent.emit(file);
    }
}

export enum FileAction {
    QUEUE,
    STOP,
    EXTRACT,
    DELETE_LOCAL,
    DELETE_REMOTE
}
