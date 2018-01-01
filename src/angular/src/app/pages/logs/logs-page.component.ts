import {ChangeDetectionStrategy, ChangeDetectorRef,Component,
        OnInit, ViewChild, ViewContainerRef} from "@angular/core";

import {LogService} from "../../services/logs/log.service";
import {LogRecord} from "../../services/logs/log-record";

@Component({
    selector: "app-logs-page",
    templateUrl: "./logs-page.component.html",
    styleUrls: ["./logs-page.component.scss"],
    providers: [],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class LogsPageComponent implements OnInit {
    public readonly LogRecord = LogRecord;

    // What to clone
    @ViewChild('clone') template;

    // Where to insert the cloned content
    @ViewChild('container', {read:ViewContainerRef}) container;

    constructor(private _logService: LogService,
                private _changeDetector: ChangeDetectorRef) {
    }

    ngOnInit() {
        this._logService.logs.subscribe({
            next: record => {
                this.insertRecord(record);
            }
        });
    }

    private insertRecord(record: LogRecord){
        this.container.createEmbeddedView(this.template, {record: record});
        this._changeDetector.detectChanges();
    }
}
