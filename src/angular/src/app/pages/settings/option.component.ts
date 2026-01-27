import { Component, Input, Output, ChangeDetectionStrategy, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';

export enum OptionType {
    Text,
    Checkbox,
    Password
}

@Component({
    selector: 'app-option',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './option.component.html',
    styleUrl: './option.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class OptionComponent implements OnInit {
    @Input() type: OptionType = OptionType.Text;
    @Input() label = '';
    @Input() value: unknown = '';
    @Input() description: string | null = null;

    @Output() changeEvent = new EventEmitter<unknown>();

    OptionType = OptionType;

    private readonly DEBOUNCE_TIME_MS = 1000;
    private newValue = new Subject<unknown>();

    ngOnInit(): void {
        this.newValue.pipe(
            debounceTime(this.DEBOUNCE_TIME_MS),
            distinctUntilChanged()
        ).subscribe({
            next: val => this.changeEvent.emit(val)
        });
    }

    onChange(value: unknown): void {
        this.newValue.next(value);
    }
}
