/**
 * Notification
 */
export interface NotificationData {
    readonly level: NotificationLevel;
    readonly text: string;
    readonly timestamp: number;
    readonly dismissible: boolean;
}

export enum NotificationLevel {
    SUCCESS = 'success',
    INFO = 'info',
    WARNING = 'warning',
    DANGER = 'danger'
}

/**
 * Immutable Notification class
 */
export class Notification implements NotificationData {
    readonly level: NotificationLevel;
    readonly text: string;
    readonly timestamp: number;
    readonly dismissible: boolean;

    constructor(data: Omit<NotificationData, 'timestamp'> & { timestamp?: number }) {
        this.level = data.level;
        this.text = data.text;
        this.timestamp = data.timestamp ?? Date.now();
        this.dismissible = data.dismissible;
        Object.freeze(this);
    }

    /**
     * Create a success notification
     */
    static success(text: string, dismissible: boolean = true): Notification {
        return new Notification({ level: NotificationLevel.SUCCESS, text, dismissible });
    }

    /**
     * Create an info notification
     */
    static info(text: string, dismissible: boolean = true): Notification {
        return new Notification({ level: NotificationLevel.INFO, text, dismissible });
    }

    /**
     * Create a warning notification
     */
    static warning(text: string, dismissible: boolean = true): Notification {
        return new Notification({ level: NotificationLevel.WARNING, text, dismissible });
    }

    /**
     * Create a danger notification
     */
    static danger(text: string, dismissible: boolean = true): Notification {
        return new Notification({ level: NotificationLevel.DANGER, text, dismissible });
    }
}
