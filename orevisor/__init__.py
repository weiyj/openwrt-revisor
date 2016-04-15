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
import traceback

from optparse import OptionParser

from orevisor.base import RevisorBase
from orevisor.translate import _

class Revisor:
    def __init__(self):
        self.args = None
        self.parser = None
        self.options = None

        self.parse_options()

        self.base = RevisorBase(self)

    def parse_options(self):
        self.parser = OptionParser()

        runtime_group = self.parser.add_option_group(_("Runtime Options"))

        ##
        ## Logging Options
        ##
        runtime_group.add_option("-d", "--debug",
                                 dest    = "debuglevel",
                                 default = 0,
                                 type    = 'int',
                                 help    = _("Set debugging level (0 by default)"))

        runtime_group.add_option("--logfile",
                                 dest    = "logfile",
                                 default = "/var/log/revisor.log",
                                 help    = _("Use a different logfile"))

        (self.options, self.args) = self.parser.parse_args()

    def run(self):
        exitcode = 0

        try:
            self.base.run()
        except SystemExit, e:
            exitcode = e
        except KeyboardInterrupt:
            exitcode = 1
            self.base.log.info(_("Interrupted by user"))
        except:
            exitcode = 2
            traceback.print_exc()

        sys.exit(exitcode)
