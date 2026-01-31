import {
    AfterContentChecked, AfterViewInit,
    ChangeDetectionStrategy, ChangeDetectorRef, Component, ElementRef, HostListener,
    OnInit, ViewChild, ViewContainerRef
} from "@angular/core";
import {NgIf, DatePipe, AsyncPipe} from "@angular/common";

import {LogService} from "../../services/logs/log.service";
import {LogRecord} from "../../services/logs/log-record";
import {StreamServiceRegistry} from "../../services/base/stream-service.registry";
import {Localization} from "../../common/localization";
import {DomService} from "../../services/utils/dom.service";
import {Observable} from "rxjs";

@Component({
    selector: "app-logs-page",
    templateUrl: "./logs-page.component.html",
    styleUrls: ["./logs-page.component.scss"],
    providers: [],
    changeDetection: ChangeDetectionStrategy.OnPush,
    standalone: true,
    imports: [NgIf, DatePipe, AsyncPipe]
})
export class LogsPageComponent implements OnInit, AfterViewInit, AfterContentChecked {
    public readonly LogRecord = LogRecord;
    public readonly Localization = Localization;

    public headerHeight: Observable<number>;

    @ViewChild("templateRecord", {static: true}) templateRecord;

    // Where to insert the cloned content
    @ViewChild("container", {static: true, read: ViewContainerRef}) container;

    @ViewChild("logHead", {static: true}) logHead;
    @ViewChild("logTail", {static: true}) logTail;

    public showScrollToTopButton = false;
    public showScrollToBottomButton = false;

    private _logService: LogService;
    private _viewInitialized = false;

    constructor(private _elementRef: ElementRef,
                private _changeDetector: ChangeDetectorRef,
                private _streamRegistry: StreamServiceRegistry,
                private _domService: DomService) {
        this._logService = _streamRegistry.logService;
        this.headerHeight = this._domService.headerHeight;
    }

    ngOnInit() {
        // Subscription moved to ngAfterViewInit to ensure ViewChild elements are available
    }

    ngAfterViewInit() {
        this._viewInitialized = true;

        // Subscribe to logs after view is initialized so ViewChild elements are available
        this._logService.logs.subscribe({
            next: record => {
                this.insertRecord(record);
            }
        });
    }

    ngAfterContentChecked() {
        // Refresh button state when tabs is switched away and back
        // Only run after view is initialized (ViewChild elements are available)
        if (this._viewInitialized) {
            this.refreshScrollButtonVisibility();
        }
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
        // Guard against ViewChild elements not being available
        if (!this.container || !this.templateRecord || !this.logTail) {
            return;
        }

        // Scroll down if the log is visible and already scrolled to the bottom
        const scrollToBottom = this._elementRef.nativeElement.offsetParent != null &&
            LogsPageComponent.isElementInViewport(this.logTail.nativeElement);
        this.container.createEmbeddedView(this.templateRecord, {record: record});
        this._changeDetector.detectChanges();

        if (scrollToBottom) {
            this.scrollToBottom();
        }
        this.refreshScrollButtonVisibility();
    }

    private refreshScrollButtonVisibility() {
        // Guard against ViewChild elements not being available
        if (!this.logHead || !this.logTail) {
            return;
        }

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
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /* or $(window).height() */
            rect.right <= (window.innerWidth || document.documentElement.clientWidth) /* or $(window).width() */
        );
    }
}
