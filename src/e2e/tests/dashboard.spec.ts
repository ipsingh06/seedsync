import {DashboardPage} from "./dashboard.page";

describe('Testing dashboard page', () => {
    let page: DashboardPage;

    beforeEach(() => {
        page = new DashboardPage();
        page.navigateTo();
    });

    it('should have right title', () => {
        page.getTitle()
            .then((title: string) => {
                expect(title).toEqual('Pylftp');
            });
    });
});