import {browser, by, element} from 'protractor';

import {Urls} from "../urls";

export class DashboardPage {
    navigateTo() {
        return browser.get(Urls.APP_BASE_URL);
    }

    getTitle() {
        return browser.getTitle();
    }

    // getParagraphText() {
    //     return element(by.css('app-root h1')).getText();
    // }
}