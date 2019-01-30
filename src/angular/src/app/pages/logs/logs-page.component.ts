import {
    AfterContentChecked,
    ChangeDetectionStrategy, ChangeDetectorRef, Component, HostListener,
    OnInit, ViewChild, ViewContainerRef
} from "@angular/core";

import {LogService} from "../../services/logs/log.service";
import {LogRecord} from "../../services/logs/log-record";
import {StreamServiceRegistry} from "../../services/base/stream-service.registry";
import {Localization} from "../../common/localization";
import {DomService} from "../../services/utils/dom.service";
import {Observable} from "rxjs/Observable";

@Component({
    selector: "app-logs-page",
    templateUrl: "./logs-page.component.html",
    styleUrls: ["./logs-page.component.scss"],
    providers: [],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class LogsPageComponent implements OnInit, AfterContentChecked {
    public readonly LogRecord = LogRecord;
    public readonly Localization = Localization;

    public headerHeight: Observable<number>;

    @ViewChild("templateRecord") templateRecord;
    @ViewChild("templateConnected") templateConnected;

    // Where to insert the cloned content
    @ViewChild("container", {read: ViewContainerRef}) container;

    @ViewChild("logHead") logHead;
    @ViewChild("logTail") logTail;

    public showScrollToTopButton = false;
    public showScrollToBottomButton = false;

    private _logService: LogService;

    constructor(private _changeDetector: ChangeDetectorRef,
                private _streamRegistry: StreamServiceRegistry,
                private _domService: DomService) {
        this._logService = _streamRegistry.logService;
        this.headerHeight = this._domService.headerHeight;
    }

    ngOnInit() {
        this._logService.logs.subscribe({
            next: record => {
                this.insertRecord(record);
            }
        });
    }

    ngAfterContentChecked() {
        // Refresh button state when tabs is switched away and back
        this.refreshScrollButtonVisibility();
    }

    scrollToTop() {
        // this.logHead.nativeElement.scrollIntoView(true);
        window.scrollTo(0, 0);
    }

    scrollToBottom() {
        window.scrollTo(0, document.body.scrollHeight);
    }

    @HostListener("window:scroll", ["$event"])
    checkScroll() {
        this.refreshScrollButtonVisibility();
    }

    private insertRecord(record: LogRecord) {
        const scrollToBottom = LogsPageComponent.isElementInViewport(this.logTail.nativeElement);
        this.container.createEmbeddedView(this.templateRecord, {record: record});
        this._changeDetector.detectChanges();

        if (scrollToBottom) {
            this.scrollToBottom();
        }
        this.refreshScrollButtonVisibility();
    }

    private refreshScrollButtonVisibility() {
        // Show/hide the scroll buttons
        this.showScrollToTopButton = !LogsPageComponent.isElementInViewport(
            this.logHead.nativeElement
        );
        this.showScrollToBottomButton = !LogsPageComponent.isElementInViewport(
            this.logTail.nativeElement
        );
    }

    // Source: https://stackoverflow.com/a/7557433
    private static isElementInViewport(el): boolean {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /*or $(window).height() */
            rect.right <= (window.innerWidth || document.documentElement.clientWidth) /*or $(window).width() */
        );
    }
}
