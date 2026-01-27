import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DIALOG_DATA, DialogRef } from '@angular/cdk/dialog';

export interface ConfirmDialogData {
    title: string;
    message: string;
}

@Component({
    selector: 'app-confirm-dialog',
    standalone: true,
    imports: [CommonModule],
    template: `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{{data.title}}</h5>
                    <button type="button" class="btn-close" (click)="onCancel()" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p [innerHTML]="data.message"></p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" (click)="onCancel()">Cancel</button>
                    <button type="button" class="btn btn-danger" (click)="onConfirm()">Delete</button>
                </div>
            </div>
        </div>
    `,
    styles: [`
        .modal-dialog {
            background: white;
            border-radius: 0.5rem;
            max-width: 500px;
            margin: 1.75rem auto;
        }
        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem;
            border-bottom: 1px solid #dee2e6;
        }
        .modal-body {
            padding: 1rem;
        }
        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
            padding: 1rem;
            border-top: 1px solid #dee2e6;
        }
    `]
})
export class ConfirmDialogComponent {
    data = inject<ConfirmDialogData>(DIALOG_DATA);
    dialogRef = inject(DialogRef<boolean>);

    onConfirm(): void {
        this.dialogRef.close(true);
    }

    onCancel(): void {
        this.dialogRef.close(false);
    }
}
