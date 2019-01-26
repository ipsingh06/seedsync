import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {ViewFileOptionsService} from "../../../../services/files/view-file-options.service";



describe("Testing view file options service", () => {
    let viewOptionsService: ViewFileOptionsService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                ViewFileOptionsService,
            ]
        });

        viewOptionsService = TestBed.get(ViewFileOptionsService);
    });

    it("should create an instance", () => {
        expect(viewOptionsService).toBeDefined();
    });

    it("should forward default options", fakeAsync(() => {
        let count = 0;

        viewOptionsService.options.subscribe({
            next: options => {
                expect(options.showDetails).toBe(false);
                count++;
            }
        });

        tick();
        expect(count).toBe(1);
    }));


    it("should forward updates to showDetails", fakeAsync(() => {
        let count = 0;
        let showDetails = null;
        viewOptionsService.options.subscribe({
            next: options => {
                showDetails = options.showDetails;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);

        viewOptionsService.setShowDetails(true);
        tick();
        expect(showDetails).toBe(true);
        expect(count).toBe(2);

        viewOptionsService.setShowDetails(false);
        tick();
        expect(showDetails).toBe(false);
        expect(count).toBe(3);

        // Setting same value shouldn't trigger an update
        viewOptionsService.setShowDetails(false);
        tick();
        expect(showDetails).toBe(false);
        expect(count).toBe(3);
    }));
});
