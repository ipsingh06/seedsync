import {fakeAsync, TestBed, tick} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";

import * as Immutable from "immutable";

import {ModelFileService} from "../../../../services/files/model-file.service";
import {LoggerService} from "../../../../services/utils/logger.service";
import {ModelFile} from "../../../../services/files/model-file";
import {RestService} from "../../../../services/utils/rest.service";


// noinspection JSUnusedLocalSymbols
const DoNothing = {next: reaction => {}};


describe("Testing model file service", () => {
    let modelFileService: ModelFileService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                LoggerService,
                RestService,
                ModelFileService
            ]
        });

        httpMock = TestBed.get(HttpTestingController);

        modelFileService = TestBed.get(ModelFileService);
    });

    it("should create an instance", () => {
        expect(modelFileService).toBeDefined();
    });

    it("should register all events with the event source", () => {
        expect(modelFileService.getEventNames()).toEqual(
            ["model-init", "model-added", "model-updated", "model-removed"]
        );
    });

    it("should send correct model on an init event", fakeAsync(() => {
        let count = 0;
        let latestModel: Immutable.Map<string, ModelFile> = null;
        modelFileService.files.subscribe({
            next: modelFiles => {
                count++;
                latestModel = modelFiles;
            }
        });
        tick();
        expect(count).toBe(1);
        expect(latestModel.size).toBe(0);

        let actualModelFiles = [
            {
                name: "File.One",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: "default",
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.one",
                children: []
            }
        ];
        let expectedModelFiles = [
            new ModelFile({
                name: "File.One",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: ModelFile.State.DEFAULT,
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.one",
                children: Immutable.Set<ModelFile>()
            })
        ];
        modelFileService.notifyEvent("model-init", JSON.stringify(actualModelFiles));
        tick();
        expect(count).toBe(2);
        expect(latestModel.size).toBe(1);
        expect(Immutable.is(latestModel.get("File.One"), expectedModelFiles[0])).toBe(true);
    }));

    it("should send correct model on an added event", fakeAsync(() => {
        let initialModelFiles = [
            {
                name: "File.One",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: "default",
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.one",
                children: []
            }
        ];
        modelFileService.notifyEvent("model-init", JSON.stringify(initialModelFiles));

        let count = 0;
        let latestModel: Immutable.Map<string, ModelFile> = null;
        modelFileService.files.subscribe({
            next: modelFiles => {
                count++;
                latestModel = modelFiles;
            }
        });
        tick();
        expect(count).toBe(1);
        expect(latestModel.size).toBe(1);

        let addedModelFile = {
            new_file: {
                name: "File.Two",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: "default",
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.two",
                children: []
            },
            old_file: {}
        };

        let expectedModelFiles = [
            new ModelFile({
                name: "File.One",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: ModelFile.State.DEFAULT,
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.one",
                children: Immutable.Set<ModelFile>()
            }),
            new ModelFile({
                name: "File.Two",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: ModelFile.State.DEFAULT,
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.two",
                children: Immutable.Set<ModelFile>()
            })
        ];
        modelFileService.notifyEvent("model-added", JSON.stringify(addedModelFile));
        tick();
        expect(count).toBe(2);
        expect(latestModel.size).toBe(2);
        expect(Immutable.is(latestModel.get("File.One"), expectedModelFiles[0])).toBe(true);
        expect(Immutable.is(latestModel.get("File.Two"), expectedModelFiles[1])).toBe(true);
    }));

    it("should send correct model on a removed event", fakeAsync(() => {
        let initialModelFiles = [
            {
                name: "File.One",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: "default",
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.one",
                children: []
            }
        ];
        modelFileService.notifyEvent("model-init", JSON.stringify(initialModelFiles));

        let count = 0;
        let latestModel: Immutable.Map<string, ModelFile> = null;
        modelFileService.files.subscribe({
            next: modelFiles => {
                count++;
                latestModel = modelFiles;
            }
        });
        tick();
        expect(count).toBe(1);
        expect(latestModel.size).toBe(1);

        let removedModelFile = {
            new_file: {},
            old_file: {
                name: "File.One",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: "default",
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.one",
                children: []
            }
        };

        modelFileService.notifyEvent("model-removed", JSON.stringify(removedModelFile));
        tick();
        expect(count).toBe(2);
        expect(latestModel.size).toBe(0);
    }));

    it("should send correct model on an updated event", fakeAsync(() => {
        let initialModelFiles = [
            {
                name: "File.One",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: "default",
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.one",
                children: []
            }
        ];
        modelFileService.notifyEvent("model-init", JSON.stringify(initialModelFiles));

        let count = 0;
        let latestModel: Immutable.Map<string, ModelFile> = null;
        modelFileService.files.subscribe({
            next: modelFiles => {
                count++;
                latestModel = modelFiles;
            }
        });
        tick();
        expect(count).toBe(1);
        expect(latestModel.size).toBe(1);

        let updatedModelFile = {
            new_file: {
                name: "File.One",
                is_dir: false,
                local_size: 4567,
                remote_size: 9012,
                state: "downloading",
                downloading_speed: 55,
                eta: 1,
                full_path: "/new/path/to/file.one",
                children: []
            },
            old_file: {
                name: "File.One",
                is_dir: false,
                local_size: 1234,
                remote_size: 4567,
                state: "default",
                downloading_speed: 99,
                eta: 54,
                full_path: "/full/path/to/file.one",
                children: []
            }
        };

        let expectedModelFiles = [
            new ModelFile({
                name: "File.One",
                is_dir: false,
                local_size: 4567,
                remote_size: 9012,
                state: ModelFile.State.DOWNLOADING,
                downloading_speed: 55,
                eta: 1,
                full_path: "/new/path/to/file.one",
                children: Immutable.Set<ModelFile>()
            })
        ];
        modelFileService.notifyEvent("model-updated", JSON.stringify(updatedModelFile));
        tick();
        expect(count).toBe(2);
        expect(latestModel.size).toBe(1);
        expect(Immutable.is(latestModel.get("File.One"), expectedModelFiles[0])).toBe(true);
    }));

    it("should send empty model on disconnect", fakeAsync(() => {
        let count = 0;
        let latestModel: Immutable.Map<string, ModelFile> = null;
        modelFileService.files.subscribe({
            next: modelFiles => {
                count++;
                latestModel = modelFiles;
            }
        });
        tick();
        expect(count).toBe(1);
        expect(latestModel.size).toBe(0);

        modelFileService.notifyDisconnected();
        tick();
        expect(count).toBe(2);
        expect(latestModel.size).toBe(0);

        tick(4000);
    }));

    it("should send a GET on queue command", fakeAsync(() => {
        // Connect the service
        modelFileService.notifyConnected();

        let modelFile = new ModelFile({
            name: "File.One",
            is_dir: false,
            local_size: 4567,
            remote_size: 9012,
            state: ModelFile.State.DOWNLOADING,
            downloading_speed: 55,
            eta: 1,
            full_path: "/new/path/to/file.one",
            children: Immutable.Set<ModelFile>()
        });

        let count = 0;
        modelFileService.queue(modelFile).subscribe({
            next: reaction => {
                expect(reaction.success).toBe(true);
                count++;
            }
        });
        httpMock.expectOne("/server/command/queue/File.One").flush("done");

        tick();
        expect(count).toBe(1);
        httpMock.verify();
    }));


    it("should send correct GET requests on queue command", fakeAsync(() => {
        // Connect the service
        modelFileService.notifyConnected();

        let modelFile;

        modelFile = new ModelFile({
            name: "test",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.queue(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/queue/test").flush("done");

        modelFile = new ModelFile({
            name: "test space",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.queue(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/queue/test%2520space").flush("done");

        modelFile = new ModelFile({
            name: "test/slash",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.queue(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/queue/test%252Fslash").flush("done");

        modelFile = new ModelFile({
            name: "test\"doublequote",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.queue(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/queue/test%2522doublequote").flush("done");

        modelFile = new ModelFile({
            name: "/test/leadingslash",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.queue(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/queue/%252Ftest%252Fleadingslash").flush("done");
    }));

    it("should send a GET on stop command", fakeAsync(() => {
        // Connect the service
        modelFileService.notifyConnected();

        let modelFile = new ModelFile({
            name: "File.One",
            is_dir: false,
            local_size: 4567,
            remote_size: 9012,
            state: ModelFile.State.DOWNLOADING,
            downloading_speed: 55,
            eta: 1,
            full_path: "/new/path/to/file.one",
            children: Immutable.Set<ModelFile>()
        });

        let count = 0;
        modelFileService.stop(modelFile).subscribe({
            next: reaction => {
                expect(reaction.success).toBe(true);
                count++;
            }
        });
        httpMock.expectOne("/server/command/stop/File.One").flush("done");

        tick();
        expect(count).toBe(1);
        httpMock.verify();
    }));

    it("should send correct GET requests on stop command", fakeAsync(() => {
        // Connect the service
        modelFileService.notifyConnected();

        let modelFile;

        modelFile = new ModelFile({
            name: "test",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.stop(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/stop/test").flush("done");

        modelFile = new ModelFile({
            name: "test space",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.stop(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/stop/test%2520space").flush("done");

        modelFile = new ModelFile({
            name: "test/slash",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.stop(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/stop/test%252Fslash").flush("done");

        modelFile = new ModelFile({
            name: "test\"doublequote",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.stop(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/stop/test%2522doublequote").flush("done");

        modelFile = new ModelFile({
            name: "/test/leadingslash",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.stop(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/stop/%252Ftest%252Fleadingslash").flush("done");
    }));

    it("should send a GET on extract command", fakeAsync(() => {
        // Connect the service
        modelFileService.notifyConnected();

        let modelFile = new ModelFile({
            name: "File.One",
            is_dir: false,
            local_size: 4567,
            remote_size: 9012,
            state: ModelFile.State.DOWNLOADING,
            downloading_speed: 55,
            eta: 1,
            full_path: "/new/path/to/file.one",
            children: Immutable.Set<ModelFile>()
        });

        let count = 0;
        modelFileService.extract(modelFile).subscribe({
            next: reaction => {
                expect(reaction.success).toBe(true);
                count++;
            }
        });
        httpMock.expectOne("/server/command/extract/File.One").flush("done");

        tick();
        expect(count).toBe(1);
        httpMock.verify();
    }));

    it("should send correct GET requests on extract command", fakeAsync(() => {
        // Connect the service
        modelFileService.notifyConnected();

        let modelFile;

        modelFile = new ModelFile({
            name: "test",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.extract(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/extract/test").flush("done");

        modelFile = new ModelFile({
            name: "test space",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.extract(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/extract/test%2520space").flush("done");

        modelFile = new ModelFile({
            name: "test/slash",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.extract(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/extract/test%252Fslash").flush("done");

        modelFile = new ModelFile({
            name: "test\"doublequote",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.extract(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/extract/test%2522doublequote").flush("done");

        modelFile = new ModelFile({
            name: "/test/leadingslash",
            state: ModelFile.State.DEFAULT,
            children: Immutable.Set<ModelFile>()
        });
        modelFileService.extract(modelFile).subscribe(DoNothing);
        httpMock.expectOne("/server/command/extract/%252Ftest%252Fleadingslash").flush("done");
    }));
});
