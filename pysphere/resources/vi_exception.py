#--
# Copyright (c) 2011, Sebastian Tello
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
#--

class VIException(Exception):
    def __init__(self, msg, fault):
        self.message = str(msg)
        self.fault = str(fault)
    def __str__(self):
        return "[%s]: %s" % (self.fault, self.message)


class VIApiException(VIException):
    def __init__(self, e):
        try:
            message = e.fault.args[1]
        except:
            message = str(e)
        try:
            fault = e.fault.detail[0].typecode.pname
        except:
            fault = 'Undefined'

        super(self.__class__, self).__init__(message, fault)

class FaultTypes:
    PARAMETER_ERROR    = 'Parameter Error'
    VM_NOT_FOUND_ERROR = 'VM Not Found'
    FOLDER_NOT_FOUND   = 'Folder Not Found'
    NOT_CONNECTED      = 'Not Connected'
    TIME_OUT           = 'Operation Timed Out'
    SNAPSHOT_NOT_FOUND = 'Snapshot Not Found'
    TASK_ERROR         = 'Task Error'
    NOT_SUPPORTED      = 'Operation Not Supported'
    INVALID_OPERATION  = 'Invalid Operation'