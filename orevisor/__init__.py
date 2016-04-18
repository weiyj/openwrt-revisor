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

import os
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

        ##
        ## Configuration Options
        ##
        config_group = self.parser.add_option_group(_("Configuration Options"))
        config_group.add_option("--kickstart",
                                dest    = "kickstart_file",
                                action  = "store",
                                default = "conf/conf.d/openwrt.conf",
                                help    = _("Use kickstart file"),
                                metavar = "[kickstart file]")
        config_group.add_option("-c", "--config",
                                dest    = "config",
                                action  = "store",
                                default = "conf/orevisor.conf",
                                help    = _("Revisor configuration file to use"),
                                metavar = "[config file]")

        config_group.add_option("--destination-directory",
                                dest    = "destination_directory",
                                action  = "store",
                                default = "/tmp/revisor/",
                                help    = _("Destination directory for products"),
                                metavar = "[directory]")

        config_group.add_option("--working-directory",
                                dest    = "working_directory",
                                action  = "store",
                                default = "/var/tmp/",
                                help    = _("Working directory"),
                                metavar = "[directory]")

        config_group.add_option("--model",
                                dest    = "model",
                                action  = "store",
                                default = "Openwrt",
                                help    = _("Model to use for composing"),
                                metavar = "[model]")

        config_group.add_option("--openwrt-directory",
                                dest    = "openwrt_directory",
                                action  = "store",
                                default = "/pub/scm/openwrt/",
                                help    = _("Openwrt directory"),
                                metavar = "[directory]")

        ##
        ## Installation Media Options
        ##
        install_group = self.parser.add_option_group(_("Installation Media Options"))

        install_group.add_option("--product-name",
                                 dest    = "product_name",
                                 action  = "store",
                                 default = "Openwrt",
                                 help    = _("Product Name"))

        install_group.add_option("--product-path",
                                 dest    = "product_path",
                                 action  = "store",
                                 default = "Packages",
                                 help    = _("Product Path (e.g. Packages)"))

        install_group.add_option("--iso-label",
                                 dest    = "iso_label",
                                 action  = "store",
                                 default = "Openwrt",
                                 help    = _("ISO Label Base. Note that other things are appended but that the length can be 32 chars maximum."))

        install_group.add_option("--iso-basename",
                                 dest    = "iso_basename",
                                 action  = "store",
                                 default = "Openwrt",
                                 help    = _("The base name for the ISOs"))

        install_group.add_option("--product-version",
                                 dest    = "version",
                                 action  = "store",
                                 default = "8",
                                 help    = _("Product Version"))

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
