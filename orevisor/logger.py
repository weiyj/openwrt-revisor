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

import sys
import logging

class RevisorLogger:
    def __init__(self, loglevel=logging.INFO, debuglevel=0, logfile="/var/log/revisor.log"):
        self.loglevel = loglevel
        self.debuglevel = debuglevel

        plaintextformatter = logging.Formatter("%(message)s")

        console_stdout = logging.StreamHandler(sys.stdout)
        console_stdout.setFormatter(plaintextformatter)

        filelog_handler = logging.FileHandler(filename=logfile)
        filelog_handler.setFormatter(plaintextformatter)

        self.log = logging.getLogger()
        self.log.addHandler(console_stdout)
        self.log.addHandler(filelog_handler)

        self.log.setLevel(self.loglevel)

    def info(self, msg):
        self.log.info(msg)

    def debug(self, msg, level=1):
        if level <= self.debuglevel:
            self.log.debug(msg)

    def error(self, msg, recoverable=True):
        self.log.error(msg)

    def warning(self, msg):
        self.log.warning(msg)
