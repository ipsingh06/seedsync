import {ChangeDetectionStrategy, ChangeDetectorRef,Component,
        OnInit, ViewChild, ViewContainerRef} from "@angular/core";

import {LogService} from "../../services/logs/log.service";
import {LogRecord} from "../../services/logs/log-record";
import {StreamServiceRegistry} from "../../services/base/stream-service.registry";
import {ConnectedService} from "../../services/utils/connected.service";
import {Localization} from "../../common/localization";

@Component({
    selector: "app-logs-page",
    templateUrl: "./logs-page.component.html",
    styleUrls: ["./logs-page.component.scss"],
    providers: [],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class LogsPageComponent implements OnInit {
    public readonly LogRecord = LogRecord;
    public readonly Localization = Localization;

    @ViewChild('templateRecord') templateRecord;
    @ViewChild('templateConnected') templateConnected;

    // Where to insert the cloned content
    @ViewChild('container', {read:ViewContainerRef}) container;

    private _logService: LogService;
    private _connectedService: ConnectedService;

    constructor(private _changeDetector: ChangeDetectorRef,
                private _streamRegistry: StreamServiceRegistry) {
        this._logService = _streamRegistry.logService;
        this._connectedService = _streamRegistry.connectedService;
    }

    ngOnInit() {
        this._logService.logs.subscribe({
            next: record => {
                this.insertRecord(record);
            }
        });
        this._connectedService.connected.subscribe({
            next: connected => {
                this.insertConnected(connected);
            }
        });
    }

    private insertConnected(connected: boolean) {
        this.container.createEmbeddedView(this.templateConnected, {connected: connected});
        this._changeDetector.detectChanges();
    }

    private insertRecord(record: LogRecord) {
        this.container.createEmbeddedView(this.templateRecord, {record: record});
        this._changeDetector.detectChanges();
    }
}
