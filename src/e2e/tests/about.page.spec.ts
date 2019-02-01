import {AboutPage} from "./about.page";

describe('Testing about page', () => {
    let page: AboutPage;

    beforeEach(() => {
        page = new AboutPage();
        page.navigateTo();
    });

    it('should have right top title', () => {
        expect(page.getTopTitle()).toEqual("About");
    });

    it('should have the right version', () => {
        expect(page.getVersion()).toEqual("v0.7.0");
    });
});