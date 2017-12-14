import {App} from "./app";

describe('Testing top-level app', () => {
    let app: App;

    beforeEach(() => {
        app = new App();
        app.navigateTo();
    });

    it('should have right title', () => {
        expect(app.getTitle()).toEqual("Pylftp");
    });

    it('should have all the sidebar items', () => {
        expect(app.getSidebarItems()).toEqual(
            [
                "Dashboard",
                "Settings",
                "AutoQueue",
                "Restart"
            ]
        );
    });

    it('should default to the dashboard page', () => {
        expect(app.getTopTitle()).toEqual("Dashboard");
    });
});