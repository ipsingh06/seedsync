import {Injectable} from "@angular/core";

import * as compareVersions from "compare-versions";

import {RestService} from "./rest.service";
import {LoggerService} from "./logger.service";
import {NotificationService} from "./notification.service";
import {Notification} from "./notification";
import {Localization} from "../../common/localization";

declare function require(moduleName: string): any;
const { version: appVersion } = require("../../../../package.json");


/**
 * VersionCheckService checks for the latest version and
 * triggers a notification
 */
@Injectable()
export class VersionCheckService {
    private readonly GITHUB_LATEST_RELEASE_URL =
        "https://api.github.com/repos/ipsingh06/seedsync/releases/latest";

    constructor(private _restService: RestService,
                private _notifService: NotificationService,
                private _logger: LoggerService) {
        this.checkVersion();
    }

    private checkVersion() {
        this._restService.sendRequest(this.GITHUB_LATEST_RELEASE_URL).subscribe({
            next: reaction => {
                if (reaction.success) {
                    let jsonResponse;
                    let latestVersion;
                    let url;
                    try {
                        jsonResponse = JSON.parse(reaction.data);
                        latestVersion = jsonResponse.tag_name;
                        url = jsonResponse.html_url;
                    } catch (e) {
                        this._logger.error("Unable to parse github response: %O", e);
                        return;
                    }
                    const message = Localization.Notification.NEW_VERSION_AVAILABLE(url);
                    this._logger.debug("Latest version: ", message);
                    if (VersionCheckService.isVersionNewer(latestVersion)) {
                        const notif = new Notification({
                            level: Notification.Level.INFO,
                            dismissible: true,
                            text: message
                        });
                        this._notifService.show(notif);
                    }
                } else {
                    this._logger.warn("Unable to fetch latest version info: %O", reaction);
                }
            }
        });
    }

    private static isVersionNewer(version: string): boolean {
        // Remove the 'v' at the beginning, if any
        version = version.replace(/^v/, "");
        // Replace - with .
        version = version.replace(/-/g, ".");
        return compareVersions(version, appVersion) > 0;
    }
}
