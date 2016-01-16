#
# VUsbTools.Log
# Micah Elizabeth Scott <micah@vmware.com>
#
# Implements parsers for USB log files. Currently
# this includes slurping usbAnalyzer data out of the
# VMX log, and parsing the XML logs exported by
# Ellisys Visual USB.
#
# Copyright (C) 2005-2010 VMware, Inc. Licensed under the MIT
# License, please see the README.txt. All rights reserved.
#

from __future__ import division
import sys, time, re, os, string, atexit
import xml.sax, Queue, threading, difflib
import gtk, gobject
import traceback, gzip, struct
from VUsbTools import Types


class Follower(threading.Thread):
    """A thread that continuously scans a file, parsing each line"""
    pollInterval = 0.1
    running = True
    progressInterval = 0.2
    progressExpiration = 0

    def __init__(self, filename, parser, progressQueue=None, tailMode=False):
        self.filename = filename
        self.parser = parser
        self.progressQueue = progressQueue

        if os.path.splitext(filename)[1] == ".gz":
            # On a gzip file, we need to read the uncompressed filesize from the footer
            f = open(filename, "rb")
            f.seek(-4, 2)
            self.fileSize = struct.unpack("<l", f.read(4))[0]
            f.seek(0)
            self.file = gzip.GzipFile(fileobj=f)
        else:
            self.file = open(filename)
            self.fileSize = os.fstat(self.file.fileno()).st_size

        if tailMode:
            # Start at the end
            self.file.seek(0, 2)

        threading.Thread.__init__(self)
        atexit.register(self.stop)

    def run(self):
        try:
            while self.running:
                if self.parser.lineOriented:
                    line = self.file.readline()
                else:
                    line = self.file.read(16384)
                if line:
                    self.parser.parse(line)

                    # Compute our progress only every progressInterval seconds
                    now = time.clock()
                    if now >= self.progressExpiration:
                        self.setProgress(min(1.0, self.file.tell() / self.fileSize))
                        self.progressExpiration = now + self.progressInterval
                else:
                    self.setProgress(1.0)
                    time.sleep(self.pollInterval)
        except KeyboardInterrupt:
            gtk.main_quit()

    def setProgress(self, progress):
        if self.progressQueue:
            self.progressQueue.put(("Loading %s" % os.path.basename(self.filename),
                                    progress))

    def stop(self):
        # Keep the queue empty so it doesn't deadlock on put()
        if not self.running:
            return
        self.running = False
        try:
            while 1:
                self.parser.eventQueue.get(False)
        except Queue.Empty:
            pass
        self.join()


class QueueSink:
    """Polls a Queue for new items, via the Glib main loop.
       When they're available, calls a callback with them.
       """
    interval = 200
    timeSlice = 0.25
    maxsize = 512
    batch = range(10)

    def __init__(self, callback):
        self.eventQueue = Queue.Queue(self.maxsize)
        self.callback = callback
        self.poll()

    def poll(self):
        try:
            deadline = time.clock() + self.timeSlice
            while time.clock() < deadline:
                # This avoids calling time.clock() once per queue item.
                for _ in self.batch:
                    try:
                        event = self.eventQueue.get(False)
                    except Queue.Empty:
                        # We have nothing to do, set a longer interval
                        gobject.timeout_add(self.interval, self.poll)
                        return False
                    else:
                        self.callback(event)

        except KeyboardInterrupt:
            gtk.main_quit()

        # Come back after GTK's event queue is idle
        gobject.idle_add(self.poll)
        return False



