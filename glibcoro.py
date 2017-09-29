#+
# glibcoro -- An interface between asyncio and the GLib event loop.
#
# The goal of this project is to implement an interface to the GLib/GTK+
# event loop as a subclass of asyncio.AbstractEventLoop, taking full
# advantage of the coroutine feature available in Python 3.5 and later.
#-

import sys
import time
import types
import asyncio
import gi
from gi.repository import \
    GLib

# TODO: handle threading?

class GLibEventLoop(asyncio.AbstractEventLoop) :

    # <https://developer.gnome.org/glib/stable/glib-The-Main-Event-Loop.html>

    def __init__(self) :
        self._gloop = GLib.MainLoop()
        self._closed = False
    #end __init__

    def run_forever(self) :
        self._check_closed()
        self._gloop.run()
    #end run_forever

    def run_until_complete(self, future) :

        async def awaitit() :
            await future
            self.stop()
        #end awaitit

    #begin run_until_complete
        self._check_closed()
        self.create_task(awaitit())
        self.run_forever()
    #end run_until_complete

    def stop(self) :
        self._gloop.quit()
    #end stop

    def is_running(self) :
        return \
            self._gloop.is_running()
    #end is_running

    def _check_closed(self) :
        if self._closed :
            raise asyncio.InvalidStateError("event loop is closed")
        #end if
    #end _check_closed

    def is_closed(self) :
        return \
            self._closed
    #end is_closed

    def close(self) :
        if self.is_running() :
            raise asyncio.InvalidStateError("event loop cannot be closed while running")
        #end if
        self._closed = True
    #end close

    def _timer_handle_cancelled(self, handle) :
        # called from asyncio.TimerHandle.cancel()
        # sys.stderr.write("cancelling timer %s\n" % (repr(handle,))) # debug
        pass # I don’t really have anything to do
    #end _timer_handle_cancelled

    def call_exception_handler(self, context) :
        # TBD
        sys.stderr.write("call_exception_handler: %s\n " % repr(context))
    #end call_exception_handler

    # TODO: shutdown_asyncgens?

    def call_soon(self, callback, *args) :

        def doit(hdl) :
            if not hdl._cancelled :
                hdl._run()
            #end if
            return \
                False # always one-shot
        #end doit

    #begin call_soon
        self._check_closed()
        hdl = asyncio.Handle(callback, args, self)
        GLib.idle_add(doit, hdl)
        return \
            hdl
    #end call_soon

    def _call_timed_common(self, when, callback, args) :

        def doit(hdl) :
            exc = None
            result = None
            if False :
                try :
                    result = callback(*args)
                except Exception as excp :
                    exc = excp
                #end try
            else :
                if not hdl._cancelled :
                    hdl._run()
                #end if
            #end if
            return \
                False # always one-shot
        #end doit

    #begin _call_timed_common
        hdl = asyncio.TimerHandle(when, callback, args, self)
        GLib.timeout_add(max(round((when - self.time()) * 1000), 0), doit, hdl)
        return \
            hdl
    #end _call_timed_common

    def call_later(self, delay, callback, *args) :
        self._check_closed()
        return \
            self._call_timed_common(delay + self.time(), callback, args)
    #end call_later

    def call_at(self, when, callback, *args) :
        self._check_closed()
        return \
            self._call_timed_common(when, callback, args)
    #end call_at

    def time(self) :
        # might as well do same thing as asyncio.BaseEventLoop
        return \
            time.monotonic()
    #end time

    def create_future(self) :
        return \
            asyncio.Future(loop = self)
    #end create_future

    def create_task(self, coro) :
        self._check_closed()
        return \
            asyncio.Task(coro)
              # will call my call_soon routine to schedule itself
    #end create_task

    # TODO: threads, executor, network, pipes and subprocesses
    # TODO: readers, writers, sockets, signals
    # TODO: task factory, exception handlers, debug flag

    def get_debug(self) :
        return \
            False
    #end get_debug

#end GLibEventLoop

_running_loop = None

class GLibEventLoopPolicy(asyncio.AbstractEventLoopPolicy) :

    def get_event_loop(self) :
        global _running_loop
        if _running_loop == None :
            _running_loop = self.new_event_loop()
        #end if
        return \
            _running_loop
    #end get_event_loop

    def set_event_loop(self, loop) :
        if not isinstance(loop, GLibEventLoop) :
            raise TypeError("loop must be a GLibEventLoop")
        #end if
        _running_loop = loop
    #end set_event_loop

    def new_event_loop(self) :
        return \
            GLibEventLoop()
    #end new_event_loop

    # TODO: get/set_child_watcher

#end GLibEventLoopPolicy

def install() :
    "installs this module as the default purveyor of asyncio event loops."
    asyncio.set_event_loop_policy(GLibEventLoopPolicy())
#end install
