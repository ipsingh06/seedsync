import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";


/**
 * DomService facilitates inter-component communication related
 * to DOM updates
 */
@Injectable()
export class DomService {
    private _headerHeight: BehaviorSubject<number> = new BehaviorSubject(0);

    get headerHeight(): Observable<number>{
        return this._headerHeight.asObservable();
    }

    public setHeaderHeight(height: number) {
        if(height !== this._headerHeight.getValue()) {
            this._headerHeight.next(height);
        }
    }

}
