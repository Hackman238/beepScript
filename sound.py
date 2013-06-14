#! /usr/bin/env python
import os, time, thread
import glib, gobject
import pygst
pygst.require("0.10")
import gst
import __main__

class playSound:
    def __init__(self, sounduri, loop = None):
        self.sounduri = sounduri
        self.loop = loop
        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.playmode = False
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.playmode = False

    def start(self):
        self.playmode = True

        self.player.set_property("uri", self.sounduri)
        self.player.set_state(gst.STATE_PLAYING)
        while self.playmode:
            time.sleep(0.5)

        time.sleep(0.5)
        self.loop.quit()
