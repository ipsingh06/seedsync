import {DashboardPage} from "./dashboard.page";

describe('Testing dashboard page', () => {
    let page: DashboardPage;

    beforeEach(() => {
        page = new DashboardPage();
        page.navigateTo();
    });

    it('should have right top title', () => {
        expect(page.getTopTitle()).toEqual("Dashboard");
    });
});