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

from orevisor.logger import RevisorLogger
from orevisor.cfg import RevisorConfig
from orevisor.pungi import RevisorPungi
from orevisor.translate import _

class RevisorBase:
    def __init__(self, revisor):
        self.parser = revisor.parser
        
        self.options = revisor.options

        self.packages = {}
        self.dependencies = []

        self.create_logger()
        
        self.create_config()

        self.cfg.setup_cfg()

        self.cfg.setup_opkg()

        self.cfg.setup_ks()

    def create_logger(self):
        if not self.options.debuglevel == None:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO
            self.options.debuglevel = 0

        # Initialize logger
        self.log = RevisorLogger(loglevel=loglevel, debuglevel=self.options.debuglevel, logfile=self.options.logfile)

    def create_config(self):
        self.cfg = RevisorConfig(self)

    def run(self):
        self.log.debug(_("Running Revisor..."))
        
        self.cfg.load_kickstart(self.cfg.kickstart_file)

        if not self.cfg.check_working_directory():
            sys.exit(1)

        self.cfg.check_destination_directory()
        
        self.lift_off()

    def check_opkg_info(self, package):
        self.packages[package] = self.cfg.opkg_info(package)
        if 'depends' in self.packages[package]:
            for dep in self.packages[package]['depends']:
                dep = dep.split(' ')[0]
                if dep in self.packages:
                    continue
                self.check_opkg_info(dep)
                self.dependencies.append(dep)

    def check_dependencies(self, groupList, packageList, excludedList = None):
        for package in packageList:
            self.check_opkg_info(package)
        
        errorExit = False
        for package in self.packages:
            if not 'name' in self.packages[package]:
                errorExit = True
                self.log.error("Package %s is missing" % package)
        
        if errorExit is True:
            sys.exit(1)

    def report_packages_stat(self):
        totalSize = 0
        for package in self.packages:
            totalSize = totalSize + int(self.packages[package]['size'])

        self.log.info("Total %d packages, download size %d" % (len(self.packages), totalSize))

    def download_packages(self):
        self.log.info("Downloading packages...")
        self.cfg.execute_shell("/bin/cp -rf %s %s" % (self.cfg.openwrt_packages, self.cfg.install_directory))

    def install_packages(self, packageList):
        self.log.info("Installing packages...")
        self.cfg.opkg_install(packageList, self.packages)
        
    def lift_off(self):
        groupList = self.cfg.get_item("packages", "groupList")
        packageList = self.cfg.get_item("packages", "packageList")
        excludedList = self.cfg.get_item("packages","excludedList")

        self.check_dependencies(groupList, packageList, excludedList)
        self.report_packages_stat()
        self.download_packages()
        self.install_packages(packageList)

        self.buildInstallationMedia()

    def buildInstallationMedia(self):
        mypungi = RevisorPungi(self)

        mypungi.buildIsolinux()
        mypungi.doCreateIso(mediatype='unified')

    
