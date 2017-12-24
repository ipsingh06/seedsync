import {DashboardPage, File, FileActionButtonState} from "./dashboard.page";

describe('Testing dashboard page', () => {
    let page: DashboardPage;

    beforeEach(async () => {
        page = new DashboardPage();
        await page.navigateTo();
    });

    it('should have right top title', () => {
        expect(page.getTopTitle()).toEqual("Dashboard");
    });

    it('should have a list of files', () => {
        let golden = [
                new File("clients.jpg", '', "0 B of 36.5 KB"),
                new File("crispycat", '', "0 B of 1.53 MB"),
                new File("documentation.png", '', "0 B of 8.88 KB"),
                new File("goose", '', "0 B of 2.78 MB"),
                new File("illusion.jpg", '', "0 B of 81.5 KB"),
                new File("joke", '', "0 B of 168 KB"),
                new File("testing.gif", '', "0 B of 8.95 MB")
            ];
        expect(page.getFiles()).toEqual(golden);
    });

    it('should show and hide action buttons on select', () => {
        expect(page.isFileActionsVisible(1)).toBe(false);
        page.selectFile(1);
        expect(page.isFileActionsVisible(1)).toBe(true);
        page.selectFile(1);
        expect(page.isFileActionsVisible(1)).toBe(false);
    });

    it('should show action buttons for most recent file selected', () => {
        expect(page.isFileActionsVisible(1)).toBe(false);
        expect(page.isFileActionsVisible(2)).toBe(false);
        page.selectFile(1);
        expect(page.isFileActionsVisible(1)).toBe(true);
        expect(page.isFileActionsVisible(2)).toBe(false);
        page.selectFile(2);
        expect(page.isFileActionsVisible(1)).toBe(false);
        expect(page.isFileActionsVisible(2)).toBe(true);
        page.selectFile(2);
        expect(page.isFileActionsVisible(1)).toBe(false);
        expect(page.isFileActionsVisible(2)).toBe(false);
    });

    it('should have all the action buttons', async () => {
        await page.getFileActions(1).then(states => {
            expect(states.length).toBe(2);
            expect(states[0].title).toBe("Queue");
            expect(states[1].title).toBe("Stop");
        });
    });

    it('should have Queue action enabled for Default state', async () => {
        await page.getFiles().then(files => {
            expect(files[1].status).toEqual("");
        });
        await page.getFileActions(1).then(states => {
            expect(states[0].title).toBe("Queue");
            expect(states[0].isEnabled).toBe(true);
        });
    });

    it('should have Stop action disabled for Default state', async () => {
        await page.getFiles().then(files => {
            expect(files[1].status).toEqual("");
        });
        await page.getFileActions(1).then(states => {
            expect(states[1].title).toBe("Stop");
            expect(states[1].isEnabled).toBe(false);
        });
    });
});