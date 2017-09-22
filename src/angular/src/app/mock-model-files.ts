import * as Immutable from 'immutable';

import {ModelFile} from "./model-file"

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
        children: []
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
        children: []
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
        children: []
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
        children: []
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
        children: []
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
        children: []
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
        children: []
    }),
});
