import {Injectable} from '@angular/core';
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";
import {HttpClient, HttpErrorResponse} from '@angular/common/http';

import * as Immutable from 'immutable';

import {LoggerService} from "../common/logger.service";
import {ModelFile} from './model-file'


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
export class ModelFileService {

    private readonly EVENT_URL = "/stream";

    private _files: BehaviorSubject<Immutable.Map<string, ModelFile>> =
        new BehaviorSubject(Immutable.Map<string, ModelFile>());

    constructor(private _logger: LoggerService,
                private _http: HttpClient) {
        this.init();
    }

    private init() {
        // Add a EventSource observable to receive file list and updates
        // from the backend
        // Observable-SSE code from https://stackoverflow.com/a/36827897/8571324
        let _modelFileService = this;

        /**
         * Helper function to add an event listener to an event source
         * Forwards the event and its data to the observer's next method
         * @param {string} eventName
         * @param eventSource
         * @param observer
         */
        function addEventListener(eventName: string, eventSource, observer) {
            eventSource.addEventListener(eventName, event => observer.next(
                {
                    "event": eventName,
                    "data": event.data
                }
            ));
        }
        const observable = Observable.create(observer => {
            const eventSource = new EventSource(this.EVENT_URL);
            addEventListener("init", eventSource, observer);
            addEventListener("added", eventSource, observer);
            addEventListener("removed", eventSource, observer);
            addEventListener("updated", eventSource, observer);

            eventSource.onerror = x => observer.error(x);

            return () => {
                eventSource.close();
            };
        });
        observable.subscribe({
            next: (x) => _modelFileService.parseEvent(x["event"], x["data"]),
            error: err => this._logger.error("SSE Error: " + err)
        });
    }

    /**
     * Parse an event and update the file model
     * @param {string} name
     * @param {string} data
     */
    private parseEvent(name: string, data: string) {
        this._logger.debug("Received event: " + name);
        if(name == "init") {
            // Init event receives an array of ModelFiles
            let parsed = JSON.parse(data);
            let newFiles: ModelFile[] = [];
            for(let file of parsed) {
                newFiles.push(new ModelFile(file));
            }
            // Replace the entire model
            let newMap = Immutable.Map<string, ModelFile>(newFiles.map(value => ([value.name, value])));
            this._files.next(newMap);
            this._logger.debug("New model: %O", this._files.getValue().toJS());
        } else if(name == "added") {
            // Added event receives old and new ModelFiles
            // Only new file is relevant
            let parsed: {new_file: any} = JSON.parse(data);
            let file = new ModelFile(parsed.new_file);
            if(this._files.getValue().has(file.name)) {
                this._logger.error("ModelFile named " + file.name + " already exists")
            } else {
                this._files.next(this._files.getValue().set(file.name, file));
                this._logger.debug("Added file: %O", file.toJS());
            }
        } else if(name == "removed") {
            // Removed event receives old and new ModelFiles
            // Only old file is relevant
            let parsed: {old_file: any} = JSON.parse(data);
            let file = new ModelFile(parsed.old_file);
            if(this._files.getValue().has(file.name)) {
                this._files.next(this._files.getValue().remove(file.name));
                this._logger.debug("Removed file: %O", file.toJS());
            } else {
                this._logger.error("Failed to find ModelFile named " + file.name);
            }
        } else if(name == "updated") {
            // Updated event received old and new ModelFiles
            // We will only use the new one here
            let parsed: {new_file: any} = JSON.parse(data);
            let file = new ModelFile(parsed.new_file);
            if(this._files.getValue().has(file.name)) {
                this._files.next(this._files.getValue().set(file.name, file));
                this._logger.debug("Updated file: %O", file.toJS());
            } else {
                this._logger.error("Failed to find ModelFile named " + file.name);
            }
        }
    }

    get files() : Observable<Immutable.Map<string, ModelFile>> {
        return this._files.asObservable();
    }

    /**
     * Queue a file for download
     * @param {ModelFile} file
     * @returns {Observable<ModelFileReaction>}
     */
    public queue(file: ModelFile): Observable<ModelFileReaction> {
        this._logger.debug("Queue model file: " + file.name);
        let url: string = "/queue/" + file.name;
        return this.sendRequest(url);
    }

    /**
     * Stop a file
     * @param {ModelFile} file
     * @returns {Observable<ModelFileReaction>}
     */
    public stop(file: ModelFile): Observable<ModelFileReaction> {
        this._logger.debug("Stop model file: " + file.name);
        let url: string = "/stop/" + file.name;
        return this.sendRequest(url);
    }

    /**
     * Helper method to send backend a request and generate a ModelFileReaction response
     * @param {string} url
     * @returns {Observable<ModelFileReaction>}
     */
    private sendRequest(url: string): Observable<ModelFileReaction> {
        return Observable.create(observer => {
            this._http.get(url, {responseType: 'text'}).subscribe(
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
                        this._logger.error(`Http request returned code ${err.status}, body was: ${err.error}`);
                        errorMessage = err.error;
                    }
                    observer.next(new ModelFileReaction(false, errorMessage));
                }
            );
        });
    }
}
