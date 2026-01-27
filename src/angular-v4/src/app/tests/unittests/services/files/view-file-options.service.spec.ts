import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {ViewFileOptionsService} from "../../../../services/files/view-file-options.service";
import {ViewFileOptions} from "../../../../services/files/view-file-options";
import {ViewFile} from "../../../../services/files/view-file";
import {LoggerService} from "../../../../services/utils/logger.service";
import {MockStorageService} from "../../../mocks/mock-storage.service";
import {LOCAL_STORAGE, StorageService} from "angular-webstorage-service";
import {StorageKeys} from "../../../../common/storage-keys";


function createViewOptionsService(): ViewFileOptionsService {
    return new ViewFileOptionsService(
        TestBed.get(LoggerService),
        TestBed.get(LOCAL_STORAGE)
    );
}


describe("Testing view file options service", () => {
    let viewOptionsService: ViewFileOptionsService;
    let storageService: StorageService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                ViewFileOptionsService,
                LoggerService,
                {provide: LOCAL_STORAGE, useClass: MockStorageService},
            ]
        });

        viewOptionsService = TestBed.get(ViewFileOptionsService);

        storageService = TestBed.get(LOCAL_STORAGE);
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
                expect(options.pinFilter).toBe(false);
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

    it("should load showDetails from storage", fakeAsync(() => {
        spyOn(storageService, "get").and.callFake(key => {
            if (key === StorageKeys.VIEW_OPTION_SHOW_DETAILS) {
                return true;
            }
        });
        // Recreate the service
        viewOptionsService = createViewOptionsService();
        expect(storageService.get).toHaveBeenCalledWith(StorageKeys.VIEW_OPTION_SHOW_DETAILS);

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
        expect(showDetails).toBe(true);
    }));

    it("should save showDetails to storage", fakeAsync(() => {
        spyOn(storageService, "set");
        viewOptionsService.setShowDetails(true);
        expect(storageService.set).toHaveBeenCalledWith(
            StorageKeys.VIEW_OPTION_SHOW_DETAILS,
            true
        );
        viewOptionsService.setShowDetails(false);
        expect(storageService.set).toHaveBeenCalledWith(
            StorageKeys.VIEW_OPTION_SHOW_DETAILS,
            false
        );
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

    it("should load sortMethod from storage", fakeAsync(() => {
        spyOn(storageService, "get").and.callFake(key => {
            if (key === StorageKeys.VIEW_OPTION_SORT_METHOD) {
                return ViewFileOptions.SortMethod.NAME_ASC;
            }
        });
        // Recreate the service
        viewOptionsService = createViewOptionsService();
        expect(storageService.get).toHaveBeenCalledWith(StorageKeys.VIEW_OPTION_SHOW_DETAILS);

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
        expect(sortMethod).toBe(ViewFileOptions.SortMethod.NAME_ASC);
    }));

    it("should save sortMethod to storage", fakeAsync(() => {
        spyOn(storageService, "set");
        viewOptionsService.setSortMethod(ViewFileOptions.SortMethod.NAME_ASC);
        expect(storageService.set).toHaveBeenCalledWith(
            StorageKeys.VIEW_OPTION_SORT_METHOD,
            ViewFileOptions.SortMethod.NAME_ASC
        );
        viewOptionsService.setSortMethod(ViewFileOptions.SortMethod.NAME_DESC);
        expect(storageService.set).toHaveBeenCalledWith(
            StorageKeys.VIEW_OPTION_SORT_METHOD,
            ViewFileOptions.SortMethod.NAME_DESC
        );
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

    it("should forward updates to pinFilter", fakeAsync(() => {
        let count = 0;
        let pinFilter = null;
        viewOptionsService.options.subscribe({
            next: options => {
                pinFilter = options.pinFilter;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);

        viewOptionsService.setPinFilter(true);
        tick();
        expect(pinFilter).toBe(true);
        expect(count).toBe(2);

        viewOptionsService.setPinFilter(false);
        tick();
        expect(pinFilter).toBe(false);
        expect(count).toBe(3);

        // Setting same value shouldn't trigger an update
        viewOptionsService.setPinFilter(false);
        tick();
        expect(pinFilter).toBe(false);
        expect(count).toBe(3);
    }));

    it("should load pinFilter from storage", fakeAsync(() => {
        spyOn(storageService, "get").and.callFake(key => {
            if (key === StorageKeys.VIEW_OPTION_PIN) {
                return true;
            }
        });
        // Recreate the service
        viewOptionsService = createViewOptionsService();
        expect(storageService.get).toHaveBeenCalledWith(StorageKeys.VIEW_OPTION_PIN);

        let count = 0;
        let pinFilter = null;
        viewOptionsService.options.subscribe({
            next: options => {
                pinFilter = options.pinFilter;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);
        expect(pinFilter).toBe(true);
    }));

    it("should save pinFilter to storage", fakeAsync(() => {
        spyOn(storageService, "set");
        viewOptionsService.setPinFilter(true);
        expect(storageService.set).toHaveBeenCalledWith(
            StorageKeys.VIEW_OPTION_PIN,
            true
        );
        viewOptionsService.setPinFilter(false);
        expect(storageService.set).toHaveBeenCalledWith(
            StorageKeys.VIEW_OPTION_PIN,
            false
        );
    }));
});
