# Coding Guidelines

## Python
1. Try not to throw exceptions in constructors.
Delay exceptions until after the web service is up and running.
This allows us to notify the user about the error.

2. Try to keep constructors short and passive.
Try not to start any threads or processes in constructors.

3. Do not rely on timing constraints in tests.
That is, don't use `time.sleep()` to wait for something to happen.
Actually wait for the condition and use a watchdog timer to check for failure.

## Angular
1. Keep constructor of Immutable.Record blank.
Any pre-processing that is needed to convert a JS object to Record should be put in a factory function.
This ensures that the Record object can be easily constructed for tests without having to know the JS object translations.
