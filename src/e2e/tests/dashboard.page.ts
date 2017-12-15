import {browser, by, element, ExpectedConditions} from 'protractor';
import {promise} from "selenium-webdriver";
import Promise = promise.Promise;

import {Urls} from "../urls";
import {App} from "./app";

export class File {
    constructor(public name,
                public status,
                public size) {
    }
}

export class FileActionButtonState {
    constructor(public title,
                public isEnabled) {
    }
}

export class DashboardPage extends App {
    navigateTo() {
        return browser.get(Urls.APP_BASE_URL + "dashboard").then(value => {
            // Wait for the files list to show up
            return browser.wait(ExpectedConditions.presenceOf(
                element.all(by.css("#file-list .file")).first()
            ));
        })
    }

    getFiles(): Promise<Array<File>> {
        return element.all(by.css("#file-list .file")).map(function (elm) {
            let name = elm.element(by.css(".name .text")).getText();
            let statusElm = elm.element(by.css(".content .status"));
            let status = statusElm.isElementPresent(by.css("span.text")).then(value => {
                if(value) {
                    return browser.executeScript(
                        "return arguments[0].innerHTML;",
                        statusElm.element(by.css("span.text"))
                    );
                } else {
                    return "";
                }
            });
            // let status = browser.executeScript("return arguments[0].innerHTML;", subelm);
            let size = elm.element(by.css(".size .size_info")).getText();
            return new File(name, status, size);
        });
    }

    selectFile(index: number) {
        element.all(by.css("#file-list .file")).get(index).click();
    }

    isFileActionsVisible(index: number) {
        return element.all(by.css("#file-list .file")).get(index)
                            .element(by.css(".actions")).isDisplayed();
    }

    getFileActions(index: number): Promise<Array<FileActionButtonState>> {
        return element.all(by.css("#file-list .file")).get(index)
                    .element(by.css(".actions"))
                    .all(by.css(".button"))
                    .map(buttonElm => {
                        let title = browser.executeScript(
                            "return arguments[0].innerHTML;",
                            buttonElm.element(by.css("span.text"))
                        );
                        let isEnabled = buttonElm.getAttribute("disabled").then(value => {
                            return value == null;
                        });
                        return new FileActionButtonState(title, isEnabled);
                    });
    }
}