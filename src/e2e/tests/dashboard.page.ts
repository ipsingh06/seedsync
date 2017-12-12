import {browser, by, element} from 'protractor';

export class DashboardPage {
    navigateTo() {
        return browser.get("http://localhost:8800/");
    }

    getTitle() {
        return browser.getTitle();
    }

    // getParagraphText() {
    //     return element(by.css('app-root h1')).getText();
    // }
}