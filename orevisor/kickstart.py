#!/usr/bin/python
#
# Copyright 2016 Openwrt x86_64 Unity Project
#
# Wei Yongjun <weiyj.lk@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion

class RevisorKickstart:
    def __init__(self, cfg=None):
        self.cfg = cfg

    def create_parser(self):
        self.handler = makeVersion()
        self.parser = KickstartParser(self.handler)

    def read_file(self, url):
        if not hasattr(self, "parser"):
            self.create_parser()
        self.parser.readKickstart(url)

    def _reset(self):
        self.parser._reset()

    def __str__(self):
        return "%s" % self.handler.__str__()

    def _get(self, item=None, val=None):
        if not item == None:
            if hasattr(self.handler, item):
                if not val is None:
                    if hasattr(getattr(self.handler, item), val):
                        return getattr(getattr(self.handler, item), val)
                    elif isinstance(getattr(self.handler, item), dict):
                        return getattr(self.handler, item)[val]
                    else:
                        return None
                else:
                    return getattr(self.handler, item)
            elif hasattr(self.handler, val):
                return getattr(self.handler, val)
        else:
            return self.handler

