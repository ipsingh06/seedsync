import * as Immutable from "immutable";

import {ModelFile} from "./model-file";

export const SCREENSHOT_MODEL_FILES: Immutable.Map<string, ModelFile> = Immutable.Map({
    "A Really Cool Video About Cats.mkv": new ModelFile({
        name: "A Really Cool Video About Cats.mkv",
        is_dir: false,
        local_size: 123644865,
        remote_size: 243644865,
        state: ModelFile.State.DOWNLOADING,
        downloading_speed: 512000,
        eta: 3612,
        full_path: null,
        is_extractable: false,
        children: Immutable.Set<ModelFile>()
    }),

    "My Important Files": new ModelFile({
        name: "My Important Files",
        is_dir: true,
        local_size: 123456,
        remote_size: 487241252,
        state: ModelFile.State.DOWNLOADING,
        downloading_speed: 1212000,
        eta: 1514,
        full_path: null,
        is_extractable: false,
        children: Immutable.Set<ModelFile>()
    }),

    "That.Show.About.Dragons.8x03.1080p": new ModelFile({
        name: "That.Show.About.Dragons.8x03.1080p",
        is_dir: true,
        local_size: 970712825,
        remote_size: 970712825,
        state: ModelFile.State.DOWNLOADED,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: true,
        children: Immutable.Set<ModelFile>()
    }),

    "ubuntu-17.10-desktop-amd64.iso": new ModelFile({
        name: "ubuntu-17.10-desktop-amd64.iso",
        is_dir: false,
        local_size: null,
        remote_size: 882722050,
        state: ModelFile.State.QUEUED,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: false,
        children: Immutable.Set<ModelFile>()
    }),

    "My Local Folder": new ModelFile({
        name: "My Local Folder",
        is_dir: true,
        local_size: 86311523,
        remote_size: null,
        state: ModelFile.State.DEFAULT,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: false,
        children: Immutable.Set<ModelFile>()
    }),

    "My Remote Folder": new ModelFile({
        name: "My Remote Folder",
        is_dir: true,
        local_size: null,
        remote_size: 7086311523,
        state: ModelFile.State.DEFAULT,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: false,
        children: Immutable.Set<ModelFile>()
    }),

    "Dont.Download.This.Song.mp3": new ModelFile({
        name: "Dont.Download.This.Song.mp3",
        is_dir: false,
        local_size: 11111111,
        remote_size: 44444444,
        state: ModelFile.State.DEFAULT,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: false,
        children: Immutable.Set<ModelFile>()
    }),

    "Folder Deleted Locally": new ModelFile({
        name: "Folder Deleted Locally",
        is_dir: true,
        local_size: null,
        remote_size: 1024,
        state: ModelFile.State.DELETED,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: false,
        children: Immutable.Set<ModelFile>()
    }),

    "Folder Containing Archives": new ModelFile({
        name: "Folder Containing Archives",
        is_dir: true,
        local_size: 1500000000,
        remote_size: 1000000000,
        state: ModelFile.State.EXTRACTING,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: true,
        children: Immutable.Set<ModelFile>()
    }),

    "archive.rar": new ModelFile({
        name: "archive.rar",
        is_dir: false,
        local_size: 1000000000,
        remote_size: 1000000000,
        state: ModelFile.State.EXTRACTED,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: true,
        children: Immutable.Set<ModelFile>()
    }),
});
