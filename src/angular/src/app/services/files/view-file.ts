/**
 * View file - Represents the View Model
 */
export interface ViewFileData {
    readonly name: string;
    readonly isDir: boolean;
    readonly localSize: number | null;
    readonly remoteSize: number | null;
    readonly percentDownloaded: number | null;
    readonly status: ViewFileStatus;
    readonly downloadingSpeed: number | null;
    readonly eta: number | null;
    readonly fullPath: string;
    readonly isArchive: boolean;  // corresponds to is_extractable in ModelFile
    readonly isSelected: boolean;
    readonly isQueueable: boolean;
    readonly isStoppable: boolean;
    // whether file can be queued for extraction (independent of isArchive)
    readonly isExtractable: boolean;
    readonly isLocallyDeletable: boolean;
    readonly isRemotelyDeletable: boolean;
    // timestamps
    readonly localCreatedTimestamp: Date | null;
    readonly localModifiedTimestamp: Date | null;
    readonly remoteCreatedTimestamp: Date | null;
    readonly remoteModifiedTimestamp: Date | null;
}

export enum ViewFileStatus {
    DEFAULT = 'default',
    QUEUED = 'queued',
    DOWNLOADING = 'downloading',
    DOWNLOADED = 'downloaded',
    STOPPED = 'stopped',
    DELETED = 'deleted',
    EXTRACTING = 'extracting',
    EXTRACTED = 'extracted'
}

/**
 * Immutable ViewFile class
 */
export class ViewFile implements ViewFileData {
    readonly name: string;
    readonly isDir: boolean;
    readonly localSize: number | null;
    readonly remoteSize: number | null;
    readonly percentDownloaded: number | null;
    readonly status: ViewFileStatus;
    readonly downloadingSpeed: number | null;
    readonly eta: number | null;
    readonly fullPath: string;
    readonly isArchive: boolean;
    readonly isSelected: boolean;
    readonly isQueueable: boolean;
    readonly isStoppable: boolean;
    readonly isExtractable: boolean;
    readonly isLocallyDeletable: boolean;
    readonly isRemotelyDeletable: boolean;
    readonly localCreatedTimestamp: Date | null;
    readonly localModifiedTimestamp: Date | null;
    readonly remoteCreatedTimestamp: Date | null;
    readonly remoteModifiedTimestamp: Date | null;

    constructor(data: ViewFileData) {
        this.name = data.name;
        this.isDir = data.isDir;
        this.localSize = data.localSize;
        this.remoteSize = data.remoteSize;
        this.percentDownloaded = data.percentDownloaded;
        this.status = data.status;
        this.downloadingSpeed = data.downloadingSpeed;
        this.eta = data.eta;
        this.fullPath = data.fullPath;
        this.isArchive = data.isArchive;
        this.isSelected = data.isSelected;
        this.isQueueable = data.isQueueable;
        this.isStoppable = data.isStoppable;
        this.isExtractable = data.isExtractable;
        this.isLocallyDeletable = data.isLocallyDeletable;
        this.isRemotelyDeletable = data.isRemotelyDeletable;
        this.localCreatedTimestamp = data.localCreatedTimestamp;
        this.localModifiedTimestamp = data.localModifiedTimestamp;
        this.remoteCreatedTimestamp = data.remoteCreatedTimestamp;
        this.remoteModifiedTimestamp = data.remoteModifiedTimestamp;
        Object.freeze(this);
    }

    /**
     * Create a new ViewFile with updated properties
     */
    update(updates: Partial<ViewFileData>): ViewFile {
        return new ViewFile({
            name: updates.name ?? this.name,
            isDir: updates.isDir ?? this.isDir,
            localSize: updates.localSize !== undefined ? updates.localSize : this.localSize,
            remoteSize: updates.remoteSize !== undefined ? updates.remoteSize : this.remoteSize,
            percentDownloaded: updates.percentDownloaded !== undefined ? updates.percentDownloaded : this.percentDownloaded,
            status: updates.status ?? this.status,
            downloadingSpeed: updates.downloadingSpeed !== undefined ? updates.downloadingSpeed : this.downloadingSpeed,
            eta: updates.eta !== undefined ? updates.eta : this.eta,
            fullPath: updates.fullPath ?? this.fullPath,
            isArchive: updates.isArchive ?? this.isArchive,
            isSelected: updates.isSelected ?? this.isSelected,
            isQueueable: updates.isQueueable ?? this.isQueueable,
            isStoppable: updates.isStoppable ?? this.isStoppable,
            isExtractable: updates.isExtractable ?? this.isExtractable,
            isLocallyDeletable: updates.isLocallyDeletable ?? this.isLocallyDeletable,
            isRemotelyDeletable: updates.isRemotelyDeletable ?? this.isRemotelyDeletable,
            localCreatedTimestamp: updates.localCreatedTimestamp !== undefined ? updates.localCreatedTimestamp : this.localCreatedTimestamp,
            localModifiedTimestamp: updates.localModifiedTimestamp !== undefined ? updates.localModifiedTimestamp : this.localModifiedTimestamp,
            remoteCreatedTimestamp: updates.remoteCreatedTimestamp !== undefined ? updates.remoteCreatedTimestamp : this.remoteCreatedTimestamp,
            remoteModifiedTimestamp: updates.remoteModifiedTimestamp !== undefined ? updates.remoteModifiedTimestamp : this.remoteModifiedTimestamp
        });
    }
}
