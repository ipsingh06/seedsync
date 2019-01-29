import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {DomService} from "../../../../services/utils/dom.service";



describe("Testing view file options service", () => {
    let domService: DomService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                DomService,
            ]
        });

        domService = TestBed.get(DomService);
    });

    it("should create an instance", () => {
        expect(domService).toBeDefined();
    });

    it("should forward updates to headerHeight", fakeAsync(() => {
        let count = 0;
        let headerHeight = null;
        domService.headerHeight.subscribe({
            next: height => {
                headerHeight = height;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);

        domService.setHeaderHeight(10);
        tick();
        expect(headerHeight).toBe(10);
        expect(count).toBe(2);

        domService.setHeaderHeight(20);
        tick();
        expect(headerHeight).toBe(20);
        expect(count).toBe(3);

        // Setting same value shouldn't trigger an update
        domService.setHeaderHeight(20);
        tick();
        expect(headerHeight).toBe(20);
        expect(count).toBe(3);
    }));
});
