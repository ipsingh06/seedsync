import {fakeAsync, TestBed, tick} from "@angular/core/testing";

import * as compareVersions from "compare-versions";

import {VersionCheckService} from "../../../../services/utils/version-check.service";
import {RestService, WebReaction} from "../../../../services/utils/rest.service";
import {NotificationService} from "../../../../services/utils/notification.service";
import {LoggerService} from "../../../../services/utils/logger.service";
import {MockRestService} from "../../../mocks/mock-rest.service";
import {Subject} from "rxjs/Subject";


describe("Testing version check service", () => {
    let versionCheckService: VersionCheckService;
    let notifService: NotificationService;
    let restService: RestService;

    let sendRequestSpy = null;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                VersionCheckService,
                LoggerService,
                NotificationService,
                {provide: RestService, useClass: MockRestService},
            ]
        });

        notifService = TestBed.get(NotificationService);
        restService = TestBed.get(RestService);

        spyOn(notifService, "show");
        sendRequestSpy = spyOn(restService, "sendRequest").and.returnValue(
            new Subject<WebReaction>());

        versionCheckService = TestBed.get(VersionCheckService);
    });

    function createVersionCheckService(): VersionCheckService {
        return new VersionCheckService(
            restService,
            notifService,
            TestBed.get(LoggerService)
        );
    }

    it("should create an instance", () => {
        expect(versionCheckService).toBeDefined();
    });

    it("should request the correct github url", fakeAsync(() => {
        expect(restService.sendRequest).toHaveBeenCalledWith(
            "https://api.github.com/repos/ipsingh06/seedsync/releases/latest"
        );
    }));

    it("should fail gracefully on failed request to github", fakeAsync(() => {
        const subject = new Subject<WebReaction>();
        sendRequestSpy.and.returnValue(subject);

        // Recreate the service
        versionCheckService = createVersionCheckService();
        subject.next(new WebReaction(false, null, "some error"));
        tick();

        expect(notifService.show).not.toHaveBeenCalled();
    }));

    it("should fail gracefully on garbage data from github", fakeAsync(() => {
        const subject = new Subject<WebReaction>();
        sendRequestSpy.and.returnValue(subject);

        // Recreate the service
        versionCheckService = createVersionCheckService();
        subject.next(new WebReaction(true, "garbage data", null));
        tick();

        expect(notifService.show).not.toHaveBeenCalled();
    }));

    it("should fire a notification on new version", fakeAsync(() => {
        const subject = new Subject<WebReaction>();
        sendRequestSpy.and.returnValue(subject);

        // Note: can't spy on compareVersions, so just replace the private method instead
        spyOn<any>(VersionCheckService, "isVersionNewer").and.returnValue(true);

        // Recreate the service
        versionCheckService = createVersionCheckService();
        subject.next(new WebReaction(true, JSON.stringify({"tag_name": "v0.0-0"}), null));
        tick();

        expect(notifService.show).toHaveBeenCalled();
    }));

    it("should not fire a notification on old version", fakeAsync(() => {
        const subject = new Subject<WebReaction>();
        sendRequestSpy.and.returnValue(subject);

        // Note: can't spy on compareVersions, so just replace the private method instead
        spyOn<any>(VersionCheckService, "isVersionNewer").and.returnValue(false);

        // Recreate the service
        versionCheckService = createVersionCheckService();
        subject.next(new WebReaction(true, JSON.stringify({"tag_name": "v0.0-0"}), null));
        tick();

        expect(notifService.show).not.toHaveBeenCalled();
    }));
});
