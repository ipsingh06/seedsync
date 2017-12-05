export class Localization {
    static Error = class {
        public static readonly SERVER_DISCONNECTED = "Lost connection to the server."
    };

    static Notification = class {
        public static readonly CONFIG_RESTART = "Restart the app to apply new settings."
        public static readonly CONFIG_VALUE_BLANK =
            (section: string, option: string) => `Setting ${section}.${option} cannot be blank.`
    };
}
