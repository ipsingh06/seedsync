import { Injectable, inject } from '@angular/core';
import { Observable, BehaviorSubject, of } from 'rxjs';

import { Config, ConfigData } from './config';
import { LoggerService } from '../utils/logger.service';
import { BaseWebService } from '../base/base-web.service';
import { Localization } from '../../common/localization';
import { RestService, WebReaction } from '../utils/rest.service';

/**
 * ConfigService provides the store for the config
 */
@Injectable({
    providedIn: 'root'
})
export class ConfigService extends BaseWebService {
    private readonly CONFIG_GET_URL = '/server/config/get';
    private readonly CONFIG_SET_URL =
        (section: string, option: string, value: string) => `/server/config/set/${section}/${option}/${value}`;

    private configSubject = new BehaviorSubject<Config | null>(null);

    private restService = inject(RestService);
    private logger = inject(LoggerService);

    /**
     * Returns an observable that provides that latest Config
     */
    get config(): Observable<Config | null> {
        return this.configSubject.asObservable();
    }

    /**
     * Sets a value in the config
     */
    public set(section: string, option: string, value: unknown): Observable<WebReaction> {
        const valueStr = String(value);
        const currentConfig = this.configSubject.getValue();

        if (!currentConfig) {
            return of(new WebReaction(false, null, 'Config not loaded'));
        }

        // Check if section/option exists
        const configData = currentConfig as unknown as Record<string, Record<string, unknown>>;
        const sectionObj = configData[section];
        if (!sectionObj || typeof sectionObj !== 'object' || !(option in sectionObj)) {
            return of(new WebReaction(false, null, `Config has no option named ${section}.${option}`));
        }

        if (valueStr.length === 0) {
            return of(new WebReaction(
                false, null, Localization.Notification.CONFIG_VALUE_BLANK(section, option)
            ));
        }

        // Double-encode the value
        const valueEncoded = encodeURIComponent(encodeURIComponent(valueStr));
        const url = this.CONFIG_SET_URL(section, option, valueEncoded);
        const obs = this.restService.sendRequest(url);

        obs.subscribe({
            next: reaction => {
                if (reaction.success && currentConfig) {
                    // Update our copy and notify clients
                    const newSectionObj = { ...sectionObj, [option]: value };
                    const newConfig = new Config({
                        ...currentConfig,
                        [section]: newSectionObj
                    } as ConfigData);
                    this.configSubject.next(newConfig);
                }
            }
        });

        return obs;
    }

    protected onConnected(): void {
        // Retry the get
        this.getConfig();
    }

    protected onDisconnected(): void {
        // Send null config
        this.configSubject.next(null);
    }

    private getConfig(): void {
        this.logger.debug('Getting config...');
        this.restService.sendRequest(this.CONFIG_GET_URL).subscribe({
            next: reaction => {
                if (reaction.success && reaction.data) {
                    const configJson: ConfigData = JSON.parse(reaction.data);
                    this.configSubject.next(new Config(configJson));
                } else {
                    this.configSubject.next(null);
                }
            }
        });
    }
}
