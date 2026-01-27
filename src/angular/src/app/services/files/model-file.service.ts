import { Injectable, inject } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';

import { LoggerService } from '../utils/logger.service';
import { ModelFile, ModelFileJson } from './model-file';
import { BaseStreamService } from '../base/base-stream.service';
import { RestService, WebReaction } from '../utils/rest.service';

/**
 * ModelFileService class provides the store for model files
 * It implements the observable service pattern to push updates
 * as they become available.
 * The model is stored as a Map of name=>ModelFiles.
 */
@Injectable({
    providedIn: 'root'
})
export class ModelFileService extends BaseStreamService {
    private readonly EVENT_INIT = 'model-init';
    private readonly EVENT_ADDED = 'model-added';
    private readonly EVENT_UPDATED = 'model-updated';
    private readonly EVENT_REMOVED = 'model-removed';

    private filesSubject = new BehaviorSubject<Map<string, ModelFile>>(new Map());

    private logger = inject(LoggerService);
    private restService = inject(RestService);

    constructor() {
        super();
        this.registerEventName(this.EVENT_INIT);
        this.registerEventName(this.EVENT_ADDED);
        this.registerEventName(this.EVENT_UPDATED);
        this.registerEventName(this.EVENT_REMOVED);
    }

    get files(): Observable<Map<string, ModelFile>> {
        return this.filesSubject.asObservable();
    }

    /**
     * Queue a file for download
     */
    public queue(file: ModelFile): Observable<WebReaction> {
        this.logger.debug('Queue model file: ' + file.name);
        // Double-encode the value
        const fileNameEncoded = encodeURIComponent(encodeURIComponent(file.name));
        const url = '/server/command/queue/' + fileNameEncoded;
        return this.restService.sendRequest(url);
    }

    /**
     * Stop a file
     */
    public stop(file: ModelFile): Observable<WebReaction> {
        this.logger.debug('Stop model file: ' + file.name);
        // Double-encode the value
        const fileNameEncoded = encodeURIComponent(encodeURIComponent(file.name));
        const url = '/server/command/stop/' + fileNameEncoded;
        return this.restService.sendRequest(url);
    }

    /**
     * Extract a file
     */
    public extract(file: ModelFile): Observable<WebReaction> {
        this.logger.debug('Extract model file: ' + file.name);
        // Double-encode the value
        const fileNameEncoded = encodeURIComponent(encodeURIComponent(file.name));
        const url = '/server/command/extract/' + fileNameEncoded;
        return this.restService.sendRequest(url);
    }

    /**
     * Delete file locally
     */
    public deleteLocal(file: ModelFile): Observable<WebReaction> {
        this.logger.debug('Delete locally model file: ' + file.name);
        // Double-encode the value
        const fileNameEncoded = encodeURIComponent(encodeURIComponent(file.name));
        const url = '/server/command/delete_local/' + fileNameEncoded;
        return this.restService.sendRequest(url);
    }

    /**
     * Delete file remotely
     */
    public deleteRemote(file: ModelFile): Observable<WebReaction> {
        this.logger.debug('Delete remotely model file: ' + file.name);
        // Double-encode the value
        const fileNameEncoded = encodeURIComponent(encodeURIComponent(file.name));
        const url = '/server/command/delete_remote/' + fileNameEncoded;
        return this.restService.sendRequest(url);
    }

    protected onEvent(eventName: string, data: string): void {
        this.parseEvent(eventName, data);
    }

    protected onConnected(): void {
        // nothing to do
    }

    protected onDisconnected(): void {
        // Update clients by clearing the model
        this.filesSubject.next(new Map());
    }

    /**
     * Parse an event and update the file model
     */
    private parseEvent(name: string, data: string): void {
        if (name === this.EVENT_INIT) {
            // Init event receives an array of ModelFiles
            let t0: number;
            let t1: number;

            t0 = performance.now();
            const parsed: ModelFileJson[] = JSON.parse(data);
            t1 = performance.now();
            this.logger.debug('Parsing took', (t1 - t0).toFixed(0), 'ms');

            t0 = performance.now();
            const newFiles: ModelFile[] = [];
            for (const file of parsed) {
                newFiles.push(ModelFile.fromJson(file));
            }
            t1 = performance.now();
            this.logger.debug('ModelFile creation took', (t1 - t0).toFixed(0), 'ms');

            // Replace the entire model
            t0 = performance.now();
            const newMap = new Map<string, ModelFile>(newFiles.map(value => [value.name, value]));
            t1 = performance.now();
            this.logger.debug('ModelFile map creation took', (t1 - t0).toFixed(0), 'ms');

            this.filesSubject.next(newMap);
        } else if (name === this.EVENT_ADDED) {
            // Added event receives old and new ModelFiles
            // Only new file is relevant
            const parsed: { new_file: ModelFileJson } = JSON.parse(data);
            const file = ModelFile.fromJson(parsed.new_file);
            const currentMap = this.filesSubject.getValue();
            if (currentMap.has(file.name)) {
                this.logger.error('ModelFile named ' + file.name + ' already exists');
            } else {
                const newMap = new Map(currentMap);
                newMap.set(file.name, file);
                this.filesSubject.next(newMap);
                this.logger.debug('Added file:', file);
            }
        } else if (name === this.EVENT_REMOVED) {
            // Removed event receives old and new ModelFiles
            // Only old file is relevant
            const parsed: { old_file: ModelFileJson } = JSON.parse(data);
            const file = ModelFile.fromJson(parsed.old_file);
            const currentMap = this.filesSubject.getValue();
            if (currentMap.has(file.name)) {
                const newMap = new Map(currentMap);
                newMap.delete(file.name);
                this.filesSubject.next(newMap);
                this.logger.debug('Removed file:', file);
            } else {
                this.logger.error('Failed to find ModelFile named ' + file.name);
            }
        } else if (name === this.EVENT_UPDATED) {
            // Updated event received old and new ModelFiles
            // We will only use the new one here
            const parsed: { new_file: ModelFileJson } = JSON.parse(data);
            const file = ModelFile.fromJson(parsed.new_file);
            const currentMap = this.filesSubject.getValue();
            if (currentMap.has(file.name)) {
                const newMap = new Map(currentMap);
                newMap.set(file.name, file);
                this.filesSubject.next(newMap);
                this.logger.debug('Updated file:', file);
            } else {
                this.logger.error('Failed to find ModelFile named ' + file.name);
            }
        } else {
            this.logger.error('Unrecognized event:', name);
        }
    }
}
