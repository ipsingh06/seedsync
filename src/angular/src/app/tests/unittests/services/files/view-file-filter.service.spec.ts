import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import * as Immutable from "immutable";

import {ViewFileFilterService} from "../../../../services/files/view-file-filter.service";
import {LoggerService} from "../../../../services/utils/logger.service";
import {ViewFileFilterCriteria, ViewFileService} from "../../../../services/files/view-file.service";
import {MockViewFileService} from "../../../mocks/mock-view-file.service";
import {ViewFile} from "../../../../services/files/view-file";
import {ViewFileFilter} from "../../../../services/files/view-file-filter";


describe("Testing view file filter service", () => {
    let viewFilterService: ViewFileFilterService;

    let viewFileService: MockViewFileService;
    let filterCriteria: ViewFileFilterCriteria;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                ViewFileFilterService,
                LoggerService,
                {provide: ViewFileService, useClass: MockViewFileService}
            ]
        });
        viewFileService = TestBed.get(ViewFileService);
        spyOn(viewFileService, "setFilterCriteria").and.callFake(
            value => filterCriteria = value
        );
        spyOn(viewFileService, "reapplyFilters");

        viewFilterService = TestBed.get(ViewFileFilterService);
    });

    it("should create an instance", () => {
        expect(viewFilterService).toBeDefined();
    });

    it("sets a filter criteria by default", () => {
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
        expect(filterCriteria).toBeDefined();
    });

    it("calls reapplyFilters on filterName", () => {
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(0);
        viewFilterService.filterName("something");
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(1);
    });

    it("does not calls reapplyFilter on duplicate filterName", () => {
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(0);
        viewFilterService.filterName("something");
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(1);
        viewFilterService.filterName("something");
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(1);
    });

    it("filters by name correctly", () => {
        viewFilterService.filterName("tofu");
        // exact match
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "tofu"}))).toBe(true);
        // no match
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flower"}))).toBe(false);
        // partial matches
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "tofuflower"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flowertofu"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "aaatofubbb"}))).toBe(true);

        // Another filter
        viewFilterService.filterName("flower");
        // exact match
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flower"}))).toBe(true);
        // no match
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "tofu"}))).toBe(false);
        // partial matches
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flowertofu"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "tofuflower"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "aaaflowerbbb"}))).toBe(true);
    });

    it("calls reapplyFilters on filterStatus", () => {
        // Enable the status by sending a file with the status
        viewFileService._files.next(Immutable.List([
            new ViewFile({status: ViewFile.Status.QUEUED})
        ]));

        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(0);
        viewFilterService.filterStatus(ViewFile.Status.QUEUED);
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(1);
    });

    it("does not call reapplyFilters on duplicate filterStatus", () => {
        // Enable the status by sending a file with the status
        viewFileService._files.next(Immutable.List([
            new ViewFile({status: ViewFile.Status.QUEUED})
        ]));

        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(0);
        viewFilterService.filterStatus(ViewFile.Status.QUEUED);
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(1);
        viewFilterService.filterStatus(ViewFile.Status.QUEUED);
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(1);
    });

    it("does not call reapplyFilters on non-existing filterStatus", () => {
        // Enable the status by sending a file with the status
        viewFileService._files.next(Immutable.List([
            new ViewFile({status: ViewFile.Status.QUEUED})
        ]));

        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(0);
        viewFilterService.filterStatus(ViewFile.Status.QUEUED);
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(1);
        viewFilterService.filterStatus(ViewFile.Status.EXTRACTING);
        expect(viewFileService.reapplyFilters).toHaveBeenCalledTimes(1);
    });

    it("has status filter disabled by default", fakeAsync(() => {
        // Enable the status by sending a file with the status
        viewFileService._files.next(Immutable.List([
            new ViewFile({status: ViewFile.Status.DEFAULT}),
            new ViewFile({status: ViewFile.Status.QUEUED}),
            new ViewFile({status: ViewFile.Status.DOWNLOADING}),
            new ViewFile({status: ViewFile.Status.DOWNLOADED}),
            new ViewFile({status: ViewFile.Status.STOPPED}),
            new ViewFile({status: ViewFile.Status.DELETED}),
            new ViewFile({status: ViewFile.Status.EXTRACTING}),
            new ViewFile({status: ViewFile.Status.EXTRACTED})
        ]));

        let count = 0;
        let filter: ViewFileFilter = null;
        viewFilterService.filter.subscribe({
            next: _filter => {
                filter = _filter;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);
        expect(filter.allFilterSelected).toBe(true);
        expect(filter.defaultFilterSelected).toBe(false);
        expect(filter.queuedFilterSelected).toBe(false);
        expect(filter.downloadingFilterSelected).toBe(false);
        expect(filter.downloadedFilterSelected).toBe(false);
        expect(filter.stoppedFilterSelected).toBe(false);
        expect(filter.extractingFilterSelected).toBe(false);
        expect(filter.extractedFilterSelected).toBe(false);
    }));

    it("updates selected filter on filterStatus", fakeAsync(() => {
        // Enable the status by sending a file with the status
        viewFileService._files.next(Immutable.List([
            new ViewFile({status: ViewFile.Status.DEFAULT}),
            new ViewFile({status: ViewFile.Status.QUEUED}),
            new ViewFile({status: ViewFile.Status.DOWNLOADING}),
            new ViewFile({status: ViewFile.Status.DOWNLOADED}),
            new ViewFile({status: ViewFile.Status.STOPPED}),
            new ViewFile({status: ViewFile.Status.DELETED}),
            new ViewFile({status: ViewFile.Status.EXTRACTING}),
            new ViewFile({status: ViewFile.Status.EXTRACTED})
        ]));

        let count = 0;
        let filter: ViewFileFilter = null;
        viewFilterService.filter.subscribe({
            next: _filter => {
                filter = _filter;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);

        viewFilterService.filterStatus(ViewFile.Status.DEFAULT);
        tick();
        expect(count).toBe(2);
        expect(filter.allFilterSelected).toBe(false);
        expect(filter.defaultFilterSelected).toBe(true);
        expect(filter.queuedFilterSelected).toBe(false);
        expect(filter.downloadingFilterSelected).toBe(false);
        expect(filter.downloadedFilterSelected).toBe(false);
        expect(filter.stoppedFilterSelected).toBe(false);
        expect(filter.extractingFilterSelected).toBe(false);
        expect(filter.extractedFilterSelected).toBe(false);

        viewFilterService.filterStatus(ViewFile.Status.EXTRACTING);
        tick();
        expect(count).toBe(3);
        expect(filter.allFilterSelected).toBe(false);
        expect(filter.defaultFilterSelected).toBe(false);
        expect(filter.queuedFilterSelected).toBe(false);
        expect(filter.downloadingFilterSelected).toBe(false);
        expect(filter.downloadedFilterSelected).toBe(false);
        expect(filter.stoppedFilterSelected).toBe(false);
        expect(filter.extractingFilterSelected).toBe(true);
        expect(filter.extractedFilterSelected).toBe(false);

        // Disabled filter
        viewFilterService.filterStatus(null);
        tick();
        expect(count).toBe(4);
        expect(filter.allFilterSelected).toBe(true);
        expect(filter.defaultFilterSelected).toBe(false);
        expect(filter.queuedFilterSelected).toBe(false);
        expect(filter.downloadingFilterSelected).toBe(false);
        expect(filter.downloadedFilterSelected).toBe(false);
        expect(filter.stoppedFilterSelected).toBe(false);
        expect(filter.extractedFilterSelected).toBe(false);
        expect(filter.extractedFilterSelected).toBe(false);
    }));

    it("updates enabled filters on view model updates", fakeAsync(() => {
        // Enable the status by sending a file with the status
        viewFileService._files.next(Immutable.List([
            new ViewFile({status: ViewFile.Status.DEFAULT}),
            new ViewFile({status: ViewFile.Status.QUEUED}),
            new ViewFile({status: ViewFile.Status.DOWNLOADING}),
            new ViewFile({status: ViewFile.Status.DOWNLOADED}),
            new ViewFile({status: ViewFile.Status.STOPPED}),
            new ViewFile({status: ViewFile.Status.DELETED}),
            new ViewFile({status: ViewFile.Status.EXTRACTING}),
            new ViewFile({status: ViewFile.Status.EXTRACTED})
        ]));

        let count = 0;
        let filter: ViewFileFilter = null;
        viewFilterService.filter.subscribe({
            next: _filter => {
                filter = _filter;
                count++;
            }
        });
        tick();
        expect(count).toBe(1);
        expect(filter.defaultFilterEnabled).toBe(true);
        expect(filter.queuedFilterEnabled).toBe(true);
        expect(filter.downloadingFilterEnabled).toBe(true);
        expect(filter.downloadedFilterEnabled).toBe(true);
        expect(filter.stoppedFilterEnabled).toBe(true);
        expect(filter.extractingFilterEnabled).toBe(true);
        expect(filter.extractedFilterEnabled).toBe(true);

        viewFileService._files.next(Immutable.List([
            new ViewFile({status: ViewFile.Status.DEFAULT}),
            new ViewFile({status: ViewFile.Status.DOWNLOADED}),
            new ViewFile({status: ViewFile.Status.EXTRACTED})
        ]));
        tick();
        expect(count).toBe(2);
        expect(filter.defaultFilterEnabled).toBe(true);
        expect(filter.queuedFilterEnabled).toBe(false);
        expect(filter.downloadingFilterEnabled).toBe(false);
        expect(filter.downloadedFilterEnabled).toBe(true);
        expect(filter.stoppedFilterEnabled).toBe(false);
        expect(filter.extractingFilterEnabled).toBe(false);
        expect(filter.extractedFilterEnabled).toBe(true);

        viewFileService._files.next(Immutable.List([]));
        tick();
        expect(count).toBe(3);
        expect(filter.defaultFilterEnabled).toBe(false);
        expect(filter.queuedFilterEnabled).toBe(false);
        expect(filter.downloadingFilterEnabled).toBe(false);
        expect(filter.downloadedFilterEnabled).toBe(false);
        expect(filter.stoppedFilterEnabled).toBe(false);
        expect(filter.extractingFilterEnabled).toBe(false);
        expect(filter.extractedFilterEnabled).toBe(false);
    }));

    it("filters by status correctly", () => {
        // Enable the status by sending a file with the status
        viewFileService._files.next(Immutable.List([
            new ViewFile({status: ViewFile.Status.DEFAULT}),
            new ViewFile({status: ViewFile.Status.QUEUED}),
            new ViewFile({status: ViewFile.Status.DOWNLOADING}),
            new ViewFile({status: ViewFile.Status.DOWNLOADED}),
            new ViewFile({status: ViewFile.Status.STOPPED}),
            new ViewFile({status: ViewFile.Status.DELETED}),
            new ViewFile({status: ViewFile.Status.EXTRACTING}),
            new ViewFile({status: ViewFile.Status.EXTRACTED})
        ]));

        viewFilterService.filterStatus(ViewFile.Status.DEFAULT);
        // exact match
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.DEFAULT}))).toBe(true);
        // no match
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.QUEUED}))).toBe(false);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.DOWNLOADING}))).toBe(false);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.DELETED}))).toBe(false);

        // Another filter
        viewFilterService.filterStatus(ViewFile.Status.EXTRACTING);
        // exact match
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.EXTRACTING}))).toBe(true);
        // no match
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.QUEUED}))).toBe(false);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.DOWNLOADING}))).toBe(false);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.DELETED}))).toBe(false);

        // Disable status filter
        viewFilterService.filterStatus(null);
        // all matches
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.DEFAULT}))).toBe(true);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.QUEUED}))).toBe(true);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.DOWNLOADING}))).toBe(true);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.DOWNLOADED}))).toBe(true);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.STOPPED}))).toBe(true);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.DELETED}))).toBe(true);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.EXTRACTING}))).toBe(true);
        expect(filterCriteria.meetsCriteria(
            new ViewFile({status: ViewFile.Status.EXTRACTED}))).toBe(true);
    });

    it("filters by name AND status correctly", () => {
        // Enable the status by sending a file with the status
        viewFileService._files.next(Immutable.List([
            new ViewFile({status: ViewFile.Status.DEFAULT}),
            new ViewFile({status: ViewFile.Status.QUEUED}),
            new ViewFile({status: ViewFile.Status.DOWNLOADING}),
            new ViewFile({status: ViewFile.Status.DOWNLOADED}),
            new ViewFile({status: ViewFile.Status.STOPPED}),
            new ViewFile({status: ViewFile.Status.DELETED}),
            new ViewFile({status: ViewFile.Status.EXTRACTING}),
            new ViewFile({status: ViewFile.Status.EXTRACTED})
        ]));

        viewFilterService.filterStatus(ViewFile.Status.DEFAULT);
        viewFilterService.filterName("tofu");
        // both match
        expect(filterCriteria.meetsCriteria(new ViewFile({
            name: "tofu",
            status: ViewFile.Status.DEFAULT
        }))).toBe(true);

        // only one matches
        expect(filterCriteria.meetsCriteria(new ViewFile({
            name: "flower",
            status: ViewFile.Status.DEFAULT
        }))).toBe(false);
        expect(filterCriteria.meetsCriteria(new ViewFile({
            name: "tofu",
            status: ViewFile.Status.QUEUED
        }))).toBe(false);

        // neither matches
        expect(filterCriteria.meetsCriteria(new ViewFile({
            name: "flower",
            status: ViewFile.Status.QUEUED
        }))).toBe(false);
    });
});
