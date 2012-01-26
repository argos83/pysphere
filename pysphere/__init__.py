#--
# Copyright (c) 2012, Sebastian Tello
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   * Neither the name of copyright holders nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# For ZSI:
#
# Copyright 2001, Zolera Systems, Inc.  All Rights Reserved.
# Copyright 2002-2003, Rich Salz. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, and/or
# sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, provided that the above copyright notice(s) and
# this permission notice appear in all copies of the Software and that
# both the above copyright notice(s) and this permission notice appear in
# supporting documentation.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# OF THIRD PARTY RIGHTS. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS
# INCLUDED IN THIS NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT
# OR CONSEQUENTIAL DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE
# OR PERFORMANCE OF THIS SOFTWARE.
#
# Except as contained in this notice, the name of a copyright holder
# shall not be used in advertising or otherwise to promote the sale, use
# or other dealings in this Software without prior written authorization
# of the copyright holder.
#
#
# Portions are also:
#
# Copyright (c) 2003, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory (subject to receipt of
# any required approvals from the U.S. Dept. of Energy). All rights
# reserved. Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# (1) Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# (2) Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# (3) Neither the name of the University of California, Lawrence Berkeley
# National Laboratory, U.S. Dept. of Energy nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# You are under no obligation whatsoever to provide any bug fixes,
# patches, or upgrades to the features, functionality or performance of
# the source code ("Enhancements") to anyone; however, if you choose to
# make your Enhancements available either publicly, or directly to
# Lawrence Berkeley National Laboratory, without imposing a separate
# written license agreement for such Enhancements, then you hereby grant
# the following license: a non-exclusive, royalty-free perpetual license
# to install, use, modify, prepare derivative works, incorporate into
# other computer software, distribute, and sublicense such Enhancements
# or derivative works thereof, in binary and source code form.
#
#
# For wstools also:
#
# Zope Public License (ZPL) Version 2.0
# -----------------------------------------------
#
# This software is Copyright (c) Zope Corporation (tm) and
# Contributors. All rights reserved.
#
# This license has been certified as open source. It has also
# been designated as GPL compatible by the Free Software
# Foundation (FSF).
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions in source code must retain the above
#    copyright notice, this list of conditions, and the following
#    disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions, and the following
#    disclaimer in the documentation and/or other materials
#    provided with the distribution.
#
# 3. The name Zope Corporation (tm) must not be used to
#    endorse or promote products derived from this software
#    without prior written permission from Zope Corporation.
#
# 4. The right to distribute this software or to use it for
#    any purpose does not give you the right to use Servicemarks
#    (sm) or Trademarks (tm) of Zope Corporation. Use of them is
#    covered in a separate agreement (see
#    http://www.zope.com/Marks).
#
# 5. If any files are modified, you must cause the modified
#    files to carry prominent notices stating that you changed
#    the files and the date of any change.
#
# Disclaimer
#
#   THIS SOFTWARE IS PROVIDED BY ZOPE CORPORATION ``AS IS''
#   AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT
#   NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
#   AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN
#   NO EVENT SHALL ZOPE CORPORATION OR ITS CONTRIBUTORS BE
#   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#   LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
#   OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#   DAMAGE.
#
#
# This software consists of contributions made by Zope
# Corporation and many individuals on behalf of Zope
# Corporation.  Specific attributions are listed in the
# accompanying credits file.
#
#--
__all__ = ['VIServer', 'VIException', 'VIApiException', 'VITask', 'FaultTypes',
            'VIMor', 'MORTypes', 'VMPowerState', 'ToolsStatus', 'VIProperty']

from vi_server import VIServer
from vi_virtual_machine import VMPowerState, ToolsStatus
from vi_property import VIProperty
from vi_task import VITask
from vi_mor import VIMor, MORTypes
from resources.vi_exception import VIException, VIApiException, FaultTypes
#from version import version as __version__
