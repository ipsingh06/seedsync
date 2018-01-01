import {Record} from "immutable";


/**
 * LogRecord immutable
 */
interface ILogRecord {
    time: Date;
    level: LogRecord.Level;
    loggerName: string;
    message: string;
}
const DefaultLogRecord: ILogRecord = {
    time: null,
    level: null,
    loggerName: null,
    message: null,
};
const LogRecordRecord = Record(DefaultLogRecord);
export class LogRecord extends LogRecordRecord implements ILogRecord {
    time: Date;
    level: LogRecord.Level;
    loggerName: string;
    message: string;

    constructor(props) {
        // State mapping
        props.level = LogRecord.Level[props.level];

        super(props);
    }
}


export module LogRecord {
    export function fromJson(json: LogRecordJson): LogRecord {
        return new LogRecord({
            // str -> number, then sec -> ms
            time: new Date(1000 * +json.time),
            level: json.level_name,
            loggerName: json.logger_name,
            message: json.message
        });
    }

    export enum Level {
        DEBUG       = <any> "DEBUG",
        INFO        = <any> "INFO",
        WARNING     = <any> "WARNING",
        ERROR       = <any> "ERROR",
        CRITICAL    = <any> "CRITICAL",
    }
}


/**
 * LogRecord as serialized by the backend.
 * Note: naming convention matches that used in JSON
 */
export interface LogRecordJson {
    time: number;
    level_name: string;
    logger_name: string;
    message: string;
}
