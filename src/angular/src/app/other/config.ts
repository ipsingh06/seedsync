import {Record} from 'immutable';

/**
 * Backend config
 * Note: Naming convention matches that used in the JSON
 */

/*
 * GENERAL
 */
interface IGeneral {
    debug: boolean;
}
const DefaultGeneral: IGeneral = {
    debug: null
};
const GeneralRecord = Record(DefaultGeneral);

/*
 * LFTP
 */
interface ILftp {
    remote_address: string;
    remote_username: string;
    remote_path: string;
    local_path: string;
    remote_path_to_scan_script: string;
    num_max_parallel_downloads: number;
    num_max_parallel_files_per_download: number;
    num_max_connections_per_root_file: number;
    num_max_connections_per_dir_file: number;
    num_max_total_connections: number;
}
const DefaultLftp: ILftp = {
    remote_address: null,
    remote_username: null,
    remote_path: null,
    local_path: null,
    remote_path_to_scan_script: null,
    num_max_parallel_downloads: null,
    num_max_parallel_files_per_download: null,
    num_max_connections_per_root_file: null,
    num_max_connections_per_dir_file: null,
    num_max_total_connections: null,
};
const LftpRecord = Record(DefaultLftp);

/*
 * CONTROLLER
 */
interface IController {
    interval_ms_remote_scan: number;
    interval_ms_local_scan: number;
    interval_ms_downloading_scan: number;
}
const DefaultController: IController = {
    interval_ms_remote_scan: null,
    interval_ms_local_scan: null,
    interval_ms_downloading_scan: null,
};
const ControllerRecord = Record(DefaultController);

/*
 * WEB
 */
interface IWeb {
    port: number;
}
const DefaultWeb: IWeb = {
    port: null
};
const WebRecord = Record(DefaultWeb);



/*
 * CONFIG
 */
interface IConfig {
    general: IGeneral,
    lftp: ILftp,
    controller: IController,
    web: IWeb

}
const DefaultConfig: IConfig = {
    general: null,
    lftp: null,
    controller: null,
    web: null
};
const ConfigRecord = Record(DefaultConfig);


export class Config extends ConfigRecord implements IConfig {
    general: IGeneral;
    lftp: ILftp;
    controller: IController;
    web: IWeb;

    constructor(props) {
        // Create immutable members
        super({
            general: GeneralRecord(props.general),
            lftp: LftpRecord(props.lftp),
            controller: ControllerRecord(props.controller),
            web: WebRecord(props.web),
        });
    }
}
