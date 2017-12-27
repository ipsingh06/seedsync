import {OptionType} from "./option.component";

export interface IOption {
    type: OptionType;
    label: string;
    valuePath: [string, string];
    description: string;
}
export interface IOptionsContext {
    header: string;
    options: IOption[];
}

export const OPTIONS_CONTEXT_SERVER: IOptionsContext = {
    header: "Server",
    options: [
        {
            type: OptionType.Text,
            label: "Server Address",
            valuePath: ["lftp", "remote_address"],
            description: null
        },
        {
            type: OptionType.Text,
            label: "Server User",
            valuePath: ["lftp", "remote_username"],
            description: null
        },
        {
            type: OptionType.Text,
            label: "Server Directory",
            valuePath: ["lftp", "remote_path"],
            description: "Path on the remote server from which to download files and directories."
        },
        {
            type: OptionType.Text,
            label: "Local Directory",
            valuePath: ["lftp", "local_path"],
            description: "Path on the local machine where downloaded files and directories " +
                         "are placed."
        },
        {
            type: OptionType.Text,
            label: "Remote SSH Port",
            valuePath: ["lftp", "remote_port"],
            description: "SSH port on the remote server."
        },
        {
            type: OptionType.Text,
            label: "Server Script Path",
            valuePath: ["lftp", "remote_path_to_scan_script"],
            description: "Path on remote server where the scanner script is placed."
        }
    ]
};

export const OPTIONS_CONTEXT_DISCOVERY: IOptionsContext = {
    header: "File Discovery",
    options: [
        {
            type: OptionType.Text,
            label: "Remote Scan Interval (ms)",
            valuePath: ["controller", "interval_ms_remote_scan"],
            description: "How often the remote server is scanned for new files."
        },
        {
            type: OptionType.Text,
            label: "Local Scan Interval (ms)",
            valuePath: ["controller", "interval_ms_local_scan"],
            description: "How often the local directory is scanned."
        },
        {
            type: OptionType.Text,
            label: "Downloading Scan Interval (ms)",
            valuePath: ["controller", "interval_ms_downloading_scan"],
            description: "How often the downloading information is updated."
        },
    ]
};

export const OPTIONS_CONTEXT_CONNECTIONS: IOptionsContext = {
    header: "Connections",
    options: [
        {
            type: OptionType.Text,
            label: "Max Parallel Downloads",
            valuePath: ["lftp", "num_max_parallel_downloads"],
            description: "Maximum number of concurrent downloads.\n" +
                         "Corresponds to the 'cmd:queue-parallel' setting in Lftp."
        },
        {
            type: OptionType.Text,
            label: "Max Total Connections",
            valuePath: ["lftp", "num_max_total_connections"],
            description: "Maximum number of connections across all downloads.\n" +
                         "Corresponds to the 'net:connection-limit' setting in Lftp."
        },
        {
            type: OptionType.Text,
            label: "Max Connections Per File (For File Download)",
            valuePath: ["lftp", "num_max_connections_per_root_file"],
            description: "Number of connections for a single-file download.\n" +
                         "Corresponds to the 'pget:default-n' setting in Lftp."
        },
        {
            type: OptionType.Text,
            label: "Max Connections Per File (For Directory Download)",
            valuePath: ["lftp", "num_max_connections_per_dir_file"],
            description: "Number of per-file connections for a directory download.\n" +
                         "Corresponds to the 'mirror:use-pget-n' setting in Lftp."
        },
        {
            type: OptionType.Text,
            label: "Max Parallel Files (For Directory Download)",
            valuePath: ["lftp", "num_max_parallel_files_per_download"],
            description: "Maximum number of files to fetch in parallel for a single directory download.\n" +
                         "Corresponds to the 'mirror:parallel-transfer-count' setting in Lftp."
        }
    ]
};

export const OPTIONS_CONTEXT_OTHER: IOptionsContext = {
    header: "Other Settings",
    options: [
        {
            type: OptionType.Text,
            label: "Web GUI Port",
            valuePath: ["web", "port"],
            description: null
        },
        {
            type: OptionType.Checkbox,
            label: "Enable Debug",
            valuePath: ["general", "debug"],
            description: "Enables debug logging."
        },
    ]
};
