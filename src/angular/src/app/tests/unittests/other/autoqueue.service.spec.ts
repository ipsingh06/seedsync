import {fakeAsync, TestBed, tick} from "@angular/core/testing";
import {HttpClientTestingModule, HttpTestingController} from "@angular/common/http/testing";

import * as Immutable from "immutable";

import {LoggerService} from "../../../common/logger.service";
import {AutoQueueService} from "../../../other/autoqueue.service";
import {AutoQueuePattern} from "../../../other/autoqueue-pattern";
import {EventSourceFactory} from "../../../common/base-stream.service";
import {createMockEventSource, MockEventSource} from "../../mocks/common/mock-event-source";

// noinspection JSUnusedLocalSymbols
const DoNothing = {next: reaction => {}};


describe("Testing autoqueue service", () => {
    let httpMock: HttpTestingController;
    let aqService: AutoQueueService;

    let mockEventSource: MockEventSource;

    beforeEach(fakeAsync(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule
            ],
            providers: [
                LoggerService,
                AutoQueueService,
            ]
        });

        spyOn(EventSourceFactory, 'createEventSource').and.callFake(
            (url: string) => {
                mockEventSource = createMockEventSource(url);
                return mockEventSource;
            }
        );

        httpMock = TestBed.get(HttpTestingController);
        aqService = TestBed.get(AutoQueueService);

        // Finish test config init
        aqService.onInit();

        // Connect the service
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();
    }));

    it("should create an instance", () => {
        expect(aqService).toBeDefined();
    });

    it("should parse patterns json correctly", fakeAsync(() => {
        const patternsJson = [
            {"pattern": "one"},
            {"pattern": "tw o"},
            {"pattern": "th'ree"},
            {"pattern": "fo\"ur"},
            {"pattern": "fi%ve"},
        ];
        httpMock.expectOne("/server/autoqueue/get").flush(patternsJson);

        const expectedPatterns = [
            new AutoQueuePattern({pattern: "one"}),
            new AutoQueuePattern({pattern: "tw o"}),
            new AutoQueuePattern({pattern: "th'ree"}),
            new AutoQueuePattern({pattern: "fo\"ur"}),
            new AutoQueuePattern({pattern: "fi%ve"})
        ];

        let actualCount = 0;
        aqService.patterns.subscribe({
            next: patterns => {
                expect(patterns.size).toBe(5);
                for (let i = 0; i < patterns.size; i++) {
                    expect(Immutable.is(patterns.get(i), expectedPatterns[i])).toBe(true);
                }
                actualCount++;
            }
        });

        tick();
        expect(actualCount).toBe(1);
        httpMock.verify();
    }));

    it("should get empty list on get error 404", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush(
        "Not found",
        {status: 404, statusText: "Bad Request"}
        );

        let actualCount = 0;
        aqService.patterns.subscribe({
            next: patterns => {
                expect(patterns.size).toBe(0);
                actualCount++;
            }
        });


        tick();
        expect(actualCount).toBe(1);
        httpMock.verify();
    }));

    it("should get empty list on get network error", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").error(new ErrorEvent("mock error"));

        let actualCount = 0;
        aqService.patterns.subscribe({
            next: patterns => {
                expect(patterns.size).toBe(0);
                actualCount++;
            }
        });


        tick();
        expect(actualCount).toBe(1);
        httpMock.verify();
    }));

    it("should get empty list on disconnect", fakeAsync(() => {
        const patternsJson = [
            {"pattern": "one"}
        ];
        httpMock.expectOne("/server/autoqueue/get").flush(patternsJson);

        const expectedPatterns = [
            Immutable.List([new AutoQueuePattern({pattern: "one"})]),
            Immutable.List([])
        ];

        let actualCount = 0;
        aqService.patterns.subscribe({
            next: patterns => {
                expect(Immutable.is(patterns, expectedPatterns[actualCount++])).toBe(true);
            }
        });

        tick();

        // status disconnect
        mockEventSource.onerror(new Event("bad event"));
        tick();

        expect(actualCount).toBe(2);
        httpMock.verify();
        tick(4000);
    }));

    it("should retry GET on disconnect", fakeAsync(() => {
        // first connect
        httpMock.expectOne("/server/autoqueue/get").flush("[]");

        tick();

        // status disconnect
        mockEventSource.onerror(new Event("bad event"));
        tick(4000);

        // status reconnect
        mockEventSource.eventListeners.get("status")({data: "doesn't matter"});
        tick();

        httpMock.expectOne("/server/autoqueue/get").flush("[]");
        tick();
        httpMock.verify();
    }));

    it("should send a GET on add pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([]);

        let actualCount = 0;
        aqService.add("one").subscribe({
            next: reaction => {
               expect(reaction.success).toBe(true);
               actualCount++;
            }
        });
        httpMock.expectOne("/server/autoqueue/add/one").flush("{}");

        tick();

        expect(actualCount).toBe(1);
        httpMock.verify();
    }));

    it("should send correct GET requests on add pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([]);

        aqService.add("test").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/add/test").flush("{}");
        aqService.add("test space").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/add/test%2520space").flush("{}");
        aqService.add("test/slash").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/add/test%252Fslash").flush("{}");
        aqService.add("test\"doublequote").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/add/test%2522doublequote").flush("{}");
        aqService.add("/test/leadingslash").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/add/%252Ftest%252Fleadingslash").flush("{}");

        httpMock.verify();
    }));

    it("should return error on adding existing pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([
            {"pattern": "one"}
        ]);

        let actualCount = 0;
        aqService.add("one").subscribe({
            next: reaction => {
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Pattern 'one' already exists.");
               actualCount++;
            }
        });
        httpMock.expectNone("/server/autoqueue/add/one");

        tick();

        expect(actualCount).toBe(1);
        httpMock.verify();
    }));

    it("should return error on adding empty pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([]);

        let actualCount = 0;
        aqService.add("").subscribe({
            next: reaction => {
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Cannot add an empty autoqueue pattern.");
               actualCount++;
            }
        });
        aqService.add(" ").subscribe({
            next: reaction => {
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Cannot add an empty autoqueue pattern.");
               actualCount++;
            }
        });
        aqService.add(null).subscribe({
            next: reaction => {
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Cannot add an empty autoqueue pattern.");
               actualCount++;
            }
        });
        httpMock.expectNone("/server/autoqueue/add/");

        tick();

        expect(actualCount).toBe(3);
        httpMock.verify();
    }));

    it("should send updated patterns after an add pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([]);


        const expectedPatterns = [
            Immutable.List([]),
            Immutable.List([new AutoQueuePattern({pattern: "one"})])
        ];

        let actualCount = 0;
        aqService.patterns.subscribe({
            next: patterns => {
                expect(Immutable.is(patterns, expectedPatterns[actualCount++])).toBe(true);
            }
        });

        aqService.add("one").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/add/one").flush("{}");

        tick();

        expect(actualCount).toBe(2);
        httpMock.verify();
    }));

    it("should NOT send updated patterns after a failed add", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([
            new AutoQueuePattern({pattern: "one"})
        ]);

        const expectedPatterns = [
            Immutable.List([new AutoQueuePattern({pattern: "one"})])
        ];

        let actualCount = 0;
        aqService.patterns.subscribe({
            next: patterns => {
                expect(Immutable.is(patterns, expectedPatterns[actualCount++])).toBe(true);
            }
        });

        aqService.add("one").subscribe(DoNothing);
        httpMock.expectNone("/server/autoqueue/add/one");

        tick();

        expect(actualCount).toBe(1);
        httpMock.verify();
    }));

    it("should send a GET on remove pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([
            new AutoQueuePattern({pattern: "one"})
        ]);

        let actualCount = 0;
        aqService.remove("one").subscribe({
            next: reaction => {
               expect(reaction.success).toBe(true);
               actualCount++;
            }
        });
        httpMock.expectOne("/server/autoqueue/remove/one").flush("{}");

        tick();

        expect(actualCount).toBe(1);
        httpMock.verify();
    }));

    it("should send correct GET requests on remove pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([
            new AutoQueuePattern({pattern: "test"}),
            new AutoQueuePattern({pattern: "test space"}),
            new AutoQueuePattern({pattern: "test/slash"}),
            new AutoQueuePattern({pattern: "test\"doublequote"}),
            new AutoQueuePattern({pattern: "/test/leadingslash"})
        ]);

        aqService.remove("test").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/remove/test").flush("{}");
        aqService.remove("test space").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/remove/test%2520space").flush("{}");
        aqService.remove("test/slash").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/remove/test%252Fslash").flush("{}");
        aqService.remove("test\"doublequote").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/remove/test%2522doublequote").flush("{}");
        aqService.remove("/test/leadingslash").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/remove/%252Ftest%252Fleadingslash").flush("{}");

        httpMock.verify();
    }));

    it("should return error on removing non-existing pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([
        ]);

        let actualCount = 0;
        aqService.remove("one").subscribe({
            next: reaction => {
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Pattern 'one' not found.");
               actualCount++;
            }
        });
        httpMock.expectNone("/server/autoqueue/remove/one");

        tick();

        expect(actualCount).toBe(1);
        httpMock.verify();
    }));

    it("should return error on removing empty pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([
        ]);

        let actualCount = 0;
        aqService.remove("").subscribe({
            next: reaction => {
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Pattern '' not found.");
               actualCount++;
            }
        });
        aqService.remove(" ").subscribe({
            next: reaction => {
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Pattern ' ' not found.");
               actualCount++;
            }
        });
        aqService.remove(null).subscribe({
            next: reaction => {
               expect(reaction.success).toBe(false);
               expect(reaction.errorMessage).toBe("Pattern 'null' not found.");
               actualCount++;
            }
        });
        httpMock.expectNone("/server/autoqueue/remove/");

        tick();

        expect(actualCount).toBe(3);
        httpMock.verify();
    }));

    it("should send updated patterns after a remove pattern", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([
            new AutoQueuePattern({pattern: "one"}),
            new AutoQueuePattern({pattern: "two"})
        ]);


        const expectedPatterns = [
            Immutable.List([
                new AutoQueuePattern({pattern: "one"}),
                new AutoQueuePattern({pattern: "two"})
            ]),
            Immutable.List([
                new AutoQueuePattern({pattern: "two"})
            ])
        ];

        let actualCount = 0;
        aqService.patterns.subscribe({
            next: patterns => {
                expect(Immutable.is(patterns, expectedPatterns[actualCount++])).toBe(true);
            }
        });

        aqService.remove("one").subscribe(DoNothing);
        httpMock.expectOne("/server/autoqueue/remove/one").flush("{}");

        tick();

        expect(actualCount).toBe(2);
        httpMock.verify();
    }));

    it("should NOT send updated patterns after a failed remove", fakeAsync(() => {
        httpMock.expectOne("/server/autoqueue/get").flush([
            new AutoQueuePattern({pattern: "one"})
        ]);

        const expectedPatterns = [
            Immutable.List([new AutoQueuePattern({pattern: "one"})])
        ];

        let actualCount = 0;
        aqService.patterns.subscribe({
            next: patterns => {
                expect(Immutable.is(patterns, expectedPatterns[actualCount++])).toBe(true);
            }
        });

        aqService.remove("two").subscribe(DoNothing);
        httpMock.expectNone("/server/autoqueue/remove/two");

        tick();

        expect(actualCount).toBe(1);
        httpMock.verify();
    }));
});
