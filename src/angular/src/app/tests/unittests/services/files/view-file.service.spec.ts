import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import * as Immutable from "immutable";

import {ViewFileService} from "../../../../services/files/view-file.service";
import {LoggerService} from "../../../../services/utils/logger.service";
import {StreamServiceRegistry} from "../../../../services/base/stream-service.registry";
import {MockStreamServiceRegistry} from "../../../mocks/mock-stream-service.registry";
import {ConnectedService} from "../../../../services/utils/connected.service";
import {MockModelFileService} from "../../../mocks/mock-model-file.service";
import {ModelFile} from "../../../../services/files/model-file";
import {ModelFileService} from "../../../../services/files/model-file.service";
import {ViewFile} from "../../../../services/files/view-file";


describe("Testing view file service", () => {
    let viewService: ViewFileService;
    let mockModelService: MockModelFileService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                ViewFileService,
                LoggerService,
                ConnectedService,
                {provide: StreamServiceRegistry, useClass: MockStreamServiceRegistry}
            ]
        });

        viewService = TestBed.get(ViewFileService);
        let mockRegistry: MockStreamServiceRegistry = TestBed.get(StreamServiceRegistry);
        mockModelService = mockRegistry.modelFileService;
    });

    it("should create an instance", () => {
        expect(viewService).toBeDefined();
    });

    it("should forward an empty model by default", fakeAsync(() => {
        let count = 0;

        viewService.files.subscribe({
            next: list => {
                expect(list.size).toBe(0);
                count++;
            }
        });

        tick();
        expect(count).toBe(1);
    }));

    it("should forward an empty model", fakeAsync(() => {
        let model = Immutable.Map<string, ModelFile>();
        mockModelService._files.next(model);
        tick();

        let count = 0;
        viewService.files.subscribe({
            next: list => {
                expect(list.size).toBe(0);
                count++;
            }
        });
        tick();
        expect(count).toBe(1);
    }));

    it("should correctly populate ViewFile props from a ModelFile", fakeAsync(() => {
        let model = Immutable.Map<string, ModelFile>();
        model = model.set("a", new ModelFile({
            name: "a",
            is_dir: true,
            local_size: 0,
            remote_size: 11,
            state: ModelFile.State.DEFAULT,
            downloading_speed: 111,
            eta: 1111,
            full_path: "root/a",
            is_extractable: true
        }));
        mockModelService._files.next(model);
        tick();

        let count = 0;
        viewService.files.subscribe({
            next: list => {
                expect(list.size).toBe(1);
                let file = list.get(0);
                expect(file.name).toBe("a");
                expect(file.isDir).toBe(true);
                expect(file.localSize).toBe(0);
                expect(file.remoteSize).toBe(11);
                expect(file.status).toBe(ViewFile.Status.DEFAULT);
                expect(file.downloadingSpeed).toBe(111);
                expect(file.eta).toBe(1111);
                expect(file.fullPath).toBe("root/a");
                expect(file.isExtractable).toBe(true);
                count++;
            }
        });
        tick();
        expect(count).toBe(1);
    }));

    it("should correctly set the ViewFile status", fakeAsync(() => {
        let modelFile = new ModelFile({
            name: "a",
            state: ModelFile.State.DEFAULT,
        });
        let model = Immutable.Map<string, ModelFile>();
        model = model.set(modelFile.name, modelFile);

        let expectedStates = [
            ViewFile.Status.DEFAULT,
            ViewFile.Status.QUEUED,
            ViewFile.Status.DOWNLOADING,
            ViewFile.Status.DOWNLOADED,
            ViewFile.Status.STOPPED,
            ViewFile.Status.DELETED,
            ViewFile.Status.EXTRACTING,
            ViewFile.Status.EXTRACTED
        ];

        // First state - DEFAULT
        mockModelService._files.next(model);
        tick();

        let count = 0;
        viewService.files.subscribe({
            next: list => {
                expect(list.size).toBe(1);
                let file = list.get(0);
                expect(file.status).toBe(expectedStates[count++]);
            }
        });
        tick();
        expect(count).toBe(1);

        // Next state - QUEUED
        modelFile = new ModelFile(modelFile.set("state", ModelFile.State.QUEUED));
        model = model.set(modelFile.name, modelFile);
        mockModelService._files.next(model);
        tick();
        expect(count).toBe(2);

        // Next state - DOWNLOADING
        modelFile = new ModelFile(modelFile.set("state", ModelFile.State.DOWNLOADING));
        model = model.set(modelFile.name, modelFile);
        mockModelService._files.next(model);
        tick();
        expect(count).toBe(3);

        // Next state - DOWNLOADED
        modelFile = new ModelFile(modelFile.set("state", ModelFile.State.DOWNLOADED));
        model = model.set(modelFile.name, modelFile);
        mockModelService._files.next(model);
        tick();
        expect(count).toBe(4);

        // Next state - STOPPED
        // local size and remote size > 0
        modelFile = new ModelFile(modelFile.set("state", ModelFile.State.DEFAULT));
        modelFile = new ModelFile(modelFile.set("local_size", 50));
        modelFile = new ModelFile(modelFile.set("remote_size", 50));
        model = model.set(modelFile.name, modelFile);
        mockModelService._files.next(model);
        tick();
        expect(count).toBe(5);

        // Next state - DELETED
        modelFile = new ModelFile(modelFile.set("state", ModelFile.State.DELETED));
        model = model.set(modelFile.name, modelFile);
        mockModelService._files.next(model);
        tick();
        expect(count).toBe(6);

        // Next state - DELETED
        modelFile = new ModelFile(modelFile.set("state", ModelFile.State.EXTRACTING));
        model = model.set(modelFile.name, modelFile);
        mockModelService._files.next(model);
        tick();
        expect(count).toBe(7);

        // Next state - DELETED
        modelFile = new ModelFile(modelFile.set("state", ModelFile.State.EXTRACTED));
        model = model.set(modelFile.name, modelFile);
        mockModelService._files.next(model);
        tick();
        expect(count).toBe(8);
    }));
});
