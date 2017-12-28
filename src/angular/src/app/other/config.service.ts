import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";
import {HttpClient} from "@angular/common/http";

import {Config, IConfig} from "./config";
import {LoggerService} from "../common/logger.service";
import {BaseWebService, WebReaction} from "../common/base-web.service";
import {ServerStatusService} from "./server-status.service";
import {Localization} from "../common/localization";


/**
 * ConfigService provides the store for the config
 */
@Injectable()
export class ConfigService extends BaseWebService {
    private readonly CONFIG_GET_URL = "/server/config/get";
    private readonly CONFIG_SET_URL =
        (section, option, value) => `/server/config/set/${section}/${option}/${value}`

    private _config: BehaviorSubject<Config> = new BehaviorSubject(null);

    constructor(_statusService: ServerStatusService,
                _logger: LoggerService,
                _http: HttpClient) {
        super(_statusService, _logger, _http);
    }

    /**
     * Returns an observable that provides that latest Config
     * @returns {Observable<Config>}
     */
    get config(): Observable<Config> {
        return this._config.asObservable();
    }

    /**
     * Sets a value in the config
     * @param {string} section
     * @param {string} option
     * @param value
     * @returns {WebReaction}
     */
    public set(section: string, option: string, value: any): Observable<WebReaction> {
        const valueStr: string = value;
        const currentConfig = this._config.getValue();
        if (!currentConfig.has(section) || !currentConfig.get(section).has(option)) {
            return Observable.create(observer => {
                observer.next(new WebReaction(false, null, `Config has no option named ${section}.${option}`));
            });
        } else if (valueStr.length === 0) {
            return Observable.create(observer => {
                observer.next(new WebReaction(
                    false, null, Localization.Notification.CONFIG_VALUE_BLANK(section, option))
                );
            });
        } else {
            // Double-encode the value
            const valueEncoded = encodeURIComponent(encodeURIComponent(valueStr));
            const url = this.CONFIG_SET_URL(section, option, valueEncoded);
            const obs = this.sendRequest(url);
            obs.subscribe({
                next: reaction => {
                    if (reaction.success) {
                        // Update our copy and notify clients
                        const config = this._config.getValue();
                        const newConfig = new Config(config.updateIn([section, option], (_) => value));
                        this._config.next(newConfig);
                    }
                }
            });
            return obs;
        }
    }

    protected onConnectedChanged(connected: boolean): void {
        if (connected) {
            // Retry the get
            this.getConfig();
        } else {
            // Send null config
            this._config.next(null);
        }
    }

    private getConfig() {
        this._logger.debug("Getting config...");
        this.sendRequest(this.CONFIG_GET_URL).subscribe({
            next: reaction => {
                if (reaction.success) {
                    const config_json: IConfig = JSON.parse(reaction.data);
                    this._config.next(new Config(config_json));
                } else {
                    this._config.next(null);
                }
            }
        });
    }
}

/**
 * ConfigService factory and provider
 */
export let configServiceFactory = (
    _statusService: ServerStatusService,
    _logger: LoggerService,
    _http: HttpClient) => {
  const configService = new ConfigService(_statusService, _logger, _http);
  configService.onInit();
  return configService;
};

// noinspection JSUnusedGlobalSymbols
export let ConfigServiceProvider = {
    provide: ConfigService,
    useFactory: configServiceFactory,
    deps: [ServerStatusService, LoggerService, HttpClient]
};
