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
import re
import subprocess

from ConfigParser import SafeConfigParser

from orevisor.kickstart import RevisorKickstart
from orevisor.translate import _

class RevisorConfig:
    def __init__(self, base):
        self.log = base.log
        self.options = base.options
        self.parser = base.parser

        self.defaults = Defaults()

        self.set_defaults_from_options()

        for option in self.defaults.__dict__.keys():
            setattr(self,option, self.defaults.__dict__[option])

        self.runtime = Runtime(self.defaults)

        for option in self.runtime.__dict__.keys():
            self.log.debug(_("Setting %s to %r") % (option, self.runtime.__dict__[option]), level=9)
            setattr(self, option, self.runtime.__dict__[option])

    def setup_cfg(self):
        self.options_set_from_config()

        self.options_set_from_commandline()

    def set_defaults_from_options(self):
        for long_opt in self.parser.__dict__['_long_opt'].keys():
            if long_opt == "--help":
                continue
            setattr(self.defaults, self.parser._long_opt[long_opt].dest, self.parser._long_opt[long_opt].default)

    def check_working_directory(self):
        self.log.debug(_("Checking working directories"))
        
        self.install_directory = "%s/revisor-install/%s/%s/%s/os" % (self.working_directory, self.version, self.model, self.architecture)

        complain = False
        if os.access(os.path.join(self.working_directory,"revisor-install"), os.R_OK):
            complain = True
        if os.access(os.path.join(self.working_directory,"revisor"), os.R_OK):
            complain = True
        if os.access(os.path.join(self.working_directory,"revisor-rundir"), os.R_OK):
            complain = True
        if os.access(self.install_directory, os.R_OK):
            complain = True

        if complain:
            self.log.debug(_("The directories Revisor uses in %s already exist. Revisor deleted them." % self.working_directory))

        if not os.access(os.path.join(self.working_directory, "revisor-install", "tmp"), os.R_OK):
            os.makedirs(os.path.join(self.working_directory, "revisor-install", "tmp"))

        if not os.access(self.install_directory, os.R_OK):
            os.makedirs(self.install_directory)

        return True

    def execute_shell(self, args):
        if isinstance(args, basestring):
            self.log.debug(args)
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
        else:
            self.log.debug(' '.join(args))
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
        shellOut = shelllog.communicate()[0]
    
        lines = shellOut.split("\n")
        lines = lines[0:-1]

        return lines

    def check_destination_directory(self):
        self.log.debug(_("Checking destination directories"))

        self.log.debug(_("Set destination directory to %s") % self.destination_directory)

        #if os.access(self.destination_directory, os.R_OK):

    def check_openwrt_directory(self):
        self.log.debug(_("Checking openwrt build directory %s") % self.openwrt_directory)

        if os.access(os.path.join(self.openwrt_directory, "packages"), os.R_OK):
            packages = os.path.join(self.openwrt_directory, "packages")
            self.openwrt_packages = packages
            self.log.debug(_("Openwrt imagebuilder directory %s exists") % packages)
        elif os.access(os.path.join(self.openwrt_directory, "bin" , "x86", "packages"), os.R_OK):
            packages = os.path.join(self.openwrt_directory, "bin" , "x86", "packages")
            self.openwrt_packages = packages
            self.log.debug(_("Openwrt build directory %s exists") % packages)

        staging_dir = os.path.join(self.openwrt_directory, "staging_dir")
        if not os.access(staging_dir, os.R_OK):
            self.log.error(_("Openwrt staging directory %s not readable") % staging_dir)
            return False

        binopkg = os.path.join(staging_dir, "host", "bin", "opkg")
        if not os.access(binopkg, os.R_OK):
            self.log.error(_("Openwrt opkg binary %s not readable") % staging_dir)
            return False

        ipkgtmp = os.path.join(self.working_directory, "openwrt", "tmp", "ipkgtmp")
        if not os.path.exists(ipkgtmp):
            self.log.debug(_("Create directory %s") % ipkgtmp)
            os.makedirs(ipkgtmp)

        ipkgdl = os.path.join(self.working_directory, "openwrt", "dl")
        if not os.path.exists(ipkgdl):
            self.log.debug(_("Create directory %s") % ipkgdl)
            os.makedirs(ipkgdl)

        ipkgos = os.path.join(self.working_directory, "openwrt", "os")
        if not os.path.exists(ipkgos):
            self.log.debug(_("Create directory %s") % ipkgos)
            os.makedirs(os.path.join(ipkgos, 'tmp'))
        else:
            self.log.debug(_("Clean directory %s") % ipkgos)
            self.execute_shell("rm -rf %s/*" % ipkgos)
            os.makedirs(os.path.join(ipkgos, 'tmp'))
            

        tmp = os.path.join(self.working_directory, "openwrt", "tmp")
        install = os.path.join(self.working_directory, "revisor-install")
        binopkg = os.path.join(self.openwrt_directory, "staging_dir", "host", "bin", "opkg")
        repo = "conf/conf.d/opkg.conf"

        cmd = "IPKG_NO_SCRIPT=1 IPKG_TMP='%s' IPKG_INSTROOT='%s' IPKG_CONF_DIR='%s' IPKG_OFFLINE_ROOT='%s' %s -f %s --offline-root %s --add-dest root:/ --add-arch all:100 --add-arch x86_64:200 update" % (ipkgtmp, install, tmp, install, binopkg, repo, install)
        self.execute_shell(cmd)

        return True

    def check_config(self, val=None):
        if val:
            config_file = val
        else:
            config_file = self.config

        if not os.access(config_file, os.R_OK):
            self.log.error(_("Configuration file %s not readable") % config_file)

        config = SafeConfigParser()
        self.log.debug(_("Reading configuration file %s") % config_file, level=9)
        try:
            config.read(config_file)
        except:
            self.log.error(_("Invalid configuration file %s") % config_file)

        if not config.has_section("revisor"):
            self.log.warning(_("No master configuration section [revisor] in configuration file %s") % config_file)

        return config

    def load_config(self, config):
        if config.has_section("revisor"):
            for varname in self.defaults.__dict__.keys():
                if not config.has_option("revisor", varname):
                    continue

                if isinstance(self.defaults.__dict__[varname], int):
                    val = config.getint("revisor",varname)
                elif isinstance(self.defaults.__dict__[varname], bool):
                    val = config.getboolean("revisor",varname)
                elif isinstance(self.defaults.__dict__[varname], str):
                    val = config.get("revisor",varname)
                elif isinstance(self.defaults.__dict__[varname], list):
                    val = eval(config.get("revisor",varname))
                elif isinstance(self.defaults.__dict__[varname], dict):
                    val = eval(config.get("revisor",varname))

                if not self.defaults.__dict__[varname] == val:
                    setattr(self,varname,val)
                    self.log.debug(_("Setting %s to %r (from configuration file)") % (varname,val))

    def options_set_from_config(self):
        self.log.debug(_("Setting options from configuration file"), level=4)

        if not self.options.config == self.defaults.config:
            self.config = self.options.config

        config = self.check_config()
        self.load_config(config)

    def options_set_from_commandline(self):
        self.log.debug(_("Setting options from command-line"))

        for option in self.options.__dict__.keys():
            if not self.options.__dict__[option] == self.defaults.__dict__[option]:
                self.log.debug(_("Setting %s to %r from command line") % (option, self.options.__dict__[option]), level=8)
                setattr(self, option, self.options.__dict__[option])

    def setup_ks(self):
        self.ksobj = RevisorKickstart(self)
        self.ksobj.create_parser()

    def load_kickstart(self, filename):
        self.log.debug(_("Load kickstart from file %s...") % filename)
        self.ksobj.read_file(filename)

    def get_item(self, item=None, val=None):
        return self.ksobj._get(item, val)

    def setup_opkg(self):
        if self.check_openwrt_directory() is False:
            sys.exit(1)

    def opkg_info_from_file(self, pkg):
        cmd = "find %s/bin/ -name %s_[0-9]*" % (self.openwrt_directory, pkg)
        lines = self.execute_shell(cmd)

        pkginfo = {}
        if len(lines) == 1:
            pkginfo['name'] = pkg
            pkginfo['size'] = os.path.getsize(lines[0])
            pkginfo['file'] = lines[0]

        return pkginfo

    def opkg_info(self, pkg):
        self.log.debug(_("Package info for %s...") % pkg)

        if pkg in ['kernel', 'libc']:
            return self.opkg_info_from_file(pkg)

        ipkgtmp = os.path.join(self.working_directory, "openwrt", "tmp", "ipkgtmp")
        tmp = os.path.join(self.working_directory, "openwrt", "tmp")
        ipkgdl = os.path.join(self.working_directory, "openwrt", "dl")
        install = os.path.join(self.working_directory, "revisor-install")
        binopkg = os.path.join(self.openwrt_directory, "staging_dir", "host", "bin", "opkg")
        repo = "conf/conf.d/opkg.conf"

        cmd = "IPKG_NO_SCRIPT=1 IPKG_TMP='%s' IPKG_INSTROOT='%s' IPKG_CONF_DIR='%s' IPKG_OFFLINE_ROOT='%s' %s -f %s --offline-root %s --add-dest root:/ --add-arch all:100 --add-arch x86_64:200 info %s" % (ipkgtmp, install, tmp, install, binopkg, repo, install, pkg)
        #print cmd
        pkginfo = {}
        for line in self.execute_shell(cmd):
            if re.match("^Package:", line):
                pkginfo['name'] = line.split(' ')[1]
            elif re.match("^Version:", line):
                pkginfo['version'] = line.split(' ')[1]
            elif re.match("^Depends:", line):
                pkginfo['depends'] = line[9:].split(', ')
            elif re.match("^Section:", line):
                pkginfo['section'] = line.split(' ')[1]
            elif re.match("^Size:", line):
                pkginfo['size'] = line.split(' ')[1]

        #if not 'name' in pkginfo:
        #    return None

        #print pkginfo
        return pkginfo

    def opkg_install(self, pkgs, packages):
        ipkgtmp = os.path.join(self.working_directory, "openwrt", "tmp", "ipkgtmp")
        tmp = os.path.join(self.working_directory, "openwrt", "tmp")
        ipkgdl = os.path.join(self.working_directory, "openwrt", "dl")
        install = os.path.join(self.working_directory, "openwrt", "os")
        binopkg = os.path.join(self.openwrt_directory, "staging_dir", "host", "bin", "opkg")
        repo = "conf/conf.d/opkg.conf"

        cmd = "IPKG_NO_SCRIPT=1 IPKG_TMP='%s' IPKG_INSTROOT='%s' IPKG_CONF_DIR='%s' IPKG_OFFLINE_ROOT='%s' %s -f %s --offline-root %s --add-dest root:/ --add-arch all:100 --add-arch x86_64:200 update" % (ipkgtmp, install, tmp, install, binopkg, repo, install)
        self.execute_shell(cmd)

        self.log.info(_("Installing package libgcc"))
        pkginfo = self.opkg_info_from_file('libgcc')
        cmd = "IPKG_NO_SCRIPT=1 IPKG_TMP='%s' IPKG_INSTROOT='%s' IPKG_CONF_DIR='%s' IPKG_OFFLINE_ROOT='%s' %s -f %s --offline-root %s --add-dest root:/ --add-arch all:100 --add-arch x86_64:200 install %s" % (ipkgtmp, install, tmp, install, binopkg, repo, install, pkginfo['file'])
        self.execute_shell(cmd)

        self.log.info(_("Installing package libc"))
        cmd = "IPKG_NO_SCRIPT=1 IPKG_TMP='%s' IPKG_INSTROOT='%s' IPKG_CONF_DIR='%s' IPKG_OFFLINE_ROOT='%s' %s -f %s --offline-root %s --add-dest root:/ --add-arch all:100 --add-arch x86_64:200 install %s" % (ipkgtmp, install, tmp, install, binopkg, repo, install, packages['libc']['file'])
        self.execute_shell(cmd)

        self.log.info(_("Installing package kernel"))
        cmd = "IPKG_NO_SCRIPT=1 IPKG_TMP='%s' IPKG_INSTROOT='%s' IPKG_CONF_DIR='%s' IPKG_OFFLINE_ROOT='%s' %s -f %s --offline-root %s --add-dest root:/ --add-arch all:100 --add-arch x86_64:200 install %s" % (ipkgtmp, install, tmp, install, binopkg, repo, install, packages['kernel']['file'])
        self.execute_shell(cmd)

        pkgs.remove('libc')
        pkgs.remove('kernel')
        
        cmd = "IPKG_NO_SCRIPT=1 IPKG_TMP='%s' IPKG_INSTROOT='%s' IPKG_CONF_DIR='%s' IPKG_OFFLINE_ROOT='%s' %s -f %s --offline-root %s --add-dest root:/ --add-arch all:100 --add-arch x86_64:200 install %s" % (ipkgtmp, install, tmp, install, binopkg, repo, install, ' '.join(pkgs))
        self.execute_shell(cmd)

class Defaults:
    def __init__(self):
        self.release_pkgs = ""
        self.release_files = "eula.txt"

        self.architecture = "x86_64"

class Runtime:
    def __init__(self, defaults):
        for option in defaults.__dict__.keys():
            self.__dict__[option] = defaults.__dict__[option]

        self.mediatypes = {
            "unified":  {
                "size": -1,
                "discdir": "unified",
                "label" : "",
                "discs": 1,
                "compose": "self.cfg.media_installation_unified"
            }
        }

        self.cmd_mkisofs = ['/usr/bin/mkisofs', '-v', '-U', '-J', '-R', '-T', '-f']

        self.bootargs = ['-b', 'isolinux/isolinux.bin', '-c', 'isolinux/boot.cat',
                         '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table']

