import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import * as Immutable from "immutable";

import {LoggerService} from "../../../../services/utils/logger.service";
import {LogService} from "../../../../services/logs/log.service";
import {LogRecord} from "../../../../services/logs/log-record";


describe("Testing log service", () => {
    let logService: LogService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                LoggerService,
                LogService
            ]
        });

        logService = TestBed.get(LogService);
    });

    it("should create an instance", () => {
        expect(logService).toBeDefined();
    });

    it("should register all events with the event source", () => {
        expect(logService.getEventNames()).toEqual(
            ["log-record"]
        );
    });

    it("should send correct record on event", fakeAsync(() => {
        let count = 0;
        let latestRecord: LogRecord = null;
        // noinspection JSUnusedAssignment
        let json = null;

        logService.logs.subscribe({
            next: record => {
                count++;
                latestRecord = record;
            }
        });

        json = {
            level_name: "DEBUG",
            time: "1514776875.9439101",
            logger_name: "seedsync.Controller.Model",
            message: "LftpModel: Adding a listener"
        };
        logService.notifyEvent("log-record", JSON.stringify(json));
        tick();
        expect(count).toBe(1);
        expect(Immutable.is(latestRecord, LogRecord.fromJson(json))).toBe(true);

        json = {
            level_name: "WARNING",
            time: "1514771875.9746701",
            logger_name: "another name",
            message: "another message"
        };
        logService.notifyEvent("log-record", JSON.stringify(json));
        tick();
        expect(count).toBe(2);
        expect(Immutable.is(latestRecord, LogRecord.fromJson(json))).toBe(true);
    }));

    it("should not cache records", fakeAsync(() => {
        let count = 0;
        let latestRecord: LogRecord = null;
        // noinspection JSUnusedAssignment
        let data1 = null;
        // noinspection JSUnusedAssignment
        let data2  = null;

        data1 = {
            level_name: "WARNING",
            time: "1514771875.9746701",
            logger_name: "another name",
            message: "another message"
        };
        data2 = {
            level_name: "DEBUG",
            time: "1514776875.9439101",
            logger_name: "seedsync.Controller.Model",
            message: "LftpModel: Adding a listener"
        };

        // Send out some data before subscription
        logService.notifyEvent("log-record", JSON.stringify(data1));
        logService.notifyEvent("log-record", JSON.stringify(data2));
        tick();

        logService.logs.subscribe({
            next: record => {
                count++;
                latestRecord = record;
            }
        });
        tick();
        // Except no data yet
        expect(count).toBe(0);

        logService.notifyEvent("log-record", JSON.stringify(data2));
        tick();
        expect(count).toBe(1);
        expect(Immutable.is(latestRecord, LogRecord.fromJson(data2))).toBe(true);

        logService.notifyEvent("log-record", JSON.stringify(data1));
        tick();
        expect(count).toBe(2);
        expect(Immutable.is(latestRecord, LogRecord.fromJson(data1))).toBe(true);
    }));
});
