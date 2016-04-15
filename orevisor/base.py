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

import logging

from orevisor.cli import RevisorCLI
from orevisor.logger import RevisorLogger
from orevisor.translate import _

class RevisorBase:
    def __init__(self, revisor):
        self.parser = revisor.parser
        
        self.options = revisor.options

        self.create_logger()

    def create_logger(self):
        if not self.options.debuglevel == None:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO
            self.options.debuglevel = 0

        # Initialize logger
        self.log = RevisorLogger(loglevel=loglevel, debuglevel=self.options.debuglevel, logfile=self.options.logfile)

    def run(self):
        self.log.debug(_("Running Revisor..."))
        self.cli = RevisorCLI(self)
        self.cli.run()
