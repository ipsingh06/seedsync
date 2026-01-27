/**
 * Model file received from the backend
 * Note: Naming convention matches that used in the JSON
 */
export interface ModelFileData {
    readonly name: string;
    readonly is_dir: boolean;
    readonly local_size: number | null;
    readonly remote_size: number | null;
    readonly state: ModelFileState;
    readonly downloading_speed: number | null;
    readonly eta: number | null;
    readonly full_path: string;
    readonly is_extractable: boolean;
    readonly local_created_timestamp: Date | null;
    readonly local_modified_timestamp: Date | null;
    readonly remote_created_timestamp: Date | null;
    readonly remote_modified_timestamp: Date | null;
    readonly children: readonly ModelFile[];
}

export enum ModelFileState {
    DEFAULT = 'default',
    QUEUED = 'queued',
    DOWNLOADING = 'downloading',
    DOWNLOADED = 'downloaded',
    DELETED = 'deleted',
    EXTRACTING = 'extracting',
    EXTRACTED = 'extracted'
}

/**
 * Immutable ModelFile class using Object.freeze()
 */
export class ModelFile implements ModelFileData {
    readonly name: string;
    readonly is_dir: boolean;
    readonly local_size: number | null;
    readonly remote_size: number | null;
    readonly state: ModelFileState;
    readonly downloading_speed: number | null;
    readonly eta: number | null;
    readonly full_path: string;
    readonly is_extractable: boolean;
    readonly local_created_timestamp: Date | null;
    readonly local_modified_timestamp: Date | null;
    readonly remote_created_timestamp: Date | null;
    readonly remote_modified_timestamp: Date | null;
    readonly children: readonly ModelFile[];

    private constructor(data: ModelFileData) {
        this.name = data.name;
        this.is_dir = data.is_dir;
        this.local_size = data.local_size;
        this.remote_size = data.remote_size;
        this.state = data.state;
        this.downloading_speed = data.downloading_speed;
        this.eta = data.eta;
        this.full_path = data.full_path;
        this.is_extractable = data.is_extractable;
        this.local_created_timestamp = data.local_created_timestamp;
        this.local_modified_timestamp = data.local_modified_timestamp;
        this.remote_created_timestamp = data.remote_created_timestamp;
        this.remote_modified_timestamp = data.remote_modified_timestamp;
        this.children = data.children;
        Object.freeze(this);
    }

    /**
     * Create a new ModelFile with updated properties
     */
    update(updates: Partial<ModelFileData>): ModelFile {
        return new ModelFile({
            name: updates.name ?? this.name,
            is_dir: updates.is_dir ?? this.is_dir,
            local_size: updates.local_size !== undefined ? updates.local_size : this.local_size,
            remote_size: updates.remote_size !== undefined ? updates.remote_size : this.remote_size,
            state: updates.state ?? this.state,
            downloading_speed: updates.downloading_speed !== undefined ? updates.downloading_speed : this.downloading_speed,
            eta: updates.eta !== undefined ? updates.eta : this.eta,
            full_path: updates.full_path ?? this.full_path,
            is_extractable: updates.is_extractable ?? this.is_extractable,
            local_created_timestamp: updates.local_created_timestamp !== undefined ? updates.local_created_timestamp : this.local_created_timestamp,
            local_modified_timestamp: updates.local_modified_timestamp !== undefined ? updates.local_modified_timestamp : this.local_modified_timestamp,
            remote_created_timestamp: updates.remote_created_timestamp !== undefined ? updates.remote_created_timestamp : this.remote_created_timestamp,
            remote_modified_timestamp: updates.remote_modified_timestamp !== undefined ? updates.remote_modified_timestamp : this.remote_modified_timestamp,
            children: updates.children ?? this.children
        });
    }

    static fromJson(json: ModelFileJson): ModelFile {
        // Create immutable objects for children as well
        const children: ModelFile[] = json.children.map(child => ModelFile.fromJson(child));

        // State mapping
        const stateKey = json.state.toUpperCase() as keyof typeof ModelFileState;
        const state = ModelFileState[stateKey] ?? ModelFileState.DEFAULT;

        // Timestamps
        const local_created_timestamp = json.local_created_timestamp != null
            ? new Date(1000 * +json.local_created_timestamp)
            : null;
        const local_modified_timestamp = json.local_modified_timestamp != null
            ? new Date(1000 * +json.local_modified_timestamp)
            : null;
        const remote_created_timestamp = json.remote_created_timestamp != null
            ? new Date(1000 * +json.remote_created_timestamp)
            : null;
        const remote_modified_timestamp = json.remote_modified_timestamp != null
            ? new Date(1000 * +json.remote_modified_timestamp)
            : null;

        return new ModelFile({
            name: json.name,
            is_dir: json.is_dir,
            local_size: json.local_size,
            remote_size: json.remote_size,
            state,
            downloading_speed: json.downloading_speed,
            eta: json.eta,
            full_path: json.full_path,
            is_extractable: json.is_extractable,
            local_created_timestamp,
            local_modified_timestamp,
            remote_created_timestamp,
            remote_modified_timestamp,
            children: Object.freeze(children)
        });
    }
}

/**
 * JSON structure from backend
 */
export interface ModelFileJson {
    name: string;
    is_dir: boolean;
    local_size: number | null;
    remote_size: number | null;
    state: string;
    downloading_speed: number | null;
    eta: number | null;
    full_path: string;
    is_extractable: boolean;
    local_created_timestamp: number | null;
    local_modified_timestamp: number | null;
    remote_created_timestamp: number | null;
    remote_modified_timestamp: number | null;
    children: ModelFileJson[];
}
