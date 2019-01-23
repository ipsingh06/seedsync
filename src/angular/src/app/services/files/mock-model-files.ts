import * as Immutable from "immutable";

import {ModelFile} from "./model-file";

export const MOCK_MODEL_FILES: Immutable.Map<string, ModelFile> = Immutable.Map({
    "[AUTHOR] A Really Cool Video About Cats.mkv": new ModelFile({
        name: "[AUTHOR] A Really Cool Video About Cats.mkv",
        is_dir: false,
        local_size: 123644865,
        remote_size: 243644865,
        state: ModelFile.State.DOWNLOADING,
        downloading_speed: 512000,
        eta: 3612,
        full_path: null,
        is_extractable: false,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "Super.Secret.Folder.With.A.Long.Name.Separated.By.Dots": new ModelFile({
        name: "Super.Secret.Folder.With.A.Long.Name.Separated.By.Dots",
        is_dir: true,
        local_size: 123456,
        remote_size: 487241252,
        state: ModelFile.State.DOWNLOADING,
        downloading_speed: 1212000,
        eta: 1514,
        full_path: null,
        is_extractable: false,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "Game.Of.Big.Bang.Last.Week.Breaking.Valley.Episode.8.03": new ModelFile({
        name: "Game.Of.Big.Bang.Last.Week.Breaking.Valley.Episode.8.03",
        is_dir: true,
        local_size: 970712825,
        remote_size: 970712825,
        state: ModelFile.State.DOWNLOADED,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: true,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "Green.Archer.Dude.And.Fast.Red.Streaky.Guy.Show": new ModelFile({
        name: "Green.Archer.Dude.And.Fast.Red.Streaky.Guy.Show",
        is_dir: true,
        local_size: null,
        remote_size: 882722050,
        state: ModelFile.State.QUEUED,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: true,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "OneLongFileWithNoSpacesNoDotsNoHypensJustLotsAndLotsOfTextOhGodWhoNamedThisFileDamnIt": new ModelFile({
        name: "OneLongFileWithNoSpacesNoDotsNoHypensJustLotsAndLotsOfTextOhGodWhoNamedThisFileDamnIt",
        is_dir: true,
        local_size: null,
        remote_size: 7086311523,
        state: ModelFile.State.DEFAULT,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: false,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "My Local File": new ModelFile({
        name: "My Local File",
        is_dir: true,
        local_size: 86311523,
        remote_size: null,
        state: ModelFile.State.DEFAULT,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: false,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "This_File_Needs_To_Be_Resumed.exe": new ModelFile({
        name: "This_File_Needs_To_Be_Resumed.exe",
        is_dir: false,
        local_size: 11111111,
        remote_size: 44444444,
        state: ModelFile.State.DEFAULT,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: false,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "Deleted Folder": new ModelFile({
        name: "Deleted Folder",
        is_dir: true,
        local_size: null,
        remote_size: 1024,
        state: ModelFile.State.DELETED,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: false,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "my.local.archive.rar": new ModelFile({
        name: "my.local.archive.rar",
        is_dir: false,
        local_size: 28000,
        remote_size: null,
        state: ModelFile.State.EXTRACTED,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: true,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "NextEpisode": new ModelFile({
        name: "NextEpisode",
        is_dir: true,
        local_size: 1500000000,
        remote_size: 1000000000,
        state: ModelFile.State.EXTRACTING,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: true,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),

    "PreviousEpisode": new ModelFile({
        name: "PreviousEpisode",
        is_dir: true,
        local_size: 2000000000,
        remote_size: 1000000000,
        state: ModelFile.State.EXTRACTED,
        downloading_speed: null,
        eta: null,
        full_path: null,
        is_extractable: true,
        local_created_timestamp: "1541717418.0",
        local_modified_timestamp: "1541828418.9439101",
        remote_created_timestamp: "1541515418.0",
        remote_modified_timestamp: "1541616418.9439101",
        children: Immutable.Set<ModelFile>()
    }),
});
