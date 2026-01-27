import {Component, Input, Output, ChangeDetectionStrategy, EventEmitter, OnInit} from "@angular/core";
import {Subject} from "rxjs/Subject";

@Component({
    selector: "app-option",
    providers: [],
    templateUrl: "./option.component.html",
    styleUrls: ["./option.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class OptionComponent implements OnInit {
    @Input() type: OptionType;
    @Input() label: string;
    @Input() value: any;
    @Input() description: string;

    @Output() changeEvent = new EventEmitter<any>();

    // expose to template
    public OptionType = OptionType;

    private readonly DEBOUNCE_TIME_MS: number = 1000;

    private newValue = new Subject<any>();

    // noinspection JSUnusedGlobalSymbols
    ngOnInit(): void {
        // Debounce
        // References:
        //      https://angular.io/tutorial/toh-pt6#fix-the-herosearchcomponent-class
        //      https://stackoverflow.com/a/41965515
        this.newValue
            .debounceTime(this.DEBOUNCE_TIME_MS)
            .distinctUntilChanged()
            .subscribe({next: val => this.changeEvent.emit(val)});
    }

    onChange(value: any) {
        this.newValue.next(value);
    }
}

export enum OptionType {
    Text,
    Checkbox,
    Password
}
