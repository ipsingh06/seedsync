import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';

/**
 * DomService facilitates inter-component communication related
 * to DOM updates
 */
@Injectable({
    providedIn: 'root'
})
export class DomService {
    private headerHeightSubject = new BehaviorSubject<number>(0);

    get headerHeight(): Observable<number> {
        return this.headerHeightSubject.asObservable();
    }

    public setHeaderHeight(height: number): void {
        if (height !== this.headerHeightSubject.getValue()) {
            this.headerHeightSubject.next(height);
        }
    }
}
