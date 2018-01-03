import {AutoQueuePage} from "./autoqueue.page";

describe('Testing autoqueue page', () => {
    let page: AutoQueuePage;

    beforeEach(() => {
        page = new AutoQueuePage();
        page.navigateTo();
    });

    it('should have right top title', () => {
        expect(page.getTopTitle()).toEqual("AutoQueue");
    });


    it('should add and remove patterns', () => {
        // start with an empty list
        expect(page.getPatterns()).toEqual([]);

        // add some patterns, and expect them in added order
        page.addPattern("APattern");
        page.addPattern("CPattern");
        page.addPattern("DPattern");
        page.addPattern("BPattern");
        expect(page.getPatterns()).toEqual([
            "APattern", "CPattern", "DPattern", "BPattern"
        ]);

        // remove patterns one by one
        page.removePattern(2);
        expect(page.getPatterns()).toEqual([
            "APattern", "CPattern", "BPattern"
        ]);
        page.removePattern(0);
        expect(page.getPatterns()).toEqual([
            "CPattern", "BPattern"
        ]);
        page.removePattern(1);
        expect(page.getPatterns()).toEqual([
            "CPattern"
        ]);
        page.removePattern(0);
        expect(page.getPatterns()).toEqual([]);
    });

    it('should list existing patterns in alphabetical order', () => {
        // start with an empty list
        expect(page.getPatterns()).toEqual([]);

        // add some patterns, and expect them in added order
        page.addPattern("APattern");
        page.addPattern("CPattern");
        page.addPattern("DPattern");
        page.addPattern("BPattern");

        // reload the page
        page.navigateTo();

        // patterns should be in alphabetical order
        expect(page.getPatterns()).toEqual([
            "APattern", "BPattern", "CPattern", "DPattern"
        ]);

        // remove all patterns
        page.removePattern(0);
        page.removePattern(0);
        page.removePattern(0);
        page.removePattern(0);
        expect(page.getPatterns()).toEqual([]);
    });
});