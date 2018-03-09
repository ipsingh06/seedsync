import {fakeAsync, TestBed, tick} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";

import * as Immutable from "immutable";

import {ConfigService} from "../../../../services/settings/config.service";
import {LoggerService} from "../../../../services/utils/logger.service";
import {Config} from "../../../../services/settings/config";
import {MockStreamServiceRegistry} from "../../../mocks/mock-stream-service.registry";
import {ConnectedService} from "../../../../services/utils/connected.service";
import {RestService} from "../../../../services/utils/rest.service";
import {StreamServiceRegistry} from "../../../../services/base/stream-service.registry";


// noinspection JSUnusedLocalSymbols
const DoNothing = {next: reaction => {}};


describe("Testing config service", () => {
    let mockRegistry: MockStreamServiceRegistry;
    let httpMock: HttpTestingController;
    let configService: ConfigService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                ConfigService,
                LoggerService,
                RestService,
                ConnectedService,
                {provide: StreamServiceRegistry, useClass: MockStreamServiceRegistry}
            ]
        });

        mockRegistry = TestBed.get(StreamServiceRegistry);
        httpMock = TestBed.get(HttpTestingController);
        configService = TestBed.get(ConfigService);

        // Connect the services
        mockRegistry.connect();

        // Finish test config init
        configService.onInit();
    });

    it("should create an instance", () => {
        expect(configService).toBeDefined();
    });

    it("should parse config json correctly", () => {
        const configJson = {
            general: {
                debug: true
            },
            lftp: {
                remote_address: "remote.server.com",
                remote_username: "some.user",
                remote_path: "/some/remote/path",
                local_path: "/some/local/path",
                remote_path_to_scan_script: "/another/remote/path",
                num_max_parallel_downloads: 2,
                num_max_parallel_files_per_download: 8,
                num_max_connections_per_root_file: 32,
                num_max_connections_per_dir_file: 4,
                num_max_total_connections: 32,
                use_temp_file: true,
            },
            controller: {
                interval_ms_remote_scan: 30000,
                interval_ms_local_scan: 10000,
                interval_ms_downloading_scan: 1000
            },
            web: {
                port: 8800
            },
            autoqueue: {
                enabled: true,
                patterns_only: false
            }
        };
        httpMock.expectOne("/server/config/get").flush(configJson);

        configService.config.subscribe({
            next: config => {
                expect(config.general.debug).toBe(true);
                expect(config.lftp.remote_address).toBe("remote.server.com");
                expect(config.lftp.remote_username).toBe("some.user");
                expect(config.lftp.remote_path).toBe("/some/remote/path");
                expect(config.lftp.local_path).toBe("/some/local/path");
                expect(config.lftp.remote_path_to_scan_script).toBe("/another/remote/path");
                expect(config.lftp.num_max_parallel_downloads).toBe(2);
                expect(config.lftp.num_max_parallel_files_per_download).toBe(8);
                expect(config.lftp.num_max_connections_per_root_file).toBe(32);
                expect(config.lftp.num_max_connections_per_dir_file).toBe(4);
                expect(config.lftp.num_max_total_connections).toBe(32);
                expect(config.lftp.use_temp_file).toBe(true);
                expect(config.controller.interval_ms_remote_scan).toBe(30000);
                expect(config.controller.interval_ms_local_scan).toBe(10000);
                expect(config.controller.interval_ms_downloading_scan).toBe(1000);
                expect(config.web.port).toBe(8800);
                expect(config.autoqueue.enabled).toBe(true);
                expect(config.autoqueue.patterns_only).toBe(false);
            }
        });

        httpMock.verify();
    });

    it("should get null on get error 404", () => {
        httpMock.expectOne("/server/config/get").flush(
        "Not found",
        {status: 404, statusText: "Bad Request"}
        );

        configService.config.subscribe({
            next: config => {
                expect(config).toBe(null);
            }
        });

        httpMock.verify();
    });

    it("should get null on get network error", () => {
        httpMock.expectOne("/server/config/get").error(new ErrorEvent("mock error"));

        configService.config.subscribe({
            next: config => {
                expect(config).toBe(null);
            }
        });

        httpMock.verify();
    });

    it("should get null on disconnect", fakeAsync(() => {
        const configExpected = [
            new Config({lftp: {remote_address: "first"}}),
            null
        ];

        httpMock.expectOne("/server/config/get").flush({lftp: {remote_address: "first"}});
        let configSubscriberIndex = 0;

        configService.config.subscribe({
            next: config => {
                expect(Immutable.is(config, configExpected[configSubscriberIndex++])).toBe(true);
            }
        });

        // status disconnect
        mockRegistry.disconnect();
        tick();

        httpMock.verify();
        expect(configSubscriberIndex).toBe(2);
    }));

    it("should retry GET on disconnect", fakeAsync(() => {
        // first connect
        httpMock.expectOne("/server/config/get").flush("{}");


        // status disconnect
        mockRegistry.disconnect();
        tick();

        // status reconnect
        mockRegistry.connect();
        tick();
        httpMock.expectOne("/server/config/get").flush("{}");

        httpMock.verify();
    }));

    it("should send a GET on a set config option", () => {
        // first connect
        httpMock.expectOne("/server/config/get").flush("{}");

        let configSubscriberIndex = 0;
        configService.set("general", "debug", true).subscribe({
           next: reaction => {
               configSubscriberIndex++;
               expect(reaction.success).toBe(true);
           }
        });

        // set request
        httpMock.expectOne("/server/config/set/general/debug/true").flush("{}");

        expect(configSubscriberIndex).toBe(1);
        httpMock.verify();
    });

    it("should send correct GET requests on setting config options", () => {
        // first connect
        httpMock.expectOne("/server/config/get").flush("{}");

        // boolean
        configService.set("general", "debug", true).subscribe(DoNothing);
        httpMock.expectOne("/server/config/set/general/debug/true").flush("{}");
        configService.set("general", "debug", false).subscribe(DoNothing);
        httpMock.expectOne("/server/config/set/general/debug/false").flush("{}");

        // integer
        configService.set("general", "debug", 0).subscribe(DoNothing);
        httpMock.expectOne("/server/config/set/general/debug/0").flush("{}");
        configService.set("general", "debug", 1000).subscribe(DoNothing);
        httpMock.expectOne("/server/config/set/general/debug/1000").flush("{}");
        configService.set("general", "debug", -1000).subscribe(DoNothing);
        httpMock.expectOne("/server/config/set/general/debug/-1000").flush("{}");

        // string
        configService.set("general", "debug", "test").subscribe(DoNothing);
        httpMock.expectOne("/server/config/set/general/debug/test").flush("{}");
        configService.set("general", "debug", "test space").subscribe(DoNothing);
        httpMock.expectOne("/server/config/set/general/debug/test%2520space").flush("{}");
        configService.set("general", "debug", "test/slash").subscribe(DoNothing);
        httpMock.expectOne("/server/config/set/general/debug/test%252Fslash").flush("{}");
        configService.set("general", "debug", "test\"doublequote").subscribe(
            DoNothing
        );
        httpMock.expectOne("/server/config/set/general/debug/test%2522doublequote").flush("{}");
        configService.set("general", "debug", "/test/leadingslash").subscribe(DoNothing);
        httpMock.expectOne("/server/config/set/general/debug/%252Ftest%252Fleadingslash").flush("{}");

        httpMock.verify();
    });

    it("should return error on setting non-existing section", () => {
        // first connect
        httpMock.expectOne("/server/config/get").flush("{}");

        let configSubscriberIndex = 0;
        configService.set("bad_section", "debug", true).subscribe({
           next: reaction => {
               configSubscriberIndex++;
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Config has no option named bad_section.debug");
           }
        });

        expect(configSubscriberIndex).toBe(1);
        httpMock.verify();
    });

    it("should return error on setting non-existing option", () => {
        // first connect
        httpMock.expectOne("/server/config/get").flush("{}");

        let configSubscriberIndex = 0;
        configService.set("general", "bad_option", true).subscribe({
           next: reaction => {
               configSubscriberIndex++;
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Config has no option named general.bad_option");
           }
        });

        expect(configSubscriberIndex).toBe(1);
        httpMock.verify();
    });

    it("should return error on empty value", () => {
        // first connect
        httpMock.expectOne("/server/config/get").flush("{}");

        let configSubscriberIndex = 0;
        configService.set("general", "debug", "").subscribe({
           next: reaction => {
               configSubscriberIndex++;
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Setting general.debug cannot be blank.");
           }
        });

        expect(configSubscriberIndex).toBe(1);
        httpMock.verify();
    });

    it("should send updated config on a successful set", () => {
        const configJson = {general: {debug: false}};
        // first connect
        httpMock.expectOne("/server/config/get").flush(configJson);

        const configExpected = [
            new Config({general: {debug: false}}),
            new Config({general: {debug: true}})
        ];
        let configSubscriberIndex = 0;
        configService.config.subscribe({
            next: config => {
                expect(Immutable.is(config, configExpected[configSubscriberIndex++])).toBe(true);
            }
        });

        // issue the set
        configService.set("general", "debug", true).subscribe(DoNothing);

        // set request
        httpMock.expectOne("/server/config/set/general/debug/true").flush("");

        expect(configSubscriberIndex).toBe(2);
        httpMock.verify();
    });

    it("should NOT send updated config on a failed set", () => {
        const configJson = {general: {debug: false}};
        // first connect
        httpMock.expectOne("/server/config/get").flush(configJson);

        const configExpected = [
            new Config({general: {debug: false}})
        ];
        let configSubscriberIndex = 0;
        configService.config.subscribe({
            next: config => {
                expect(Immutable.is(config, configExpected[configSubscriberIndex++])).toBe(true);
            }
        });

        // issue the set
        configService.set("general", "debug", true).subscribe(DoNothing);

        // set request
        httpMock.expectOne("/server/config/set/general/debug/true").flush(
            "Not found",
            {status: 404, statusText: "Bad Request"}
        );

        expect(configSubscriberIndex).toBe(1);
        httpMock.verify();
    });
});
