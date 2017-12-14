import {AutoQueuePage} from "./autoqueue.page";

describe('Testing dashboard page', () => {
    let page: AutoQueuePage;

    beforeEach(() => {
        page = new AutoQueuePage();
        page.navigateTo();
    });

    it('should have right top title', () => {
        expect(page.getTopTitle()).toEqual("AutoQueue");
    });
});