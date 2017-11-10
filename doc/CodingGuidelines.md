# Coding Guidelines

## Python
1. Try not to throw exceptions in constructors.
Delay exceptions until after the web service is up and running.
This allows us to notify the user about the error.

2. Try to keep constructors short and passive.
Try not to start any threads or processes in constructors.