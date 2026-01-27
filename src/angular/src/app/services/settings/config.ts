/**
 * Backend config
 * Note: Naming convention matches that used in the JSON
 */

export interface GeneralConfig {
    readonly debug: boolean;
}

export interface LftpConfig {
    readonly remote_address: string;
    readonly remote_username: string;
    readonly remote_password: string;
    readonly remote_port: number;
    readonly remote_path: string;
    readonly local_path: string;
    readonly remote_path_to_scan_script: string;
    readonly use_ssh_key: boolean;
    readonly num_max_parallel_downloads: number;
    readonly num_max_parallel_files_per_download: number;
    readonly num_max_connections_per_root_file: number;
    readonly num_max_connections_per_dir_file: number;
    readonly num_max_total_connections: number;
    readonly use_temp_file: boolean;
}

export interface ControllerConfig {
    readonly interval_ms_remote_scan: number;
    readonly interval_ms_local_scan: number;
    readonly interval_ms_downloading_scan: number;
    readonly extract_path: string;
    readonly use_local_path_as_extract_path: boolean;
}

export interface WebConfig {
    readonly port: number;
}

export interface AutoQueueConfig {
    readonly enabled: boolean;
    readonly patterns_only: boolean;
    readonly auto_extract: boolean;
}

export interface ConfigData {
    readonly general: GeneralConfig;
    readonly lftp: LftpConfig;
    readonly controller: ControllerConfig;
    readonly web: WebConfig;
    readonly autoqueue: AutoQueueConfig;
}

/**
 * Immutable Config class
 */
export class Config implements ConfigData {
    readonly general: GeneralConfig;
    readonly lftp: LftpConfig;
    readonly controller: ControllerConfig;
    readonly web: WebConfig;
    readonly autoqueue: AutoQueueConfig;

    constructor(data: ConfigData) {
        this.general = Object.freeze({ ...data.general });
        this.lftp = Object.freeze({ ...data.lftp });
        this.controller = Object.freeze({ ...data.controller });
        this.web = Object.freeze({ ...data.web });
        this.autoqueue = Object.freeze({ ...data.autoqueue });
        Object.freeze(this);
    }

    /**
     * Create a new Config with updated properties
     */
    update(updates: Partial<ConfigData>): Config {
        return new Config({
            general: updates.general ?? this.general,
            lftp: updates.lftp ?? this.lftp,
            controller: updates.controller ?? this.controller,
            web: updates.web ?? this.web,
            autoqueue: updates.autoqueue ?? this.autoqueue
        });
    }

    /**
     * Create a Config from JSON response
     */
    static fromJson(json: ConfigData): Config {
        return new Config(json);
    }
}
