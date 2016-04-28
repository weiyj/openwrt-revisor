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

class RevisorPungi:
    def __init__(self, base):
        self.base = base
        self.cfg = base.cfg
        self.log = base.log

        self.destdir = os.path.join(self.cfg.working_directory,"revisor-install")
        self.archdir = os.path.join(self.destdir,
                                   self.cfg.version,
                                   self.cfg.model,
                                   self.cfg.architecture)

        self.topdir = os.path.join(self.archdir, 'os')
        self.isodir = os.path.join(self.archdir, 'iso')
        
        print self.archdir

    def buildIsolinux(self):
        self.log.info("Building isolinux directory")

        isolinux = "%s/isolinux" % self.topdir

        if not os.path.exists(isolinux):
            os.makedirs(isolinux)

        install = os.path.join(self.cfg.working_directory, "openwrt", "os")
        self.cfg.execute_shell("cd %s; find . | cpio -o -H newc | gzip -9 > %s/initrd.img" % (install, isolinux))

        self.cfg.execute_shell("cp /usr/share/syslinux/isolinux.bin %s" % isolinux)
        self.cfg.execute_shell("cp /usr/share/syslinux/ldlinux.c32 %s" % isolinux)
        self.cfg.execute_shell("cp conf/isolinux/boot.msg %s" % isolinux)
        self.cfg.execute_shell("cp conf/isolinux/splash.jpg %s" % isolinux)
        self.cfg.execute_shell("cp %s/bin/x86/openwrt-x86-64-vmlinuz %s/vmlinuz" % (self.cfg.openwrt_directory, isolinux))

        
    def doCreateIso(self, mediatype=None, disc=0,  callback=None, is_source=False):

        mt = self.cfg.mediatypes[mediatype]
        isoname = "%s-%s-%s" % (self.cfg.iso_basename, self.cfg.version, self.cfg.architecture)

        isoname = "%s.iso" % isoname

        isofile = os.path.join(self.cfg.destination_directory, "iso", isoname)
        
        extraargs = []
        if self.cfg.architecture == 'i386' or self.cfg.architecture == 'x86_64':
                extraargs.extend(self.cfg.bootargs)

        extraargs.append('-V')
        volume = "%s %s %s" % (self.cfg.iso_label, self.cfg.version, self.cfg.architecture)

        extraargs.extend(['"%s"' % volume])
        extraargs.extend(['-o', isofile])
        extraargs.extend(['-m', '*.iso'])
        extraargs.append(self.topdir)

        self.cfg.execute_shell(self.cfg.cmd_mkisofs + extraargs)
