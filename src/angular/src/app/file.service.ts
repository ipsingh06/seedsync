import {Injectable} from '@angular/core';
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import {List} from 'immutable';

import {ModelFile} from './model-file'


/**
 * FileService class provides the store for model files
 * It implements the observable service pattern to push updates
 * as they become available.
 * Reference: http://blog.angular-university.io/how-to-build-angular2
 *            -apps-using-rxjs-observable-data-services-pitfalls-to-avoid
 */
@Injectable()
export class FileService {

    private readonly EVENT_URL = "/stream";

    private _files: BehaviorSubject<List<ModelFile>> = new BehaviorSubject(List([]));

    constructor() {
        this.init();
    }

    private init() {
        // Add a EventSource observable to receive file list and updates
        // from the backend
        // Observable-SSE code from https://stackoverflow.com/a/36827897/8571324
        let _fileService = this;

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

            eventSource.onerror = x => observer.error(x);

            return () => {
                eventSource.close();
            };
        });
        observable.subscribe({
            next: (x) => _fileService.parseEvent(x["event"], x["data"]),
            error: err => console.error("SSE Error: " + err)
        });
    }

    /**
     * Parse an event and update the file model
     * @param {string} name
     * @param {string} data
     */
    private parseEvent(name: string, data: string) {
        console.debug("Received event: " + name);
        if(name == "init") {
            let newFiles: ModelFile[] = JSON.parse(data);
            this._files.next(List(newFiles))
        } else if(name == "added") {

        }
    }

    get files() {
        return new Observable(fn => this._files.subscribe(fn));
    }

}
