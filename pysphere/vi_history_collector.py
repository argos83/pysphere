#--
# Copyright (c) 2017, Jiri Machalek
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

from pysphere.resources import VimService_services as VI
from pysphere import VIException, FaultTypes

class VIHistoryCollector(object):
    """
    HistoryCollector provides is abstract base class for task and event history
    collectors.
    """

    def __init__(self, server):
        """Creates a History Collector that gathers history objects.
        based on the provides filters.
          * server: the connected VIServer instance
        """

        self._server = server
        self._mor = None

    def reset(self):
        """
        Moves the 'scrollable view' to the item immediately preceding the
        'viewable latest page'. If you use 'read_previous_events' all items
        are retrieved from the newest item to the oldest item.
        """
        if not self._mor:
            raise VIException("History collector is not properly initialized",
                              FaultTypes.PARAMETER_ERROR)
        request = VI.ResetCollectorRequestMsg()
        _this = request.new__this(self._mor)
        _this.set_attribute_type(self._mor.get_attribute_type())
        request.set_element__this(_this)
        self._server._proxy.ResetCollector(request)

    def rewind(self):
        """
        Moves the 'scrollable view' to the oldest item. If you use
        'read_next_events', all items are retrieved from the oldest item to
        the newest item. This is the default setting when the collector is
        created.
        """
        if not self._mor:
            raise VIException("History collector is not properly initialized",
                              FaultTypes.PARAMETER_ERROR)
        request = VI.RewindCollectorRequestMsg()
        _this = request.new__this(self._mor)
        _this.set_attribute_type(self._mor.get_attribute_type())
        request.set_element__this(_this)
        self._server._proxy.RewindCollector(request)

