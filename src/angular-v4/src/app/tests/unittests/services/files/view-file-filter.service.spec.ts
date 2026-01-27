import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import {ViewFileFilterService} from "../../../../services/files/view-file-filter.service";
import {LoggerService} from "../../../../services/utils/logger.service";
import {ViewFileFilterCriteria, ViewFileService} from "../../../../services/files/view-file.service";
import {MockViewFileService} from "../../../mocks/mock-view-file.service";
import {ViewFile} from "../../../../services/files/view-file";
import {ViewFileOptionsService} from "../../../../services/files/view-file-options.service";
import {MockViewFileOptionsService} from "../../../mocks/mock-view-file-options.service";
import {ViewFileOptions} from "../../../../services/files/view-file-options";


describe("Testing view file filter service", () => {
    let viewFilterService: ViewFileFilterService;

    let viewFileService: MockViewFileService;
    let viewFileOptionsService: MockViewFileOptionsService;
    let filterCriteria: ViewFileFilterCriteria;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                ViewFileFilterService,
                LoggerService,
                {provide: ViewFileService, useClass: MockViewFileService},
                {provide: ViewFileOptionsService, useClass: MockViewFileOptionsService}
            ]
        });
        viewFileService = TestBed.get(ViewFileService);
        spyOn(viewFileService, "setFilterCriteria").and.callFake(
            value => filterCriteria = value
        );

        viewFileOptionsService = TestBed.get(ViewFileOptionsService);

        viewFilterService = TestBed.get(ViewFileFilterService);
    });

    it("should create an instance", () => {
        expect(viewFilterService).toBeDefined();
    });

    it("does not set a filter criteria by default", () => {
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(0);
        expect(filterCriteria).toBeUndefined();
    });

    it("calls setFilterCriteria on filter name set", fakeAsync(() => {
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "something",
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
    }));

    it("does not call setFilterCriteria on duplicate filter names", fakeAsync(() => {
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "something",
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "something",
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
    }));

    it("does not call setFilterCriteria for filter name " +
            "when a different option is changed", fakeAsync(() => {
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "something",
            showDetails: true,
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "something",
            showDetails: false,
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
    }));

    it("correctly filters by name", fakeAsync(() => {
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "tofu",
        }));
        tick();

        // exact match
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "tofu"}))).toBe(true);
        // no match
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flower"}))).toBe(false);
        // partial matches
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "tofuflower"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flowertofu"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "aaatofubbb"}))).toBe(true);

        // Another filter
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "flower",
        }));
        tick();
        // exact match
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flower"}))).toBe(true);
        // no match
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "tofu"}))).toBe(false);
        // partial matches
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flowertofu"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "tofuflower"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "aaaflowerbbb"}))).toBe(true);
    }));

    it("ignores cases when filtering by name", fakeAsync(() => {
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "tofu",
        }));
        tick();
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "TOFU"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "TofU"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "aaaToFubbb"}))).toBe(true);

        // Another filter
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "flOweR",
        }));
        tick();
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "FLowEr"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "tofuflowertofu"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "floWer"}))).toBe(true);
    }));

    it("treats dots as spaces when filtering by name", fakeAsync(() => {
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "to.fu",
        }));
        tick();
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "to.fu"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "to fu"}))).toBe(true);

        // Another filter
        viewFileOptionsService._options.next(new ViewFileOptions({
            nameFilter: "flo wer",
        }));
        tick();
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flo wer"}))).toBe(true);
        expect(filterCriteria.meetsCriteria(new ViewFile({name: "flo.wer"}))).toBe(true);
    }));

    it("calls setFilterCriteria on filter status set", fakeAsync(() => {
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            selectedStatusFilter: ViewFile.Status.QUEUED
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
    }));

    it("does not call setFilterCriteria on duplicate filter status", fakeAsync(() => {
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            selectedStatusFilter: ViewFile.Status.QUEUED
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
        viewFileOptionsService._options.next(new ViewFileOptions({
            selectedStatusFilter: ViewFile.Status.QUEUED
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
    }));

    it("does not call setFilterCriteria for filter status " +
            "when a different option is changed", fakeAsync(() => {
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(0);
        viewFileOptionsService._options.next(new ViewFileOptions({
            selectedStatusFilter: ViewFile.Status.QUEUED,
            showDetails: true,
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
        viewFileOptionsService._options.next(new ViewFileOptions({
            selectedStatusFilter: ViewFile.Status.QUEUED,
            showDetails: false,
        }));
        tick();
        expect(viewFileService.setFilterCriteria).toHaveBeenCalledTimes(1);
    }));

    it("correctly filters by status", fakeAsync(() => {
        viewFileOptionsService._options.next(new ViewFileOptions({
            selectedStatusFilter: ViewFile.Status.DEFAULT,
        }));
        tick();

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
        viewFileOptionsService._options.next(new ViewFileOptions({
            selectedStatusFilter: ViewFile.Status.EXTRACTING,
        }));
        tick();
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
        viewFileOptionsService._options.next(new ViewFileOptions({
            selectedStatusFilter: null,
        }));
        tick();
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
    }));

    it("correctly filters by name AND status", fakeAsync(() => {
        viewFileOptionsService._options.next(new ViewFileOptions({
            selectedStatusFilter: ViewFile.Status.DEFAULT,
            nameFilter: "tofu",
        }));
        tick();

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
    }));
});
