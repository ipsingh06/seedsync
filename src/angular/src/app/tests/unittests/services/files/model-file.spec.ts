import * as Immutable from "immutable";

import {ModelFile} from "../../../../services/files/model-file";

describe("Testing config record initialization", () => {
    let baseJson;
    let baseModelFile;

    beforeEach(() => {
        baseJson = {
            name: "File.One",
            is_dir: false,
            local_size: 1234,
            remote_size: 4567,
            state: "default",
            downloading_speed: 99,
            eta: 54,
            full_path: "/full/path/to/file.one",
            children: []
        };
        baseModelFile = new ModelFile(baseJson);
    });

    it("should be immutable", () => {
        expect(baseModelFile instanceof Immutable.Record).toBe(true);
    });

    it("should have an immutable container of children", () => {
        expect(baseModelFile.children instanceof Immutable.Set).toBe(true);
    });

    it("should correctly initialize all states", () => {
        baseJson.state = "default";
        baseModelFile = new ModelFile(baseJson);
        expect(baseModelFile.state).toBe(ModelFile.State.DEFAULT);
        baseJson.state = "queued";
        baseModelFile = new ModelFile(baseJson);
        expect(baseModelFile.state).toBe(ModelFile.State.QUEUED);
        baseJson.state = "downloading";
        baseModelFile = new ModelFile(baseJson);
        expect(baseModelFile.state).toBe(ModelFile.State.DOWNLOADING);
        baseJson.state = "downloaded";
        baseModelFile = new ModelFile(baseJson);
        expect(baseModelFile.state).toBe(ModelFile.State.DOWNLOADED);
        baseJson.state = "deleted";
        baseModelFile = new ModelFile(baseJson);
        expect(baseModelFile.state).toBe(ModelFile.State.DELETED);
    });

    it("should initialize with correct values", () => {
        expect(baseModelFile.name).toBe("File.One");
        expect(baseModelFile.is_dir).toBe(false);
        expect(baseModelFile.local_size).toBe(1234);
        expect(baseModelFile.remote_size).toBe(4567);
        expect(baseModelFile.state).toBe(ModelFile.State.DEFAULT);
        expect(baseModelFile.downloading_speed).toBe(99);
        expect(baseModelFile.eta).toBe(54);
        expect(baseModelFile.full_path).toBe("/full/path/to/file.one");
        expect(baseModelFile.children.size).toBe(0);
    });

    it("should correctly initialize children", () => {
        baseJson.children = [
            {
                name: "a",
                is_dir: true,
                local_size: 1,
                remote_size: 11,
                state: "default",
                downloading_speed: 111,
                eta: 1111,
                full_path: "root/a",
                children: [
                    {
                        name: "aa",
                        is_dir: false,
                        local_size: 1,
                        remote_size: 11,
                        state: "default",
                        downloading_speed: 111,
                        eta: 1111,
                        full_path: "root/a/aa",
                        children: []
                    },
                ]
            },
            {
                name: "b",
                is_dir: false,
                local_size: 2,
                remote_size: 22,
                state: "default",
                downloading_speed: 222,
                eta: 2222,
                full_path: "root/b",
                children: []
            }
        ];
        baseModelFile = new ModelFile(baseJson);
        expect(baseModelFile.children.size).toBe(2);

        let a = baseModelFile.children.find(value => {return value.name === "a"});
        expect(a.name).toBe("a");
        expect(a.is_dir).toBe(true);
        expect(a.local_size).toBe(1);
        expect(a.remote_size).toBe(11);
        expect(a.state).toBe(ModelFile.State.DEFAULT);
        expect(a.downloading_speed).toBe(111);
        expect(a.eta).toBe(1111);
        expect(a.full_path).toBe("root/a");
        expect(a.children.size).toBe(1);

        let aa = a.children.find(value => {return value.name === "aa"});
        expect(aa.name).toBe("aa");
        expect(aa.is_dir).toBe(false);
        expect(aa.local_size).toBe(1);
        expect(aa.remote_size).toBe(11);
        expect(aa.state).toBe(ModelFile.State.DEFAULT);
        expect(aa.downloading_speed).toBe(111);
        expect(aa.eta).toBe(1111);
        expect(aa.full_path).toBe("root/a/aa");
        expect(aa.children.size).toBe(0);

        let b = baseModelFile.children.find(value => {return value.name === "b"});
        expect(b.name).toBe("b");
        expect(b.is_dir).toBe(false);
        expect(b.local_size).toBe(2);
        expect(b.remote_size).toBe(22);
        expect(b.state).toBe(ModelFile.State.DEFAULT);
        expect(b.downloading_speed).toBe(222);
        expect(b.eta).toBe(2222);
        expect(b.full_path).toBe("root/b");
        expect(b.children.size).toBe(0);
    });
});
