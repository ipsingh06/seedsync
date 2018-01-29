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
            description: "Path to your files on the remote server"
        },
        {
            type: OptionType.Text,
            label: "Local Directory",
            valuePath: ["lftp", "local_path"],
            description: "Downloaded files are placed here"
        },
        {
            type: OptionType.Text,
            label: "Remote SSH Port",
            valuePath: ["lftp", "remote_port"],
            description: null,
        },
        {
            type: OptionType.Text,
            label: "Server Script Path",
            valuePath: ["lftp", "remote_path_to_scan_script"],
            description: "Where to install scanner script on remote server"
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
            description: "How often the remote server is scanned for new files"
        },
        {
            type: OptionType.Text,
            label: "Local Scan Interval (ms)",
            valuePath: ["controller", "interval_ms_local_scan"],
            description: "How often the local directory is scanned"
        },
        {
            type: OptionType.Text,
            label: "Downloading Scan Interval (ms)",
            valuePath: ["controller", "interval_ms_downloading_scan"],
            description: "How often the downloading information is updated"
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
            description: "How many items download in parallel.\n" +
                         "(cmd:queue-parallel)"
        },
        {
            type: OptionType.Text,
            label: "Max Total Connections",
            valuePath: ["lftp", "num_max_total_connections"],
            description: "Maximum number of connections.\n" +
                         "(net:connection-limit)"
        },
        {
            type: OptionType.Text,
            label: "Max Connections Per File (Single-File)",
            valuePath: ["lftp", "num_max_connections_per_root_file"],
            description: "Number of connections for single-file download.\n" +
                         "(pget:default-n)"
        },
        {
            type: OptionType.Text,
            label: "Max Connections Per File (Directory)",
            valuePath: ["lftp", "num_max_connections_per_dir_file"],
            description: "Number of per-file connections for directory download.\n" +
                         "(mirror:use-pget-n)"
        },
        {
            type: OptionType.Text,
            label: "Max Parallel Files (Directory)",
            valuePath: ["lftp", "num_max_parallel_files_per_download"],
            description: "Maximum number of files to fetch in parallel for single directory download.\n" +
                         "(mirror:parallel-transfer-count)"
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

export const OPTIONS_CONTEXT_AUTOQUEUE: IOptionsContext = {
    header: "AutoQueue",
    options: [
        {
            type: OptionType.Checkbox,
            label: "Enable AutoQueue",
            valuePath: ["autoqueue", "enabled"],
            description: null
        },
        {
            type: OptionType.Checkbox,
            label: "Restrict to patterns",
            valuePath: ["autoqueue", "patterns_only"],
            description: "Only autoqueue files that match a pattern"
        },
    ]
};

export const OPTIONS_CONTEXT_EXTRACT: IOptionsContext = {
    header: "Archive Extraction",
    options: [
        {
            type: OptionType.Checkbox,
            label: "Extract archives in the downloads directory",
            valuePath: ["controller", "use_local_path_as_extract_path"],
            description: null
        },
        {
            type: OptionType.Text,
            label: "Extract Path",
            valuePath: ["controller", "extract_path"],
            description: "When option above is disabled, extract archives to this directory"
        },
    ]
};
