// Because this file imports from  protractor, you'll need to have it as a
// project dependency. Please see the reference config: lib/config.ts for more
// information.
//
// Why you might want to create your config with typescript:
// Editors like Microsoft Visual Studio Code will have autocomplete and
// description hints.
//
// To run this example, first transpile it to javascript with `npm run tsc`,
// then run `protractor conf.js`.
import {Config} from 'protractor';

import {Urls} from "./urls";

export let config: Config = {
    framework: 'jasmine',
    capabilities: {
        browserName: 'chrome'
    },
    specs: ['tests/**/*.spec.js'],
    seleniumAddress: Urls.SELENIUM_ADDRESS,

    // You could set no globals to true to avoid jQuery '$' and protractor '$'
    // collisions on the global namespace.
    noGlobals: true,

    allScriptsTimeout: 5000,

    // Options to be passed to Jasmine-node.
    jasmineNodeOpts: {
        showColors: true,
        defaultTimeoutInterval: 3000
    }
};
