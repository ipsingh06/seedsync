import {Injectable, NgZone} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";
import {HttpClient, HttpErrorResponse} from "@angular/common/http";

import * as Immutable from "immutable";

import {LoggerService} from "../common/logger.service";
import {ModelFile} from "./model-file";
import {BaseStreamService} from "../common/base-stream.service";


/**
 * ModelFileReaction encapsulates the response for an action
 * executed on the ModelFileService
 */
export class ModelFileReaction {
    readonly success: boolean;
    readonly errorMessage: string;

    constructor(success: boolean, errorMessage: string) {
        this.success = success;
        this.errorMessage = errorMessage;
    }
}


/**
 * ModelFileService class provides the store for model files
 * It implements the observable service pattern to push updates
 * as they become available.
 * The model is stored as an Immutable Map of name=>ModelFiles. Hence, the
 * ModelFiles have no defined order. The name key allows more efficient
 * lookup and model diffing.
 * Reference: http://blog.angular-university.io/how-to-build-angular2
 *            -apps-using-rxjs-observable-data-services-pitfalls-to-avoid
 */
@Injectable()
export class ModelFileService extends BaseStreamService {

    private readonly MODEL_STREAM_URL = "/server/model-stream";

    private _files: BehaviorSubject<Immutable.Map<string, ModelFile>> =
        new BehaviorSubject(Immutable.Map<string, ModelFile>());

    constructor(private _logger: LoggerService,
                private _http: HttpClient,
                _zone: NgZone) {
        super(_zone);

        this.streamUrl = this.MODEL_STREAM_URL;

        super.registerEvent("init");
        super.registerEvent("added");
        super.registerEvent("removed");
        super.registerEvent("updated");
    }

    protected onEvent(eventName: string, data: string) {
        this.parseEvent(eventName, data);
    }

    protected onError(err: any) {
        // Log the error
        this._logger.error("Error in model stream: %O", err);

        // Update clients by clearing the model
        this._files.next(this._files.getValue().clear());
    }

    /**
     * Parse an event and update the file model
     * @param {string} name
     * @param {string} data
     */
    private parseEvent(name: string, data: string) {
        this._logger.debug("Received event: " + name);
        if (name === "init") {
            // Init event receives an array of ModelFiles
            const parsed = JSON.parse(data);
            const newFiles: ModelFile[] = [];
            for (const file of parsed) {
                newFiles.push(new ModelFile(file));
            }
            // Replace the entire model
            const newMap = Immutable.Map<string, ModelFile>(newFiles.map(value => ([value.name, value])));
            this._files.next(newMap);
            this._logger.debug("New model: %O", this._files.getValue().toJS());
        } else if (name === "added") {
            // Added event receives old and new ModelFiles
            // Only new file is relevant
            const parsed: {new_file: any} = JSON.parse(data);
            const file = new ModelFile(parsed.new_file);
            if (this._files.getValue().has(file.name)) {
                this._logger.error("ModelFile named " + file.name + " already exists");
            } else {
                this._files.next(this._files.getValue().set(file.name, file));
                this._logger.debug("Added file: %O", file.toJS());
            }
        } else if (name === "removed") {
            // Removed event receives old and new ModelFiles
            // Only old file is relevant
            const parsed: {old_file: any} = JSON.parse(data);
            const file = new ModelFile(parsed.old_file);
            if (this._files.getValue().has(file.name)) {
                this._files.next(this._files.getValue().remove(file.name));
                this._logger.debug("Removed file: %O", file.toJS());
            } else {
                this._logger.error("Failed to find ModelFile named " + file.name);
            }
        } else if (name === "updated") {
            // Updated event received old and new ModelFiles
            // We will only use the new one here
            const parsed: {new_file: any} = JSON.parse(data);
            const file = new ModelFile(parsed.new_file);
            if (this._files.getValue().has(file.name)) {
                this._files.next(this._files.getValue().set(file.name, file));
                this._logger.debug("Updated file: %O", file.toJS());
            } else {
                this._logger.error("Failed to find ModelFile named " + file.name);
            }
        }
    }

    get files(): Observable<Immutable.Map<string, ModelFile>> {
        return this._files.asObservable();
    }

    /**
     * Queue a file for download
     * @param {ModelFile} file
     * @returns {Observable<ModelFileReaction>}
     */
    public queue(file: ModelFile): Observable<ModelFileReaction> {
        this._logger.debug("Queue model file: " + file.name);
        // Double-encode the value
        const fileNameEncoded = encodeURIComponent(encodeURIComponent(file.name));
        const url: string = "/server/command/queue/" + fileNameEncoded;
        return this.sendRequest(url);
    }

    /**
     * Stop a file
     * @param {ModelFile} file
     * @returns {Observable<ModelFileReaction>}
     */
    public stop(file: ModelFile): Observable<ModelFileReaction> {
        this._logger.debug("Stop model file: " + file.name);
        // Double-encode the value
        const fileNameEncoded = encodeURIComponent(encodeURIComponent(file.name));
        const url: string = "/server/command/stop/" + fileNameEncoded;
        return this.sendRequest(url);
    }

    /**
     * Helper method to send backend a request and generate a ModelFileReaction response
     * @param {string} url
     * @returns {Observable<ModelFileReaction>}
     */
    private sendRequest(url: string): Observable<ModelFileReaction> {
        return Observable.create(observer => {
            this._http.get(url, {responseType: "text"}).subscribe(
                data => {
                    this._logger.debug("Http response: " + data);
                    observer.next(new ModelFileReaction(true, null));
                },
                (err: HttpErrorResponse) => {
                    let errorMessage = null;
                    if (err.error instanceof Error) {
                        // A client-side or network error occurred. Handle it accordingly.
                        this._logger.error("Http client error: " + err.error.message);
                        errorMessage = "HTTP client-side error";
                    } else {
                        // The backend returned an unsuccessful response code.
                        // The response body may contain clues as to what went wrong,
                        this._logger.error("Http request returned code %d, body was: %O", err.status, err.error);
                        errorMessage = err.error;
                    }
                    observer.next(new ModelFileReaction(false, errorMessage));
                }
            );
        });
    }
}

/**
 * ModelFileService factory and provider
 */
export let modelFileServiceFactory = (
        _logger: LoggerService,
        _http: HttpClient,
        _zone: NgZone) => {
    const modelFileService = new ModelFileService(_logger, _http, _zone);
    modelFileService.onInit();
    return modelFileService;
};

// noinspection JSUnusedGlobalSymbols
export let ModelFileServiceProvider = {
    provide: ModelFileService,
    useFactory: modelFileServiceFactory,
    deps: [LoggerService, HttpClient, NgZone]
};
