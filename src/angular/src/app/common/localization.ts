export class Localization {
    static Error = class {
        public static readonly SERVER_DISCONNECTED = "Lost connection to the SeedSync service.";
    };

    static Notification = class {
        public static readonly CONFIG_RESTART = "Restart the app to apply new settings.";
        public static readonly CONFIG_VALUE_BLANK =
            (section: string, option: string) => `Setting ${section}.${option} cannot be blank.`

        public static readonly AUTOQUEUE_PATTERN_EMPTY = "Cannot add an empty autoqueue pattern.";

        public static readonly STATUS_REMOTE_SCAN_WAITING = "Waiting for remote server to respond...";
    };

    static Modal = class {
        public static readonly DELETE_LOCAL_TITLE = "Delete Local File";
        public static readonly DELETE_LOCAL_MESSAGE =
            (name: string) => `Are you sure you want to delete <b>${name}</b> from the local server?`

        public static readonly DELETE_REMOTE_TITLE = "Delete Remote File";
        public static readonly DELETE_REMOTE_MESSAGE =
            (name: string) => `Are you sure you want to delete <b>${name}</b> from the remote server?`
    };

    static Log = class {
        public static readonly CONNECTED = "Connected to service";
        public static readonly DISCONNECTED = "Lost connection to service";
    };
}
