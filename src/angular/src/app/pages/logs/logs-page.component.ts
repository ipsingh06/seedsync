import { Component, ChangeDetectionStrategy, ChangeDetectorRef, OnInit, ViewChild, ElementRef, HostListener, inject } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { Observable } from 'rxjs';

import { LogService } from '../../services/logs/log.service';
import { LogRecord, LogRecordLevel } from '../../services/logs/log-record';
import { StreamServiceRegistry } from '../../services/base/stream-service.registry';
import { DomService } from '../../services/utils/dom.service';

@Component({
    selector: 'app-logs-page',
    standalone: true,
    imports: [CommonModule, DatePipe],
    templateUrl: './logs-page.component.html',
    styleUrl: './logs-page.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class LogsPageComponent implements OnInit {
    LogRecordLevel = LogRecordLevel;

    public headerHeight: Observable<number>;
    public logs: LogRecord[] = [];
    public showScrollToTopButton = false;
    public showScrollToBottomButton = false;

    @ViewChild('logHead') logHead!: ElementRef;
    @ViewChild('logTail') logTail!: ElementRef;

    private logService: LogService;

    private elementRef = inject(ElementRef);
    private changeDetector = inject(ChangeDetectorRef);
    private streamRegistry = inject(StreamServiceRegistry);
    private domService = inject(DomService);

    constructor() {
        this.logService = this.streamRegistry.logService;
        this.headerHeight = this.domService.headerHeight;
    }

    ngOnInit(): void {
        this.logService.logs.subscribe({
            next: record => {
                this.insertRecord(record);
            }
        });
    }

    scrollToTop(): void {
        window.scrollTo(0, 0);
    }

    scrollToBottom(): void {
        window.scrollTo(0, document.body.scrollHeight);
    }

    @HostListener('window:scroll')
    checkScroll(): void {
        this.refreshScrollButtonVisibility();
    }

    private insertRecord(record: LogRecord): void {
        const scrollToBottom = this.elementRef.nativeElement.offsetParent != null &&
            this.logTail?.nativeElement && this.isElementInViewport(this.logTail.nativeElement);

        this.logs = [...this.logs, record];
        this.changeDetector.detectChanges();

        if (scrollToBottom) {
            this.scrollToBottom();
        }
        this.refreshScrollButtonVisibility();
    }

    private refreshScrollButtonVisibility(): void {
        this.showScrollToTopButton = this.logHead?.nativeElement &&
            !this.isElementInViewport(this.logHead.nativeElement);
        this.showScrollToBottomButton = this.logTail?.nativeElement &&
            !this.isElementInViewport(this.logTail.nativeElement);
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
