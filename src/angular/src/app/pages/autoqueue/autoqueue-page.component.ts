import { Component, ChangeDetectionStrategy, ChangeDetectorRef, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';

import { AutoQueueService } from '../../services/autoqueue/autoqueue.service';
import { AutoQueuePattern } from '../../services/autoqueue/autoqueue-pattern';
import { Notification } from '../../services/utils/notification';
import { NotificationService } from '../../services/utils/notification.service';
import { ConnectedService } from '../../services/utils/connected.service';
import { StreamServiceRegistry } from '../../services/base/stream-service.registry';
import { ConfigService } from '../../services/settings/config.service';

@Component({
    selector: 'app-autoqueue-page',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './autoqueue-page.component.html',
    styleUrl: './autoqueue-page.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class AutoQueuePageComponent implements OnInit {
    public patterns: Observable<readonly AutoQueuePattern[]>;
    public newPattern = '';

    public connected = false;
    public enabled = false;
    public patternsOnly = false;

    private connectedService: ConnectedService;

    private changeDetector = inject(ChangeDetectorRef);
    private autoqueueService = inject(AutoQueueService);
    private notifService = inject(NotificationService);
    private configService = inject(ConfigService);
    private streamServiceRegistry = inject(StreamServiceRegistry);

    constructor() {
        this.connectedService = this.streamServiceRegistry.connectedService;
        this.patterns = this.autoqueueService.patterns;
    }

    ngOnInit(): void {
        this.connectedService.connected.subscribe({
            next: (connected: boolean) => {
                this.connected = connected;
                if (!this.connected) {
                    this.newPattern = '';
                }
            }
        });

        this.configService.config.subscribe({
            next: config => {
                if (config != null) {
                    this.enabled = config.autoqueue.enabled;
                    this.patternsOnly = config.autoqueue.patterns_only;
                } else {
                    this.enabled = false;
                    this.patternsOnly = false;
                }
                this.changeDetector.detectChanges();
            }
        });

        // Initialize services
        this.autoqueueService.onInit();
    }

    onAddPattern(): void {
        this.autoqueueService.add(this.newPattern).subscribe({
            next: reaction => {
                if (reaction.success) {
                    this.newPattern = '';
                } else {
                    const notif = Notification.danger(reaction.errorMessage ?? 'Error', true);
                    this.notifService.show(notif);
                }
            }
        });
    }

    onRemovePattern(pattern: AutoQueuePattern): void {
        this.autoqueueService.remove(pattern.pattern).subscribe({
            next: reaction => {
                if (!reaction.success) {
                    const notif = Notification.danger(reaction.errorMessage ?? 'Error', true);
                    this.notifService.show(notif);
                }
            }
        });
    }
}
