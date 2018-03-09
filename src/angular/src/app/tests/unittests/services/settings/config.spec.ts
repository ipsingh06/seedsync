import * as Immutable from "immutable";

import {Config} from "../../../../services/settings/config";

describe("Testing config record initialization", () => {
    let config: Config;

    beforeEach(() => {
        const configJson = {
            general: {
                debug: true
            },
            lftp: {
                remote_address: "remote.server.com",
                remote_username: "some.user",
                remote_port: 3456,
                remote_path: "/some/remote/path",
                local_path: "/some/local/path",
                remote_path_to_scan_script: "/another/remote/path",
                num_max_parallel_downloads: 2,
                num_max_parallel_files_per_download: 8,
                num_max_connections_per_root_file: 32,
                num_max_connections_per_dir_file: 4,
                num_max_total_connections: 32,
                use_temp_file: true
            },
            controller: {
                interval_ms_remote_scan: 30000,
                interval_ms_local_scan: 10000,
                interval_ms_downloading_scan: 1000,
                extract_path: "/path/to/extract",
                use_local_path_as_extract_path: true,
            },
            web: {
                port: 8800
            },
            autoqueue: {
                enabled: true,
                patterns_only: false,
                auto_extract: true,
            }
        };
        config = new Config(configJson);
    });


    it("should initialize with correct values", () => {
        expect(config.general.debug).toBe(true);
        expect(config.lftp.remote_address).toBe("remote.server.com");
        expect(config.lftp.remote_username).toBe("some.user");
        expect(config.lftp.remote_port).toBe(3456);
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
        expect(config.controller.extract_path).toBe("/path/to/extract");
        expect(config.controller.use_local_path_as_extract_path).toBe(true);
        expect(config.web.port).toBe(8800);
        expect(config.autoqueue.enabled).toBe(true);
        expect(config.autoqueue.patterns_only).toBe(false);
        expect(config.autoqueue.auto_extract).toBe(true);
    });

    it("should be immutable", () => {
        expect(config instanceof Immutable.Record).toBe(true);
    });

    it("should have immutable members", () => {
        expect(config.general instanceof Immutable.Record).toBe(true);
        expect(config.lftp instanceof Immutable.Record).toBe(true);
        expect(config.controller instanceof Immutable.Record).toBe(true);
        expect(config.web instanceof Immutable.Record).toBe(true);
        expect(config.autoqueue instanceof Immutable.Record).toBe(true);
    });
});
