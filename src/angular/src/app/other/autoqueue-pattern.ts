import {Record} from 'immutable';

interface IAutoQueuePattern {
    pattern: string;
}
const DefaultAutoQueuePattern: IAutoQueuePattern = {
    pattern: null
};
const AutoQueuePatternRecord = Record(DefaultAutoQueuePattern);


export class AutoQueuePattern extends AutoQueuePatternRecord implements IAutoQueuePattern {
    pattern: string;

    constructor(props) {
        super(props);
    }
}

/**
 * ServerStatus as serialized by the backend.
 * Note: naming convention matches that used in JSON
 */
export interface AutoQueuePatternJson {
    pattern: string;
}
