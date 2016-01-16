#
# VUsbTools.Views
# Micah Elizabeth Scott <micah@vmware.com>
#
# A container for color and font preferences
#
# Copyright (C) 2005-2010 VMware, Inc. Licensed under the MIT
# License, please see the README.txt. All rights reserved.
#

import math

# Not sure the psyobj reference is needed. Included the fallback code for now.
psyobj = object
psycoBind = lambda _: None

# Moved from Types.
class Color(psyobj):
    """A simple color abstraction, supports linear interpolation.
       We store individual rgba values, as well as a 32-bit packed
       RGBA representation and an html/gdk-style string.
       """
    def __init__(self, r, g, b, a=0xFF):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

        self.gdkString = "#%02X%02X%02X" % (int(self.r + 0.5),
                                            int(self.g + 0.5),
                                            int(self.b + 0.5))

        self.rgba = ((int(self.r + 0.5) << 24) |
                     (int(self.g + 0.5) << 16) |
                     (int(self.b + 0.5) << 8) |
                     int(self.a + 0.5))

    def lerp(self, a, other):
        """For a=0, returns a copy of 'self'. For a=1, returns
           a copy of 'other'. Other values return a new interpolated
           color. Values are clamped to [0,1], so this will not
           extrapolate new colors.
           """
        a = min(1, max(0, a))
        b = 1.0 - a
        return self.__class__(self.r * b + other.r * a,
                              self.g * b + other.g * a,
                              self.b * b + other.b * a)


#
# Use the default monospace font.  If this is too large/small for your
# tastes, you can try a specific font name and size like "courier 9".
#
monospaceFont = "monospace"

def toMonospaceMarkup(text):
    """Convert arbitrary text to pango markup in our monospace font"""
    return '<span font_desc="%s">%s</span>' % (
        monospaceFont,
        text.replace("&", "&amp;").replace("<", "&lt;"))

directionColors = {
    "Up":   Color(0x00, 0x00, 0xFF),
    "Down": Color(0x00, 0x80, 0x00),
    }

directionIcons = {
    "Down": "gtk-go-forward",
    "Up":   "gtk-go-back",
    }

errorMarkerColor = Color(0xFF, 0x00, 0x00, 0x80)
diffMarkerColor = Color(0x00, 0xA0, 0x00, 0x30)
diffBorderColor = Color(0x00, 0xA0, 0x00, 0xA0)
emptyTransactionColor = Color(0x80, 0x80, 0x80)
smallTransactionColor = Color(0x80, 0x80, 0xFF)
largeTransactionColor = Color(0xFF, 0xFF, 0x80)
frameMarkerColor = Color(0x00, 0x00, 0xFF)
duplicateFrameColor = Color(0x80, 0x00, 0x00)

def getBarColor(transaction):
    """Get the color to use for a transaction's bar on the timing diagram.
    This implementation bases the color on a transaction's size.
    """
    s = transaction.datalen or 0
    if not s:
        return emptyTransactionColor

    # For non-empty transactions, the color is actually proportional
    # to size on a logarithmic scale.
    return smallTransactionColor.lerp(
        math.log(s) / math.log(4096), largeTransactionColor)
