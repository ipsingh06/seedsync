import * as Immutable from "immutable";

import {LogRecord} from "../../../../services/logs/log-record";


describe("Testing log record initialization", () => {
    let baseJson;
    let baseLogRecord: LogRecord;

    beforeEach(() => {
        baseJson = {
            level_name: "DEBUG",
            time: "1514776875.9439101",
            logger_name: "seedsync.Controller.Model",
            message: "LftpModel: Adding a listener",
            exc_tb: "Exception Traceback"
        };
        baseLogRecord = LogRecord.fromJson(baseJson);
    });

    it("should be immutable", () => {
        expect(baseLogRecord instanceof Immutable.Record).toBe(true);
    });

    it("should correctly initialize logger name", () => {
        expect(baseLogRecord.loggerName).toBe("seedsync.Controller.Model");
    });

    it("should correctly initialize message", () => {
        expect(baseLogRecord.message).toBe("LftpModel: Adding a listener");
    });

    it("should correctly initialize level names", () => {
        baseJson.level_name = "DEBUG";
        baseLogRecord = LogRecord.fromJson(baseJson);
        expect(baseLogRecord.level).toBe(LogRecord.Level.DEBUG);
        baseJson.level_name = "INFO";
        baseLogRecord = LogRecord.fromJson(baseJson);
        expect(baseLogRecord.level).toBe(LogRecord.Level.INFO);
        baseJson.level_name = "WARNING";
        baseLogRecord = LogRecord.fromJson(baseJson);
        expect(baseLogRecord.level).toBe(LogRecord.Level.WARNING);
        baseJson.level_name = "ERROR";
        baseLogRecord = LogRecord.fromJson(baseJson);
        expect(baseLogRecord.level).toBe(LogRecord.Level.ERROR);
        baseJson.level_name = "CRITICAL";
        baseLogRecord = LogRecord.fromJson(baseJson);
        expect(baseLogRecord.level).toBe(LogRecord.Level.CRITICAL);
    });

    it("should correctly initialize time", () => {
        expect(baseLogRecord.time).toEqual(new Date(1514776875943));
    });

    it("should correctly initialize exception traceback", () => {
        expect(baseLogRecord.exceptionTraceback).toEqual("Exception Traceback");
        baseJson.exc_tb = null;
        baseLogRecord = LogRecord.fromJson(baseJson);
        expect(baseLogRecord.exceptionTraceback).toBeNull();
    });
});
