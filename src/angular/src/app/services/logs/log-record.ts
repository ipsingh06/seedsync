/**
 * LogRecord
 */
export interface LogRecordData {
    readonly time: Date;
    readonly level: LogRecordLevel;
    readonly loggerName: string;
    readonly message: string;
    readonly exceptionTraceback: string | null;
}

export enum LogRecordLevel {
    DEBUG = 'DEBUG',
    INFO = 'INFO',
    WARNING = 'WARNING',
    ERROR = 'ERROR',
    CRITICAL = 'CRITICAL'
}

/**
 * Immutable LogRecord class
 */
export class LogRecord implements LogRecordData {
    readonly time: Date;
    readonly level: LogRecordLevel;
    readonly loggerName: string;
    readonly message: string;
    readonly exceptionTraceback: string | null;

    constructor(data: LogRecordData) {
        this.time = data.time;
        this.level = data.level;
        this.loggerName = data.loggerName;
        this.message = data.message;
        this.exceptionTraceback = data.exceptionTraceback;
        Object.freeze(this);
    }

    /**
     * Create from JSON response
     */
    static fromJson(json: LogRecordJson): LogRecord {
        return new LogRecord({
            // str -> number, then sec -> ms
            time: new Date(1000 * +json.time),
            level: LogRecordLevel[json.level_name as keyof typeof LogRecordLevel] ?? LogRecordLevel.INFO,
            loggerName: json.logger_name,
            message: json.message,
            exceptionTraceback: json.exc_tb ?? null
        });
    }
}

/**
 * JSON structure from backend
 */
export interface LogRecordJson {
    time: number;
    level_name: string;
    logger_name: string;
    message: string;
    exc_tb: string | null;
}
