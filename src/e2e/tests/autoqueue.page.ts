import {browser, by, element} from 'protractor';
import {promise} from "selenium-webdriver";
import Promise = promise.Promise;

import {Urls} from "../urls";
import {App} from "./app";

export class AutoQueuePage extends App {
    navigateTo() {
        return browser.get(Urls.APP_BASE_URL + "autoqueue");
    }

    getPatterns(): Promise<Array<string>> {
        return element.all(by.css("#autoqueue .pattern span.text")).map(function (elm) {
            return browser.executeScript("return arguments[0].innerHTML;", elm);
        });
    }

    addPattern(pattern: string) {
        let input = element(by.css("#add-pattern input"));
        input.sendKeys(pattern);
        let button = element(by.css("#add-pattern .button"));
        button.click();
    }

    removePattern(index: number) {
        let button = element.all(by.css("#autoqueue .pattern")).get(index).element(by.css(".button"));
        button.click();
    }
}