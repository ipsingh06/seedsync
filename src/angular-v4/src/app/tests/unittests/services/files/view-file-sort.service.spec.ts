import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {LoggerService} from "../../../../services/utils/logger.service";
import {ViewFileSortService} from "../../../../services/files/view-file-sort.service";
import {MockViewFileService} from "../../../mocks/mock-view-file.service";
import {MockViewFileOptionsService} from "../../../mocks/mock-view-file-options.service";
import {ViewFileComparator, ViewFileService} from "../../../../services/files/view-file.service";
import {ViewFileOptionsService} from "../../../../services/files/view-file-options.service";
import {ViewFileOptions} from "../../../../services/files/view-file-options";
import {ViewFile} from "../../../../services/files/view-file";


describe("Testing view file sort service", () => {
    let viewSortService: ViewFileSortService;

    let viewFileService: MockViewFileService;
    let viewFileOptionsService: MockViewFileOptionsService;
    let sortComparator: ViewFileComparator;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                ViewFileSortService,
                LoggerService,
                {provide: ViewFileService, useClass: MockViewFileService},
                {provide: ViewFileOptionsService, useClass: MockViewFileOptionsService}
            ]
        });
        viewFileService = TestBed.get(ViewFileService);
        spyOn(viewFileService, "setComparator").and.callFake(
            value => sortComparator = value
        );

        viewFileOptionsService = TestBed.get(ViewFileOptionsService);

        viewSortService = TestBed.get(ViewFileSortService);
    });

    it("should create an instance", () => {
        expect(viewSortService).toBeDefined();
    });

    it("does not set a sort comparator by default", () => {
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(0);
        expect(sortComparator).toBeUndefined();
    });

    it("calls setComparator when sort method is changed", fakeAsync(() => {
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.STATUS
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(1);
        expect(sortComparator).not.toBeNull();
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.NAME_ASC
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(2);
        expect(sortComparator).not.toBeNull();
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.NAME_DESC
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(3);
        expect(sortComparator).not.toBeNull();
    }));

    it("does not call setComparator on duplicate sort methods", fakeAsync(() => {
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.STATUS
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(1);
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.STATUS
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(1);
    }));

    it("does not call setComparator when a different option is changed", fakeAsync(() => {
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.STATUS,
            showDetails: false,
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(1);
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.STATUS,
            showDetails: true,
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(1);
    }));

    it("correctly sorts by status", fakeAsync(() => {
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.STATUS
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(1);
        expect(sortComparator).not.toBeNull();

        // Check the order based on status
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTING}),
            new ViewFile({status: ViewFile.Status.DOWNLOADING})
        )).toBeLessThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.DOWNLOADING}),
            new ViewFile({status: ViewFile.Status.QUEUED})
        )).toBeLessThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.QUEUED}),
            new ViewFile({status: ViewFile.Status.EXTRACTED})
        )).toBeLessThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED}),
            new ViewFile({status: ViewFile.Status.DOWNLOADED})
        )).toBeLessThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.DOWNLOADED}),
            new ViewFile({status: ViewFile.Status.STOPPED})
        )).toBeLessThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.STOPPED}),
            new ViewFile({status: ViewFile.Status.DEFAULT})
        )).toBeLessThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.STOPPED}),
            new ViewFile({status: ViewFile.Status.DELETED})
        )).toBeLessThan(0);

        // Default and Deleted should be intermixed
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.DEFAULT, name: ""}),
            new ViewFile({status: ViewFile.Status.DELETED, name: ""})
        )).toBe(0);

        // Given same status, order should be determined by ascending name
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "flower"}),
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "tofu"})
        )).toBeLessThan(0);
    }));

    it("correctly sorts by ascending name", fakeAsync(() => {
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.NAME_ASC
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(1);
        expect(sortComparator).not.toBeNull();

        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "flower"}),
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "tofu"})
        )).toBeLessThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "cat"}),
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "dog"})
        )).toBeLessThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "fff"}),
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "ffff"})
        )).toBeLessThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "aaaa"}),
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "aaaa"})
        )).toBe(0);
    }));

    it("correctly sorts by descending name", fakeAsync(() => {
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            sortMethod: ViewFileOptions.SortMethod.NAME_DESC
        }));
        tick();
        expect(viewFileService.setComparator).toHaveBeenCalledTimes(1);
        expect(sortComparator).not.toBeNull();

        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "flower"}),
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "tofu"})
        )).toBeGreaterThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "cat"}),
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "dog"})
        )).toBeGreaterThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "fff"}),
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "ffff"})
        )).toBeGreaterThan(0);
        expect(sortComparator(
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "aaaa"}),
            new ViewFile({status: ViewFile.Status.EXTRACTED, name: "aaaa"})
        )).toBe(0);
    }));
});

