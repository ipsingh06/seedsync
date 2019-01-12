declare let spyOn: any;

export class MockEventSource {
    url: string;
    onopen: (event: Event) => any;
    onerror: (event: Event) => any;

    eventListeners: Map<string, EventListener> = new Map();

    constructor(url: string) {
        this.url = url;
    }

    addEventListener(type: string, listener: EventListener) {
        this.eventListeners.set(type, listener);
    }

    close() {}
}

export function createMockEventSource(url: string): MockEventSource {
    let mockEventSource = new MockEventSource(url);
    spyOn(mockEventSource, 'addEventListener').and.callThrough();
    spyOn(mockEventSource, 'close').and.callThrough();
    return mockEventSource;
}
