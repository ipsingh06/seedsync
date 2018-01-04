import {browser, by, element} from 'protractor';
import {promise} from "selenium-webdriver";
import Promise = promise.Promise;

import {Urls} from "../urls";
import {App} from "./app";

export class AboutPage extends App {
    navigateTo() {
        return browser.get(Urls.APP_BASE_URL + "about");
    }

    getVersion(): Promise<string> {
        return element(by.css("#version")).getText();
    }
}