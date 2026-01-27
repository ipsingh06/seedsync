import { Component, Input, Output, ChangeDetectionStrategy, EventEmitter, OnChanges, SimpleChanges, ViewChild, ElementRef, inject } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { Dialog, DialogModule } from '@angular/cdk/dialog';

import { Observable } from 'rxjs';
import { ViewFile, ViewFileStatus } from '../../services/files/view-file';
import { ViewFileOptions } from '../../services/files/view-file-options';
import { Localization } from '../../common/localization';
import { FileSizePipe } from '../../common/file-size.pipe';
import { EtaPipe } from '../../common/eta.pipe';
import { CapitalizePipe } from '../../common/capitalize.pipe';
import { ClickStopPropagationDirective } from '../../common/click-stop-propagation.directive';
import { ConfirmDialogComponent } from '../../common/confirm-dialog.component';

export enum FileAction {
    QUEUE,
    STOP,
    EXTRACT,
    DELETE_LOCAL,
    DELETE_REMOTE
}

@Component({
    selector: 'app-file',
    standalone: true,
    imports: [CommonModule, DatePipe, FileSizePipe, EtaPipe, CapitalizePipe, ClickStopPropagationDirective, DialogModule],
    templateUrl: './file.component.html',
    styleUrl: './file.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FileComponent implements OnChanges {
    // Make types accessible from template
    ViewFileStatus = ViewFileStatus;
    FileAction = FileAction;
    min = Math.min;

    @ViewChild('fileElement') fileElement!: ElementRef<HTMLDivElement>;

    @Input() file!: ViewFile;
    @Input() options!: Observable<ViewFileOptions>;

    @Output() queueEvent = new EventEmitter<ViewFile>();
    @Output() stopEvent = new EventEmitter<ViewFile>();
    @Output() extractEvent = new EventEmitter<ViewFile>();
    @Output() deleteLocalEvent = new EventEmitter<ViewFile>();
    @Output() deleteRemoteEvent = new EventEmitter<ViewFile>();

    activeAction: FileAction | null = null;

    private dialog = inject(Dialog);

    ngOnChanges(changes: SimpleChanges): void {
        const oldFile: ViewFile | undefined = changes['file']?.previousValue;
        const newFile: ViewFile | undefined = changes['file']?.currentValue;
        if (oldFile != null && newFile != null && oldFile.status !== newFile.status) {
            this.activeAction = null;
            if (newFile.isSelected && this.fileElement?.nativeElement && !this.isElementInViewport(this.fileElement.nativeElement)) {
                this.fileElement.nativeElement.scrollIntoView();
            }
        }
    }

    showDeleteConfirmation(title: string, message: string, callback: () => void): void {
        const dialogRef = this.dialog.open<boolean>(ConfirmDialogComponent, {
            data: { title, message }
        });

        dialogRef.closed.subscribe(result => {
            if (result) {
                callback();
            }
        });
    }

    isQueueable(): boolean {
        return this.activeAction == null && this.file.isQueueable;
    }

    isStoppable(): boolean {
        return this.activeAction == null && this.file.isStoppable;
    }

    isExtractable(): boolean {
        return this.activeAction == null && this.file.isExtractable && this.file.isArchive;
    }

    isLocallyDeletable(): boolean {
        return this.activeAction == null && this.file.isLocallyDeletable;
    }

    isRemotelyDeletable(): boolean {
        return this.activeAction == null && this.file.isRemotelyDeletable;
    }

    onQueue(file: ViewFile): void {
        this.activeAction = FileAction.QUEUE;
        this.queueEvent.emit(file);
    }

    onStop(file: ViewFile): void {
        this.activeAction = FileAction.STOP;
        this.stopEvent.emit(file);
    }

    onExtract(file: ViewFile): void {
        this.activeAction = FileAction.EXTRACT;
        this.extractEvent.emit(file);
    }

    onDeleteLocal(file: ViewFile): void {
        this.showDeleteConfirmation(
            Localization.Modal.DELETE_LOCAL_TITLE,
            Localization.Modal.DELETE_LOCAL_MESSAGE(file.name),
            () => {
                this.activeAction = FileAction.DELETE_LOCAL;
                this.deleteLocalEvent.emit(file);
            }
        );
    }

    onDeleteRemote(file: ViewFile): void {
        this.showDeleteConfirmation(
            Localization.Modal.DELETE_REMOTE_TITLE,
            Localization.Modal.DELETE_REMOTE_MESSAGE(file.name),
            () => {
                this.activeAction = FileAction.DELETE_REMOTE;
                this.deleteRemoteEvent.emit(file);
            }
        );
    }

    private isElementInViewport(el: HTMLElement): boolean {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
}
