import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {ViewFileOptionsService} from "../../../../services/files/view-file-options.service";
import {ViewFileOptions} from "../../../../services/files/view-file-options";
import {ViewFile} from "../../../../services/files/view-file";
import {LoggerService} from "../../../../services/utils/logger.service";



describe("Testing view file options service", () => {
    let viewOptionsService: ViewFileOptionsService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                ViewFileOptionsService,
                LoggerService,
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
                expect(options.sortMethod).toBe(ViewFileOptions.SortMethod.STATUS);
                expect(options.selectedStatusFilter).toBeNull();
                expect(options.nameFilter).toBeNull();
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

    it("should forward updates to sortMethod", fakeAsync(() => {
        let count = 0;
        let sortMethod = null;
        viewOptionsService.options.subscribe({
            next: options => {
                sortMethod = options.sortMethod;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);

        viewOptionsService.setSortMethod(ViewFileOptions.SortMethod.NAME_ASC);
        tick();
        expect(sortMethod).toBe(ViewFileOptions.SortMethod.NAME_ASC);
        expect(count).toBe(2);

        viewOptionsService.setSortMethod(ViewFileOptions.SortMethod.NAME_DESC);
        tick();
        expect(sortMethod).toBe(ViewFileOptions.SortMethod.NAME_DESC);
        expect(count).toBe(3);

        // Setting same value shouldn't trigger an update
        viewOptionsService.setSortMethod(ViewFileOptions.SortMethod.NAME_DESC);
        tick();
        expect(sortMethod).toBe(ViewFileOptions.SortMethod.NAME_DESC);
        expect(count).toBe(3);
    }));

    it("should forward updates to selectedStatusFilter", fakeAsync(() => {
        let count = 0;
        let selectedStatusFilter = null;
        viewOptionsService.options.subscribe({
            next: options => {
                selectedStatusFilter = options.selectedStatusFilter;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);

        viewOptionsService.setSelectedStatusFilter(ViewFile.Status.EXTRACTED);
        tick();
        expect(selectedStatusFilter).toBe(ViewFile.Status.EXTRACTED);
        expect(count).toBe(2);

        viewOptionsService.setSelectedStatusFilter(ViewFile.Status.QUEUED);
        tick();
        expect(selectedStatusFilter).toBe(ViewFile.Status.QUEUED);
        expect(count).toBe(3);

        // Setting same value shouldn't trigger an update
        viewOptionsService.setSelectedStatusFilter(ViewFile.Status.QUEUED);
        tick();
        expect(selectedStatusFilter).toBe(ViewFile.Status.QUEUED);
        expect(count).toBe(3);

        // Null should be allowed
        viewOptionsService.setSelectedStatusFilter(null);
        tick();
        expect(selectedStatusFilter).toBeNull();
        expect(count).toBe(4);
    }));

    it("should forward updates to nameFilter", fakeAsync(() => {
        let count = 0;
        let nameFilter = null;
        viewOptionsService.options.subscribe({
            next: options => {
                nameFilter = options.nameFilter;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);

        viewOptionsService.setNameFilter("tofu");
        tick();
        expect(nameFilter).toBe("tofu");
        expect(count).toBe(2);

        viewOptionsService.setNameFilter("flower");
        tick();
        expect(nameFilter).toBe("flower");
        expect(count).toBe(3);

        // Setting same value shouldn't trigger an update
        viewOptionsService.setNameFilter("flower");
        tick();
        expect(nameFilter).toBe("flower");
        expect(count).toBe(3);

        // Null should be allowed
        viewOptionsService.setNameFilter(null);
        tick();
        expect(nameFilter).toBeNull();
        expect(count).toBe(4);
    }));
});
