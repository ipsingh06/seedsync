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
                expect(file.isArchive).toBe(true);
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

    it("should always set a non-null file sizes in ViewFile", fakeAsync(() => {
        let model = Immutable.Map<string, ModelFile>();
        model = model.set("a", new ModelFile({
            name: "a",
            local_size: null,
            remote_size: null,
        }));
        mockModelService._files.next(model);
        tick();

        let count = 0;
        viewService.files.subscribe({
            next: list => {
                expect(list.size).toBe(1);
                let file = list.get(0);
                expect(file.localSize).toBe(0);
                expect(file.remoteSize).toBe(0);
                count++;
            }
        });
        tick();
        expect(count).toBe(1);
    }));

    it("should correctly set ViewFile percent downloaded", fakeAsync(() => {
        // Test vectors of local size, remote size, percentage
        let testVectors = [
            [0, 10, 0],
            [5, 10, 50],
            [10, 10, 100],
            [null, 10, 0],
            [10, null, 100]
        ];

        let count = -1;
        viewService.files.subscribe({
            next: list => {
                // Ignore first
                if(count >= 0) {
                    expect(list.size).toBe(1);
                    let file = list.get(0);
                    expect(file.percentDownloaded).toBe(testVectors[count][2]);
                }
                count++;
            }
        });
        tick();
        expect(count).toBe(0);

        // Send over the test vectors
        for(let vector of testVectors) {
            let model = Immutable.Map<string, ModelFile>();
            model = model.set("a", new ModelFile({
                name: "a",
                local_size: vector[0],
                remote_size: vector[1],
            }));
            mockModelService._files.next(model);
            tick();
        }
        expect(count).toBe(testVectors.length);
    }));

    it("should should correctly set ViewFile isQueueable", fakeAsync(() => {
        // Test and expected result vectors
        // test - [ModelFile.State, local size, remote size]
        // result - [isQueueable, ViewFile.Status]
        let testVectors: any[][][] = [
            // Default remote file is queueable
            [[ModelFile.State.DEFAULT, null, 100], [true, ViewFile.Status.DEFAULT]],
            // Default local file is NOT queueable
            [[ModelFile.State.DEFAULT, 100, null], [false, ViewFile.Status.DEFAULT]],
            // Stopped file is queueable
            [[ModelFile.State.DEFAULT, 50, 100], [true, ViewFile.Status.STOPPED]],
            // Deleted file is queueable
            [[ModelFile.State.DELETED, null, 100], [true, ViewFile.Status.DELETED]],
            // Queued file is NOT queueable
            [[ModelFile.State.QUEUED, null, 100], [false, ViewFile.Status.QUEUED]],
            // Downloading file is NOT queueable
            [[ModelFile.State.DOWNLOADING, 10, 100], [false, ViewFile.Status.DOWNLOADING]],
            // Downloaded file is NOT queueable
            [[ModelFile.State.DOWNLOADED, 100, 100], [false, ViewFile.Status.DOWNLOADED]],
            // Extracting file is NOT queueable
            [[ModelFile.State.EXTRACTING, 100, 100], [false, ViewFile.Status.EXTRACTING]],
            // Extracting local-only file is NOT queueable
            [[ModelFile.State.EXTRACTING, 100, null], [false, ViewFile.Status.EXTRACTING]],
            // Extracted file is NOT queueable
            [[ModelFile.State.EXTRACTED, 100, 100], [false, ViewFile.Status.EXTRACTED]],
        ];

        let count = -1;
        viewService.files.subscribe({
            next: list => {
                // Ignore first
                if(count >= 0) {
                    expect(list.size).toBe(1);
                    let file = list.get(0);
                    let resultVector = testVectors[count][1];
                    expect(file.isQueueable).toBe(resultVector[0]);
                    expect(file.status).toBe(resultVector[1]);
                }
                count++;
            }
        });
        tick();
        expect(count).toBe(0);

        // Send over the test vectors
        for(let vector of testVectors) {
            let testVector = vector[0];
            let model = Immutable.Map<string, ModelFile>();
            model = model.set("a", new ModelFile({
                name: "a",
                state: testVector[0],
                local_size: testVector[1],
                remote_size: testVector[2],
            }));
            mockModelService._files.next(model);
            tick();
        }
        expect(count).toBe(testVectors.length);
    }));

    it("should should correctly set ViewFile isStoppable", fakeAsync(() => {
        // Test and expected result vectors
        // test - [ModelFile.State, local size, remote size]
        // result - [isStoppable, ViewFile.Status]
        let testVectors: any[][][] = [
            // Default remote file is NOT stoppable
            [[ModelFile.State.DEFAULT, null, 100], [false, ViewFile.Status.DEFAULT]],
            // Default local file is NOT stoppable
            [[ModelFile.State.DEFAULT, 100, null], [false, ViewFile.Status.DEFAULT]],
            // Stopped file is NOT stoppable
            [[ModelFile.State.DEFAULT, 50, 100], [false, ViewFile.Status.STOPPED]],
            // Deleted file is NOT stoppable
            [[ModelFile.State.DELETED, null, 100], [false, ViewFile.Status.DELETED]],
            // Queued file is stoppable
            [[ModelFile.State.QUEUED, null, 100], [true, ViewFile.Status.QUEUED]],
            // Downloading file is stoppable
            [[ModelFile.State.DOWNLOADING, 10, 100], [true, ViewFile.Status.DOWNLOADING]],
            // Downloaded file is NOT stoppable
            [[ModelFile.State.DOWNLOADED, 100, 100], [false, ViewFile.Status.DOWNLOADED]],
            // Extracting file is NOT stoppable
            [[ModelFile.State.EXTRACTING, 100, 100], [false, ViewFile.Status.EXTRACTING]],
            // Extracted file is NOT stoppable
            [[ModelFile.State.EXTRACTED, 100, 100], [false, ViewFile.Status.EXTRACTED]],
        ];

        let count = -1;
        viewService.files.subscribe({
            next: list => {
                // Ignore first
                if(count >= 0) {
                    expect(list.size).toBe(1);
                    let file = list.get(0);
                    let resultVector = testVectors[count][1];
                    expect(file.isStoppable).toBe(resultVector[0]);
                    expect(file.status).toBe(resultVector[1]);
                }
                count++;
            }
        });
        tick();
        expect(count).toBe(0);

        // Send over the test vectors
        for(let vector of testVectors) {
            let testVector = vector[0];
            let model = Immutable.Map<string, ModelFile>();
            model = model.set("a", new ModelFile({
                name: "a",
                state: testVector[0],
                local_size: testVector[1],
                remote_size: testVector[2],
            }));
            mockModelService._files.next(model);
            tick();
        }
        expect(count).toBe(testVectors.length);
    }));

    it("should should correctly set ViewFile isExtractable", fakeAsync(() => {
        // Test and expected result vectors
        // test - [ModelFile.State, local size, remote size]
        // result - [isExtractable, ViewFile.Status]
        let testVectors: any[][][] = [
            // Default remote file is NOT extractable
            [[ModelFile.State.DEFAULT, null, 100], [false, ViewFile.Status.DEFAULT]],
            // Default local file is extractable
            [[ModelFile.State.DEFAULT, 100, null], [true, ViewFile.Status.DEFAULT]],
            // Stopped file is extractable
            [[ModelFile.State.DEFAULT, 50, 100], [true, ViewFile.Status.STOPPED]],
            // Deleted file is NOT extractable
            [[ModelFile.State.DELETED, null, 100], [false, ViewFile.Status.DELETED]],
            // Queued file is NOT extractable
            [[ModelFile.State.QUEUED, null, 100], [false, ViewFile.Status.QUEUED]],
            // Downloading file is NOT extractable
            [[ModelFile.State.DOWNLOADING, 10, 100], [false, ViewFile.Status.DOWNLOADING]],
            // Downloaded file is extractable
            [[ModelFile.State.DOWNLOADED, 100, 100], [true, ViewFile.Status.DOWNLOADED]],
            // Extracting file is NOT extractable
            [[ModelFile.State.EXTRACTING, 100, 100], [false, ViewFile.Status.EXTRACTING]],
            // Extracted file is extractable
            [[ModelFile.State.EXTRACTED, 100, 100], [true, ViewFile.Status.EXTRACTED]],
        ];

        let count = -1;
        viewService.files.subscribe({
            next: list => {
                // Ignore first
                if(count >= 0) {
                    expect(list.size).toBe(1);
                    let file = list.get(0);
                    let resultVector = testVectors[count][1];
                    expect(file.isExtractable).toBe(resultVector[0]);
                    expect(file.status).toBe(resultVector[1]);
                }
                count++;
            }
        });
        tick();
        expect(count).toBe(0);

        // Send over the test vectors
        for(let vector of testVectors) {
            let testVector = vector[0];
            let model = Immutable.Map<string, ModelFile>();
            model = model.set("a", new ModelFile({
                name: "a",
                state: testVector[0],
                local_size: testVector[1],
                remote_size: testVector[2],
            }));
            mockModelService._files.next(model);
            tick();
        }
        expect(count).toBe(testVectors.length);
    }));

    it("should sort view files by status then name", fakeAsync(() => {
        // Test vectors to create model file
        // name, ModelFile.State, local size, remote size
        let testVector: any[][] = [
            ["a", ModelFile.State.DEFAULT, null, 100],
            ["b", ModelFile.State.DEFAULT, 100, null],
            ["c", ModelFile.State.DEFAULT, 50, 100],
            ["d", ModelFile.State.DELETED, null, 100],
            ["e", ModelFile.State.QUEUED, null, 100],
            ["f", ModelFile.State.DOWNLOADING, 50, 100],
            ["g", ModelFile.State.DOWNLOADED, 50, 100],
            ["h", ModelFile.State.EXTRACTING, 50, 100],
            ["i", ModelFile.State.EXTRACTED, 50, 100]
        ];

        // Except result vector in order of view file name and state
        let resultVector: any[][] = [
            ["h", ViewFile.Status.EXTRACTING],
            ["f", ViewFile.Status.DOWNLOADING],
            ["e", ViewFile.Status.QUEUED],
            ["i", ViewFile.Status.EXTRACTED],
            ["g", ViewFile.Status.DOWNLOADED],
            ["c", ViewFile.Status.STOPPED],
            ["a", ViewFile.Status.DEFAULT],
            ["b", ViewFile.Status.DEFAULT],
            ["d", ViewFile.Status.DELETED]
        ];

        let model = Immutable.Map<string, ModelFile>();
        for(let vector of testVector) {
            model = model.set(vector[0], new ModelFile({
                name: vector[0],
                state: vector[1],
                local_size: vector[2],
                remote_size: vector[3],
            }));
        }
        mockModelService._files.next(model);
        tick();

        let count = 0;
        viewService.files.subscribe({
            next: list => {
                expect(list.size).toBe(resultVector.length);
                resultVector.forEach((item, index) => {
                    let file = list.get(index);
                    expect(file.name).toBe(item[0]);
                    expect(file.status).toBe(item[1]);
                });
                count++;
            }
        });
        tick();
        expect(count).toBe(1);
    }));

    it("should correctly set and unset the selected file", fakeAsync(() => {
        let model = Immutable.Map<string, ModelFile>();
        model = model.set("a", new ModelFile({name: "a"}));
        model = model.set("b", new ModelFile({name: "b"}));
        model = model.set("c", new ModelFile({name: "c"}));

        let expectedSelectedFileIndex = -1;

        mockModelService._files.next(model);
        tick();

        let viewFileList;
        let count = 0;
        viewService.files.subscribe({
            next: list => {
                viewFileList = list;
                expect(list.size).toBe(3);
                expect(list.get(0).name).toBe("a");
                expect(list.get(1).name).toBe("b");
                expect(list.get(2).name).toBe("c");
                list.forEach((item, index) => {
                    // Only 1 file is selected at a time
                    if(index == expectedSelectedFileIndex) {
                        expect(item.isSelected).toBe(true);
                    } else {
                        expect(item.isSelected).toBe(false);
                    }
                });
                count++;
            }
        });

        tick();
        expect(count).toBe(1);

        // select "a"
        expectedSelectedFileIndex = 0;
        viewService.setSelected(viewFileList.get(0));
        tick();
        expect(count).toBe(2);

        // unselect "a"
        expectedSelectedFileIndex = -1;
        viewService.unsetSelected();
        tick();
        expect(count).toBe(3);

        // select "b"
        expectedSelectedFileIndex = 1;
        viewService.setSelected(viewFileList.get(1));
        tick();
        expect(count).toBe(4);

        // select "c"
        expectedSelectedFileIndex = 2;
        viewService.setSelected(viewFileList.get(2));
        tick();
        expect(count).toBe(5);

        // select "b" again
        expectedSelectedFileIndex = 1;
        viewService.setSelected(viewFileList.get(1));
        tick();
        expect(count).toBe(6);

        // unselect "b"
        expectedSelectedFileIndex = -1;
        viewService.unsetSelected();
        tick();
        expect(count).toBe(7);
    }));
});
