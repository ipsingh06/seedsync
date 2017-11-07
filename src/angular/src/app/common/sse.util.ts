export class SseUtil {
    /**
     * Helper function to add a server-send event listener to an event source
     * Forwards the event and its data to the observer's next method
     * The next method receives objects with the following fields:
     *      event: str, event name
     *      data: str, event data
     * Source: https://stackoverflow.com/a/36827897/8571324
     * @param {string} eventName
     * @param eventSource
     * @param observer
     */
    public static addSseListener(eventName: string, eventSource, observer) {
        eventSource.addEventListener(eventName, event => observer.next(
            {
                "event": eventName,
                "data": event.data
            }
        ));
    }
}

