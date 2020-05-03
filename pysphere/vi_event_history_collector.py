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
#--

from pysphere import VIProperty, VIMor
from pysphere.resources import VimService_services as VI
from pysphere import VIException, VIApiException, FaultTypes
from pysphere.vi_history_collector import VIHistoryCollector

class Recursion:
    ALL      = "all"
    CHILDREN = "children"
    SELF     = "self"

class VIEventHistoryCollector(VIHistoryCollector):
    """
    EventHistoryCollector provides a mechanism for retrieving historical data and
    updates when the server appends new events.
    """

    RECURSION = Recursion

    def __init__(self, server, entity=None, recursion=None, types=None, chain_id=None):
        """Creates a Event History Collector that gathers Event objects.
        based on the provides filters.
          * server: the connected VIServer instance
          * entity: Entity MOR, if provided filters events related to this entity
          * recursion: If 'entity' is provided then recursion is mandatory.
          specification of related managed entities in the inventory hierarchy
          should be either: 'all', 'children', or 'self'
          * types: if provided, limits the set of collected events by their
          types.
          * chain_id: if provided, retrieves events by chain ID
        """

        super(VIEventHistoryCollector, self).__init__(server)

        if entity and not VIMor.is_mor(entity):
            raise VIException("Entity should be a MOR object",
                              FaultTypes.PARAMETER_ERROR)

        if entity and not recursion in [Recursion.ALL, Recursion.CHILDREN,
                                        Recursion.SELF]:
            raise VIException("Recursion should be either: "
                              "'all', 'children', or 'self'",
                              FaultTypes.PARAMETER_ERROR)

        try:
            event_manager = server._do_service_content.EventManager
            request = VI.CreateCollectorForEventsRequestMsg()
            _this = request.new__this(event_manager)
            _this.set_attribute_type(event_manager.get_attribute_type())
            request.set_element__this(_this)

            _filter = request.new_filter()

            if types and not isinstance(types, list):
                types = [types]
            if types:
                _filter.set_element_eventTypeId(types)

            if chain_id is not None:
                _filter.set_element_eventChainId(chain_id)

            if entity:
                entity_filter = _filter.new_entity()
                mor_entity = entity_filter.new_entity(entity)
                mor_entity.set_attribute_type(entity.get_attribute_type())
                entity_filter.set_element_entity(mor_entity)
                entity_filter.set_element_recursion(recursion)
                _filter.set_element_entity(entity_filter)

            request.set_element_filter(_filter)
            resp = server._proxy.CreateCollectorForEvents(request)._returnval

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

        self._mor = resp
        self._props = VIProperty(self._server, self._mor)


    def get_latest_events(self):
        """
        Returns a list of event items in the 'viewable latest page'. As new events
        that match the collector's filter are created, they are added to this
        page, and the oldest events are removed from the collector to keep the
        size of the page.
        The "oldest event" is the one with the oldest creation time.
        The events in the returned page are unordered.
        """
        self._props._flush_cache()
        if not hasattr(self._props, "latestPage"):
            return []

        ret = []
        for event in self._props.latestPage:
            ret.append(event)
        return ret

    def read_next_events(self, max_count):
        """
        Reads the 'scrollable view' from the current position.
        The scrollable position is moved to the next newer page after the read.
        No item is returned when the end of the collector is reached.
        """
        return self.__read_events(max_count, True)

    def read_previous_events(self, max_count):
        """
        Reads the 'scrollable view' from the current position. The scrollable
        position is then moved to the next older page after the read. No item is
        returned when the head of the collector is reached.
        """
        return self.__read_events(max_count, False)

    def reset(self):
        """
        Moves the 'scrollable view' to the item immediately preceding the
        'viewable latest page'. If you use 'read_previous_events' all items
        are retrieved from the newest item to the oldest item.
        """
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
        request = VI.RewindCollectorRequestMsg()
        _this = request.new__this(self._mor)
        _this.set_attribute_type(self._mor.get_attribute_type())
        request.set_element__this(_this)
        self._server._proxy.RewindCollector(request)

    def __read_events(self, max_count, next_page):

        if not isinstance(max_count, int):
            raise VIException("max_count should be an integer",
                              FaultTypes.PARAMETER_ERROR)

        if next_page:
            request = VI.ReadNextEventsRequestMsg()
        else:
            request = VI.ReadPreviousEventsRequestMsg()

        _this = request.new__this(self._mor)
        _this.set_attribute_type(self._mor.get_attribute_type())
        request.set_element__this(_this)

        request.set_element_maxCount(max_count)
        try:
            if next_page:
                resp = self._server._proxy.ReadNextEvents(request)._returnval
            else:
                resp = self._server._proxy.ReadPreviousEvents(request)._returnval

            ret = []
            for event in resp:
                ret.append(VIProperty(self._server, event))

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

        return ret
