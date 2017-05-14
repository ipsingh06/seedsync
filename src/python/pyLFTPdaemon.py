# To kick off the script, run the following from the python directory:
#   PYTHONPATH=`pwd` python pyLFTPdaemon.py start

# standard python libs
import math
import logging
import time
import os
import ConfigParser
import sys
import subprocess
import threading
import time
import thread
from pwd import getpwnam

# third party libs
import web
from daemon import runner

debugMode = True  # Set's various print out options
homeDir = "/home/someone"  # for reading config file
webServerPort = '88'  # Port for web server

urls = (
    '/', 'index',
    '/command/(.*)/(.*)', 'command',
    '/json/(.*)', 'json',
    '/files/(.*)', 'static',
)


class static:
    def GET(self, file):
        try:
            f = open(os.path.dirname(os.path.realpath(__file__)) + '/files/' + file, 'r')
            return f.read()
        except:
            return web.notfound()


class command:
    def GET(self, command, parameters):
        if command == 'add':
            web.ctx.pyLFTPInst.addRuntimeQueue(parameters)
            return "Added " + parameters + " to runtime queue"
        else:
            return web.notfound()


class json:
    def GET(self, filter):
        if filter == 'all':
            allFiles = self.__getFilteredFileData(web.ctx.pipe)
            return self.__getJSON(allFiles)
        elif filter == 'queued':
            queuedFiles = self.__getFilteredFileData(web.ctx.pipe, status=[FileState.queued, FileState.downloading,
                                                                           FileState.downloaded])
            return self.__getJSON(queuedFiles)
        else:
            return web.notfound()

    def __getJSON(self, database):
        output = ""
        output += '{\n'
        output += '\t "totalRecords": "%d",\n' % len(database)
        output += '\t "aaData": [\n'

        first = True
        for file in database:
            if first:
                first = False
            else:
                output += '\t\t ],\n'
            output += '\t\t [\n'
            output += '\t\t\t "%s",\n' % file.filename
            output += '\t\t\t "%s",\n' % FileStatePrintable[file.status]
            output += '\t\t\t "%s",\n' % self.__sizeof_fmt(int(file.getSpeed()), speed=True)
            output += '\t\t\t "%s",\n' % self.__sizeof_fmt(file.remoteSize)
            output += '\t\t\t "%s",\n' % self.__sizeof_fmt(file.localSize)
            output += '\t\t\t "%d",\n' % (int(100 * file.localSize / file.remoteSize) if file.remoteSize > 0 else 0)
            output += '\t\t\t ""\n'
        if len(database) > 0:
            output += '\t\t ]\n'

        output += '\t ]\n'
        output += '}'
        return output

    def __getFilteredFileData(self, database, status=None):
        filteredDatabase = []
        for file in database:
            doInclude = True
            if status is not None and status != file.status and file.status not in status:
                doInclude = False
            if doInclude:
                filteredDatabase.append(file)
        return filteredDatabase

    def __sizeof_fmt(self, num, speed=False):
        units = []
        if speed:
            units = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s']
        else:
            units = ['bytes', 'KB', 'MB', 'GB', 'TB']
        for x in units:
            if num == 0:
                return "0 %s" % (x)
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
        return "%3.1f %s" % (num, units[-1])


class index:
    def GET(self):
        index = web.template.frender(os.path.dirname(os.path.realpath(__file__)) + '/index.html')
        return index()


# Hack to create enums
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


FileState = enum(downloading='downloading', downloaded='downloaded', queued='queued', deleted='deleted',
                 no_match='no_match')
BuildType = enum(full='full', local='local', downloading='downloading')

FileStatePrintable = {'downloading': 'Downloading',
                      'downloaded': 'Downloaded',
                      'queued': 'Queued',
                      'deleted': 'Deleted',
                      'no_match': 'No Match',
                      }

appName = "pyLFTPdaemon"


class pyLFTPdaemon():
    def __init__(self):
        self.stdin_path = '/dev/null'
        if debugMode:
            self.stdout_path = "/var/log/%s/%s.log" % (appName, appName)
            self.stderr_path = "/var/log/%s/%s.log" % (appName, appName)
        else:
            self.stdout_path = '/dev/null'
            self.stderr_path = '/dev/null'
        self.pidfile_path = '/var/run/%s/%s.pid' % (appName, appName)
        self.pidfile_timeout = 5

        self.pyLFTPInst = pyLFTP()

    def run(self):
        logger.info("Started daemon")
        logger.debug("Debug mode enabled")

        # Launch the webserver
        sys.argv[1] = webServerPort  # Hack, web.py expects port number as first parameter
        app = web.application(urls, globals(), autoreload=True)
        app.add_processor(web.loadhook(self.pyLFTPInst.webLoadHook))
        thread.start_new_thread(app.run, ())

        # Read in the config
        self.pyLFTPInst.readConfig()

        # Grab some config parameters
        minFullIntervalTime = self.pyLFTPInst.config["TimeParameters"]["minfullinterval"]
        minLocalIntervalTime = self.pyLFTPInst.config["TimeParameters"]["minlocalinterval"]
        minDownloadingIntervalTime = self.pyLFTPInst.config["TimeParameters"]["mindownloadinginterval"]
        watchdogIntervalTime = self.pyLFTPInst.config["TimeParameters"]["watchdoginterval"]

        # Build initial remote database from scratch
        self.pyLFTPInst.buildRemoteFileDatabase(buildType=BuildType.full)

        currentTime = int(round(time.time() * 1000))
        lastFullBuildTime = currentTime
        lastLocalBuildTime = currentTime
        lastWatchdogTime = currentTime

        while True:
            # Main code goes here ...
            # Note that logger level needs to be set to logging.DEBUG before this shows up in the logs
            # logger.debug("Debug message")
            # logger.warn("Warning message")
            # logger.error("Error message")
            # logger.info("Info message")

            currentTime = int(round(time.time() * 1000))
            timeToSleep = 0.0

            # Process incoming commands
            if self.pyLFTPInst.forceLocalUpdate:
                self.pyLFTPInst.forceLocalUpdate = False
                self.pyLFTPInst.buildRemoteFileDatabase(buildType=BuildType.local)
                lastLocalBuildTime = currentTime

            # Regular state machine
            if self.pyLFTPInst.isProcessOngoing():
                # A download is under way
                # Update the database, and do nothing else
                if lastFullBuildTime + int(minFullIntervalTime) < currentTime:
                    self.pyLFTPInst.buildRemoteFileDatabase(buildType=BuildType.full)
                    lastFullBuildTime = currentTime
                    lastLocalBuildTime = currentTime
                elif lastLocalBuildTime + int(minLocalIntervalTime) < currentTime:
                    self.pyLFTPInst.buildRemoteFileDatabase(buildType=BuildType.local)
                    lastLocalBuildTime = currentTime
                elif not self.pyLFTPInst.isFileDownloading():
                    # Recently started file's status hasn't updated, do local build to update its status
                    self.pyLFTPInst.buildRemoteFileDatabase(buildType=BuildType.local)
                    lastLocalBuildTime = currentTime
                else:
                    self.pyLFTPInst.buildRemoteFileDatabase(buildType=BuildType.downloading)

                # Run the downloading watchdog
                if lastWatchdogTime + int(watchdogIntervalTime) < currentTime:
                    self.pyLFTPInst.watchdog()
                    lastWatchdogTime = currentTime

                # Sleep for a short while
                timeToSleep = float(minDownloadingIntervalTime) / 1000.0
            else:
                # No download is under way
                # Do a full build if needed, otherwise a local build to update any finished downloading files
                if lastFullBuildTime + int(minFullIntervalTime) < currentTime:
                    self.pyLFTPInst.buildRemoteFileDatabase(buildType=BuildType.full)
                    lastFullBuildTime = currentTime
                    lastLocalBuildTime = currentTime
                else:
                    self.pyLFTPInst.buildRemoteFileDatabase(buildType=BuildType.local)

                if self.pyLFTPInst.isFileQueued():
                    # There is a file queued, start downloading it
                    self.pyLFTPInst.startQueuedDownload()

                    # Sleep for a short while
                    timeToSleep = float(minDownloadingIntervalTime) / 1000.0

                elif self.pyLFTPInst.isFileDownloading():
                    # Previously downloading file needs its state updated, do a short wait
                    timeToSleep = float(minDownloadingIntervalTime) / 1000.0

                else:
                    # There is no file queued, sleep until the next full build
                    timeToSleep = 1.1 * float(minFullIntervalTime) / 1000.0
                    logger.debug("run() - No file queued, sleep for %.2f seconds" % timeToSleep)

            # Sleep in small intervals so that we can capture incoming commands
            for i in range(int(math.ceil(timeToSleep))):
                time.sleep(1)
                # Break if there is a command to be processed
                if self.pyLFTPInst.hasIncomingCommand:
                    self.pyLFTPInst.hasIncomingCommand = False
                    break

    def __del__(self):
        logger.info("pyLFTPdaemon stopping")
        self.pyLFTPInst.killLFTPProcess()


class pyLFTP():
    def __init__(self):
        # Config variables
        self.config = {}
        self.downloadPatterns = []
        self.configDirectoryPath = "%s/.pyLFTPdaemon" % homeDir
        self.uid = 0  # uid of user for executing LFTP under
        self.gid = 0  # gid of user for executing LFTP under

        # Local variables
        self.process = None
        self.remoteFileDatabase = []  # List of FileObjs
        self.remoteFileListCache = None  # Cache remote file info

        # Communication facilitators
        self.runtimeQueue = []  # Files queued via interface
        self.remoteFileDatabaseLock = threading.Lock()  # Lock on database
        self.hasIncomingCommand = False  # Is there a new command to be processed?
        self.forceLocalUpdate = False  # If command wants to force a local update

        # Watchdog variables
        self.watchdogLastFilesize = None
        self.watchdogLastFilename = None

    def __del__(self):
        self.killLFTPProcess()

    def killLFTPProcess(self):
        logger.debug("Running pkill lftp")
        import subprocess
        killProcess = subprocess.Popen("pkill -9 lftp", shell=True)
        killProcess.wait()

    def webLoadHook(self):
        """Called by webserver to grab data from daemon"""
        import copy
        self.remoteFileDatabaseLock.acquire()
        self.databaseCache = copy.deepcopy(self.remoteFileDatabase)
        self.remoteFileDatabaseLock.release()
        web.ctx.pipe = self.databaseCache
        web.ctx.pyLFTPInst = self

    def addRuntimeQueue(self, filename):
        """Used by webserver to add files to runtime queue"""
        if not filename in self.runtimeQueue:
            self.runtimeQueue.append(filename)
            logger.info("Added %s to runtime queue." % filename)
            self.hasIncomingCommand = True
            self.forceLocalUpdate = True
        logger.debug("runtimeQueue: " + str(self.runtimeQueue))

    def cleanRuntimeQueue(self, filename):
        """Called internally to remove file from runtime queue for clean up purposes"""
        if filename in self.runtimeQueue:
            self.runtimeQueue.remove(filename)
        logger.debug("runtimeQueue: " + str(self.runtimeQueue))

    def readConfig(self):
        """
           Read configuration from the file in ~/.pyLFTPdaemon/config
        """

        # Read config in
        logger.debug("Config path - %s" % self.configDirectoryPath)
        Config = ConfigParser.ConfigParser()
        Config.read("%s/config" % self.configDirectoryPath)
        for section in Config.sections():
            self.config[section] = {}
            for option in Config.options(section):
                self.config[section][option] = Config.get(section, option)

        # Parse download patterns        
        try:
            with open("%s/patterns" % self.configDirectoryPath) as f:
                self.downloadPatterns = [x.strip() for x in f.readlines()]
        except:
            pass

        # Get uid for localUsername
        self.uid = getpwnam(self.config["SSHConfig"]["localusername"]).pw_uid
        self.gid = getpwnam(self.config["SSHConfig"]["localusername"]).pw_gid
        logger.debug(
            "localusername: %s, uid: %d, gid: %d" % (self.config["SSHConfig"]["localusername"], self.uid, self.gid))

        logger.info("Read config")
        logger.debug("self.config: " + str(self.config))
        logger.debug("self.downloadPatterns: " + str(self.downloadPatterns))

    def __getRemoteFileList(self):
        """
           Returns a list of (filenames,filesize,isFile) tuples of all files/folders on server.
           Execute du command both with and without --apparent-size (-b) and take the smaller file size.
        """
        command = "ssh %s@%s 'cd %s; find * -maxdepth 0 | while read DIR; do find \"$DIR\" -type f -print0 | du -scB 1 --files0-from=- | tail -n 1 | sed \"s/total/$DIR/g\"; done' 2>/dev/null" % (
            self.config["SSHConfig"]["username"], self.config["SSHConfig"]["address"],
            self.config["SSHConfig"]["downloadfrompath"]
        )
        command2 = "ssh %s@%s 'cd %s; find * -maxdepth 0 | while read DIR; do find \"$DIR\" -type f -print0 | du -scb --files0-from=- | tail -n 1 | sed \"s/total/$DIR/g\"; done' 2>/dev/null" % (
            self.config["SSHConfig"]["username"], self.config["SSHConfig"]["address"],
            self.config["SSHConfig"]["downloadfrompath"]
        )
        commandIsfile = "ssh %s@%s 'cd %s; find * -maxdepth 0 -type f' 2>/dev/null" % (
            self.config["SSHConfig"]["username"], self.config["SSHConfig"]["address"],
            self.config["SSHConfig"]["downloadfrompath"]
        )
        lsOut, lsErr = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
        lsOut = lsOut.splitlines()
        logger.debug(command)
        logger.debug("__getRemoteFileList: command 1 done")
        lsOut2, lsErr2 = subprocess.Popen(command2, stdout=subprocess.PIPE, shell=True).communicate()
        lsOut2 = lsOut2.splitlines()
        logger.debug(command2)
        logger.debug("__getRemoteFileList: command 2 done")
        logger.debug(commandIsfile)
        lsOutIsfile, lsErrIsfile = subprocess.Popen(commandIsfile, stdout=subprocess.PIPE, shell=True).communicate()
        lsOutIsfile = lsOutIsfile.splitlines()
        logger.debug("__getRemoteFileList: command 3 done")

        files = []  # list of (filename, filesize) tuples

        if len(lsOut) != len(lsOut2):
            logger.error(
                "__getRemoteFileList: Output of similar du commands returned different outputs. lsOut: %d, lsOut2: %d" % (
                len(lsOut), len(lsOut2)))
            logger.error(command)
            logger.error(command2)
            logger.error(lsOut)
            logger.error(lsOut2)
        else:
            import re
            for i, line in enumerate(lsOut):
                matchObj = re.search(r'(\d+)\s+(.*)', lsOut[i].rstrip())
                matchObj2 = re.search(r'(\d+)\s+(.*)', lsOut2[i].rstrip())
                if matchObj.group(2) != matchObj2.group(2):
                    logger.error("__getRemoteFileList: file names do not match: %s vs %s" % (
                    matchObj.group(2), matchObj2.group(2)))
                    continue
                fileName = matchObj.group(2)
                fileSize = min(int(matchObj.group(1)), int(matchObj2.group(1)))
                isFile = fileName in lsOutIsfile
                files.append((fileName, fileSize, isFile))

        logger.debug(files)
        return files

    def __getLocalFileList(self):
        """
           Returns a list of (filenames,filesize) tuples of all files/folders on local machine.
           Execute du command both with and without --apparent-size (-b) and take the smaller file size.
        """
        command = "cd %s; find * -maxdepth 0 | while read DIR; do find \"$DIR\" -type f -print0 | du -scB 1 --files0-from=- | tail -n 1 | sed \"s/total/$DIR/g\"; done" % \
                  self.config["SSHConfig"]["downloadtopath"]
        command2 = "cd %s; find * -maxdepth 0 | while read DIR; do find \"$DIR\" -type f -print0 | du -scb --files0-from=- | tail -n 1 | sed \"s/total/$DIR/g\"; done" % \
                   self.config["SSHConfig"]["downloadtopath"]
        lsOut, lsErr = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
        lsOut = lsOut.splitlines()
        lsOut2, lsErr2 = subprocess.Popen(command2, stdout=subprocess.PIPE, shell=True).communicate()
        lsOut2 = lsOut2.splitlines()

        files = []  # list of (filename, filesize) tuples

        if len(lsOut) != len(lsOut2):
            logger.error(
                "__getLocalFileList: Output of similar du commands returned different outputs. lsOut: %d, lsOut2: %d" % (
                len(lsOut), len(lsOut2)))
            logger.error(command)
            logger.error(command2)
            logger.error(lsOut)
            logger.error(lsOut2)
        else:
            import re
            for i, line in enumerate(lsOut):
                matchObj = re.search(r'(\d+)\s+(.*)', lsOut[i].rstrip())
                matchObj2 = re.search(r'(\d+)\s+(.*)', lsOut2[i].rstrip())
                if matchObj.group(2) != matchObj2.group(2):
                    logger.error("__getLocalFileList: file names do not match: %s vs %s" % (
                    matchObj.group(2), matchObj2.group(2)))
                    continue
                fileName = matchObj.group(2)
                fileSize = min(int(matchObj.group(1)), int(matchObj2.group(1)))
                fileName = matchObj.group(2)
                files.append((fileName, fileSize))

        return files

    def __getLocalFileSize(self, filename):
        """
           Returns a filesize of given file/folder on local machine.
           Execute du command both with and without --apparent-size (-b) and take the smaller file size.
        """
        command = "cd %s; find \"%s\" -type f -print0 | du -scB 1 --files0-from=- | tail -n 1 | sed \"s/total/%s/g\"" % (
            self.config["SSHConfig"]["downloadtopath"], filename, filename)
        command2 = "cd %s; find \"%s\" -type f -print0 | du -scb --files0-from=- | tail -n 1 | sed \"s/total/%s/g\"" % (
            self.config["SSHConfig"]["downloadtopath"], filename, filename)
        lsOut, lsErr = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
        lsOut2, lsErr2 = subprocess.Popen(command2, stdout=subprocess.PIPE, shell=True).communicate()

        import re
        matchObj = re.search(r'(\d+)\s+(%s)' % filename, lsOut.rstrip())
        matchObj2 = re.search(r'(\d+)\s+(%s)' % filename, lsOut2.rstrip())
        if matchObj and matchObj.group(1):
            return min(int(matchObj.group(1)), int(matchObj2.group(1)))
        else:
            return 0

    def __getDownloadingFile(self, database=None):
        databaseToSearch = None
        if database:
            databaseToSearch = database
        else:
            databaseToSearch = self.remoteFileDatabase
        downloadingFiles = [v for i, v in enumerate(databaseToSearch) if v.status == FileState.downloading]
        if downloadingFiles:
            return downloadingFiles[0]
        else:
            return None

    def isFileQueued(self):
        return any([v for i, v in enumerate(self.remoteFileDatabase) if v.status == FileState.queued])

    def isFileDownloading(self):
        return any([v for i, v in enumerate(self.remoteFileDatabase) if v.status == FileState.downloading])

    def isProcessOngoing(self):
        return self.process is not None and self.process.poll() is None

    def startQueuedDownload(self):
        # Find next queued file to download
        for file in self.remoteFileDatabase:
            if file.status == FileState.queued:
                self.__startDownload(file.filename, file.remoteSize, file.isFile)
                break

    def watchdog(self):
        """Kill LFTP service if downloading has stalled"""
        downloadingFile = self.__getDownloadingFile()
        if downloadingFile:
            if self.watchdogLastFilename == downloadingFile.filename and self.watchdogLastFilesize == downloadingFile.localSize:
                logger.info("Stalled download '%s' detected. Killing LFTP." % downloadingFile.filename)
                self.killLFTPProcess()
                self.watchdogLastFilename = None
                self.watchdogLastFilesize = None
            else:
                logger.debug("Watchdog - file: %s, size: %d" % (downloadingFile.filename, downloadingFile.localSize))
                self.watchdogLastFilename = downloadingFile.filename
                self.watchdogLastFilesize = downloadingFile.localSize
        else:
            self.watchdogLastFilename = None
            self.watchdogLastFilesize = None

    # Use this pre-function to set correct file permissions
    def __my_preexec_fn(self):
        os.setegid(self.gid)
        os.setuid(self.uid)

    def __startDownload(self, filename, filesize, isFile):
        if self.process is not None and self.process.poll() is None:
            logger.error("startDownload: previous process is not yet finished!")

        command = ""
        if isFile:
            command = '/usr/bin/lftp -u %s,pass sftp://%s -e "pget -c -n %s \\\"%s/%s\\\" -o %s/; exit" ' % \
                      (self.config["SSHConfig"]["username"], self.config["SSHConfig"]["address"],
                       self.config["LFTPConfig"]["use_pget_n"],
                       self.config["SSHConfig"]["downloadfrompath"], filename,
                       self.config["SSHConfig"]["downloadtopath"] + "/")
        else:
            command = '/usr/bin/lftp -u %s,pass sftp://%s -e "mirror -c --parallel=%s --use-pget-n=%s \\\"%s/%s\\\" %s; exit" ' % \
                      (self.config["SSHConfig"]["username"], self.config["SSHConfig"]["address"],
                       self.config["LFTPConfig"]["parallel"], self.config["LFTPConfig"]["use_pget_n"],
                       self.config["SSHConfig"]["downloadfrompath"], filename,
                       self.config["SSHConfig"]["downloadtopath"] + "/")

        # Run command
        logger.debug("Command: " + command)
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                        preexec_fn=self.__my_preexec_fn)
        self.process.lastFile = filename

        # Create a thread for callback on process exit
        # This function will create a dummy file when the download is done.
        # This is so if the downloaded file is later deleted, it is not redownloaded.
        def processOnExit(process, configDirectoryPath, filename, filesize):
            process.wait()
            localFilesize = self.__getLocalFileSize(filename)
            import string
            import re
            fullLFTPOutput = self.process.stdout.read().translate(string.maketrans("\r", " "))  # Remove delete lines
            match = re.search('(Total(.|\n)*)', fullLFTPOutput, re.MULTILINE)
            if match and match.group(0):
                logger.debug("LFTP output: " + match.group(0))
            if localFilesize >= filesize:
                command = "touch %s/_%s" % (configDirectoryPath, filename.replace(' ', '\ '))
                createFileProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                     shell=True, preexec_fn=self.__my_preexec_fn)
                createFileProcess.wait()
                logger.info("Finished downloading %s" % filename)
                self.cleanRuntimeQueue(filename)
            return

        thread = threading.Thread(target=processOnExit,
                                  args=(self.process, self.configDirectoryPath, filename, filesize))
        thread.start()

        logger.info("Started downloading %s (%d bytes)" % (filename, filesize))

    """
    def __getDownloadStatus(self):
        if self.process is None or self.process.poll() is not None:
            return None
        else:
            line = self.process.stdout.readline()
            return line
    """

    def buildRemoteFileDatabase(self, buildType=BuildType.full):
        """
           Build remote file information from scratch
        """

        if buildType == BuildType.full:
            logger.info("buildRemoteFileData - buildType=" + buildType)
        elif debugMode:
            logger.debug("buildRemoteFileData - buildType=" + buildType)

        if buildType == BuildType.downloading:
            # downloading - only update the downloading file
            downloadingFile = self.__getDownloadingFile()
            if downloadingFile:
                downloadingFile.prevLocalSize = downloadingFile.localSize
                downloadingFile.prevUpdateTime = downloadingFile.updateTime
                downloadingFile.localSize = self.__getLocalFileSize(downloadingFile.filename)
                downloadingFile.updateTime = time.time()

        else:
            # full or local - rebuild the file database

            # Reset the file database, save backup in a temporary copy to access previous data
            prevRemoteFileDatabase = self.remoteFileDatabase
            newRemoteFileDatabase = []

            # Get list of remote files
            if buildType == BuildType.full or not self.remoteFileListCache:
                # full - get the remote file list from server
                self.remoteFileListCache = self.__getRemoteFileList()
            else:
                # local - use remote file list cache
                pass

            remoteFiles = self.remoteFileListCache

            # Get list of local files
            localFiles = self.__getLocalFileList()

            # Keep track of currently downloading files
            downloadingFileName = None
            if self.process is not None and self.process.poll() is None:
                downloadingFileName = self.process.lastFile

            for (filename, filesize, isFile) in remoteFiles:
                # Assume file is a no_match            
                file = FileObj(filename, int(filesize), FileState.no_match, 0, time.time(), isFile)

                # Check if file is a match (and hence queued):
                #    1. if it's in the patterns file
                #    2. if it's in the runtime queue
                import re
                if any(re.match(r'%s' % pattern, filename) and pattern != '' for pattern in self.downloadPatterns) \
                        or filename in self.runtimeQueue:
                    file.status = FileState.queued

                # If local file exists, check if it's partially downloaded
                localFilesize = [v[1] for i, v in enumerate(localFiles) if v[0] == filename]
                if localFilesize:
                    file.localSize = int(localFilesize[0])
                    if file.localSize == file.remoteSize:
                        # If local file exists and has full size, then it's downloaded
                        file.status = FileState.downloaded
                    elif file.localSize > file.remoteSize and os.path.isfile(
                                    "%s/_%s" % (self.configDirectoryPath, filename)):
                        # Local file size greater and dummy file exists, then it's downloaded
                        file.status = FileState.downloaded
                elif os.path.isfile("%s/_%s" % (self.configDirectoryPath, filename)):
                    # if no local file but dummy file exists, then file was downloaded but deleted
                    file.status = FileState.deleted

                # Check if file is downloading
                # Copy the previous update information for downloading file
                if downloadingFileName == filename:
                    file.status = FileState.downloading
                    prevDownloadingFile = self.__getDownloadingFile(prevRemoteFileDatabase)
                    if prevDownloadingFile and prevDownloadingFile.filename == filename:
                        file.prevLocalSize = prevDownloadingFile.localSize
                        file.prevUpdateTime = prevDownloadingFile.updateTime

                newRemoteFileDatabase.append(file)

            self.remoteFileDatabaseLock.acquire()
            self.remoteFileDatabase = newRemoteFileDatabase
            self.remoteFileDatabaseLock.release()

    def printFileData(self, status=None):
        for file in self.remoteFileDatabase:
            doPrint = True
            if status is not None and status != file.status and file.status not in status:
                doPrint = False
            if doPrint:
                logger.info("%s\t%d\t%s\t%d" % (file.filename, file.remoteSize, file.status, file.localSize))


class FileObj():
    def __init__(self, filename, remoteSize, status, localSize, time, isFile):
        self.filename = filename  # File/folder name
        self.remoteSize = remoteSize  # Size on remote server
        self.status = status  # Status (downloading, downloaded, queued, deleted, no_match)
        self.localSize = localSize  # Size on local machine
        self.updateTime = time  # Time of latest update
        self.isFile = isFile
        self.prevUpdateTime = None  # Time of previous update
        self.prevLocalSize = None  # localSize at previous update

    def getSpeed(self):
        if self.updateTime is not None and self.prevUpdateTime is not None:
            return (self.localSize - self.prevLocalSize) / (self.updateTime - self.prevUpdateTime)
        else:
            return 0.0


def shellquote(s):
    """
    Use to pass file names to shell to preserve spaces and other shell meta characters
    :param s:
    :return:
    """
    return "'" + s.replace("'", "'\\''") + "'"


if __name__ == "__main__":
    app = pyLFTPdaemon()
    logger = logging.getLogger("DaemonLog")
    if debugMode:
        logger.setLevel(logging.DEBUG)  # logging.DEBUG logging.INFO logging.WARNING
    else:
        logger.setLevel(logging.INFO)  # logging.DEBUG logging.INFO logging.WARNING

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    web.config.debug = False

    # Create logging directory if one doesn't exist
    if not os.path.exists("/var/log/%s" % appName):
        os.makedirs("/var/log/%s" % appName)

    # Create run directory if one doesn't exist
    if not os.path.exists("/var/run/%s" % appName):
        os.makedirs("/var/run/%s" % appName)

    handler = logging.FileHandler("/var/log/%s/%s.log" % (appName, appName))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    daemon_runner = runner.DaemonRunner(app)
    # This ensures that the logger file handle does not get closed during daemonization
    daemon_runner.daemon_context.files_preserve = [handler.stream]
    daemon_runner.do_action()

# For webserver - mod_wsgi will catch this instance of the wsgi application
app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()
