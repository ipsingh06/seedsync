/**
 * AutoQueue Pattern
 */
export interface AutoQueuePatternData {
    readonly pattern: string;
}

/**
 * Immutable AutoQueuePattern class
 */
export class AutoQueuePattern implements AutoQueuePatternData {
    readonly pattern: string;

    constructor(data: AutoQueuePatternData) {
        this.pattern = data.pattern;
        Object.freeze(this);
    }

    /**
     * Create from JSON response
     */
    static fromJson(json: AutoQueuePatternJson): AutoQueuePattern {
        return new AutoQueuePattern({ pattern: json.pattern });
    }
}

/**
 * JSON structure from backend
 */
export interface AutoQueuePatternJson {
    pattern: string;
}
