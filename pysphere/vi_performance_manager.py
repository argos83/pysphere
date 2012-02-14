#--
# Copyright (c) 2012, Sebastian Tello, Alejandro Lozanoff
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

from resources import VimService_services as VI
from resources.vi_exception import VIException, VIApiException, FaultTypes
import datetime

class EntityStatistics:
    def __init__(self, mor, counter_key, counter_name, counter_desc, group_name,
                 group_desc, unit_name, unit_desc, instance_name, value,
                 time_stamp):
        self.mor = mor
        self.counter_key = counter_key
        self.counter = counter_name
        self.description = counter_desc
        self.group = group_name
        self.group_description = group_desc
        self.unit = unit_name
        self.unit_description = unit_desc
        self.instance = instance_name
        self.value = value
        self.time = time_stamp

    def __str__(self):
        return "MOR: %s\nCounter: %s (%s)\nGroup: %s\nDescription: %s\n" \
               "Instance: %s\nValue: %s\nUnit: %s\nTime: %s" % (
                                       self.mor, self.counter, self.counter_key, 
                                       self.group_description, self.description,
                                       self.instance, self.value,
                                       self.unit_description, self.time)

    def __repr__(self):
        return"<%(mor)s:%(counter)s(%(counter_key)s):%(description)s" \
              ":%(instance)s:%(value)s:%(unit)s:%(time)s>" % self.__dict__

class PerformanceManager:

    def __init__(self, server, mor):
        self._server = server
        self._mor = mor

    def _get_counter_info(self, counter_id, counter_obj):
        """Return name, description, group, and unit info of a give counter_id.
        counter_id [int]: id of the counter.
        counter_obj [list]: An array consisting of performance
            counter information for the specified counterIds."""
        for c in counter_obj:
            if c.Key == counter_id:
                return (c.NameInfo.Key, c.NameInfo.Label, c.GroupInfo.Key, 
                        c.GroupInfo.Label, c.UnitInfo.Key, c.UnitInfo.Label)
        return None, None, None, None, None, None

    def _get_metric_id(self, metrics, counter_obj, counter_ids):
        """ Get the metric ID from a metric name.
        metrics [list]: An array of performance metrics with a
            performance counter ID and an instance name.
        counter_obj [list]: An array consisting of performance
            counter information for the specified counterIds.
        """
        metric_list = []
        for metric in metrics:
            if metric.CounterId in counter_ids:
                if metric not in metric_list:
                    metric_list.append(metric)
        return metric_list

    def get_entity_counters(self, entity):
        """Returns a dictionary of available counters. The dictionary key
        is the counter name, and value is the corresponding counter id"""
        refresh_rate = self.query_perf_provider_summary(entity).RefreshRate
        metrics = self.query_available_perf_metric(entity,
                                                   interval_id=refresh_rate)
        counter_obj = self.query_perf_counter([metric.CounterId 
                                               for metric in metrics])
        return dict([("%s.%s" % (c.GroupInfo.Key, c.NameInfo.Key), c.Key)
                     for c in counter_obj]) 
        

    def get_entity_statistic(self, entity, counters):
        """ Get the give statistics from a given managed object
        entity [mor]: ManagedObject Reference of the managed object from were
            statistics are to be retrieved.
        counter_id [list of integers or strings]: Counter names or ids 
                                                 to retrieve stats for.
        """
        if not isinstance(counters, list):
            counters = [counters]
            
        if any([isinstance(i, basestring) for i in counters]):
            avail_counters = self.get_entity_counters(entity)
            new_list = []
            for c in counters:
                if isinstance(c, int):
                    new_list.append(c)
                else:
                    counter_id = avail_counters.get(c)
                    if counter_id:
                        new_list.append(counter_id)
            counters = new_list
                    
        refresh_rate = self.query_perf_provider_summary(entity).RefreshRate
        metrics = self.query_available_perf_metric(entity,
                                                   interval_id=refresh_rate)
        counter_obj = self.query_perf_counter(counters)
        metric = self._get_metric_id(metrics, counter_obj, counters)
        if not metric:
            return []
        query = self.query_perf(entity, metric_id=metric, max_sample=1,
                                interval_id=refresh_rate)

        statistics = []
        if not query:
            return statistics
        for stat in query[0].Value:
            cname, cdesc, gname, gdesc, uname, udesc = self._get_counter_info(
                                                  stat.Id.CounterId,counter_obj)

            instance_name = str(stat.Id.Instance)
            stat_value = str(stat.Value[0])
            date_now = datetime.datetime.utcnow()
            statistics.append(EntityStatistics(entity, stat.Id.CounterId, cname,
                                               cdesc, gname, gdesc, uname, 
                                               udesc, instance_name, stat_value,
                                               date_now))
        return statistics

    def query_available_perf_metric(self, entity, begin_time=None,
                                                  end_time=None,
                                                  interval_id=None):
        """Retrieves available performance metrics for the specified
        ManagedObject between the optional beginTime and endTime. These are the
        performance statistics that are available for the given time interval.
        entity [mor]: The ManagedObject for which available performance metrics
            are queried.
        begin_time [dateTime]: The time from which available performance metrics
            are gathered. Corresponds to server time. When the beginTime is
            omitted, the returned metrics start from the first available metric
            in the system.
        end_time [dateTime]: The time up to which available performance metrics
            are gathered. Corresponds to server time. When the endTime is
            omitted, the returned result includes up to the most recent metric
            value.
        interval_id [int]: Specify a particular interval that the query is
            interested in. Acceptable intervals are the refreshRate returned in
            QueryProviderSummary, which is used to retrieve available metrics
            for real-time performance statistics, or one of the historical
            intervals, which are used to retrieve available metrics for
            historical performance statistics. If interval is not specified,
            system returns available metrics for historical statistics.
        """
        if begin_time:
            if not isinstance(begin_time, list) or len(begin_time) != 9:
                raise VIException("begin_time should be a 9 elements list",
                                  FaultTypes.PARAMETER_ERROR)
            begin_time[6] = 0
        if end_time:
            if not isinstance(end_time, list) or len(begin_time) != 9:
                raise VIException("end_time should be a 9 elements list",
                                  FaultTypes.PARAMETER_ERROR)
            end_time[6] = 0
        try:
            request = VI.QueryAvailablePerfMetricRequestMsg()
            mor_pm = request.new__this(self._mor)
            mor_pm.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_pm)

            mor_entity = request.new_entity(entity)
            mor_entity.set_attribute_type(entity.get_attribute_type())
            request.set_element_entity(mor_entity)

            if begin_time:
                request.set_element_beginTime(begin_time)
            if end_time:
                request.set_element_endTime(end_time)
            if interval_id:
                request.set_element_intervalId(interval_id)

            do_perf_metric_id = self._server._proxy.QueryAvailablePerfMetric(
                                                             request)._returnval
            return do_perf_metric_id

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def query_perf_provider_summary(self, entity):
        """Returns a ProviderSummary object for a ManagedObject for which 
        performance statistics can be queried. Also indicates whether current or
        summary statistics are supported. If the input managed entity is not a 
        performance provider, an InvalidArgument exception is thrown.
        entity [mor]: The ManagedObject for which available performance metrics
        are queried.
        """

        if not entity:
            raise VIException("No Entity specified.",FaultTypes.PARAMETER_ERROR)

        try:
            request = VI.QueryPerfProviderSummaryRequestMsg()
            mor_qpps = request.new__this(self._mor)
            mor_qpps.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_qpps)

            qpps_entity = request.new_entity(entity)
            qpps_entity.set_attribute_type(entity.get_attribute_type())
            request.set_element_entity(qpps_entity)

            qpps = self._server._proxy.QueryPerfProviderSummary(
                                                             request)._returnval
            return qpps

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def query_perf_counter(self, counter_id):
        """Retrieves counter information for the list of counter IDs passed in.
        counter_id [list]: list of integers containing the counter IDs.
        """

        if counter_id:
            if not isinstance(counter_id, list):
                raise VIException("counter_id must be a list",
                                  FaultTypes.PARAMETER_ERROR)
        else:
            raise VIException("No counter_id specified.",
                              FaultTypes.PARAMETER_ERROR)

        try:
            request = VI.QueryPerfCounterRequestMsg()
            mor_qpc = request.new__this(self._mor)
            mor_qpc.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_qpc)

            request.set_element_counterId(counter_id)

            qpc = self._server._proxy.QueryPerfCounter(request)._returnval
            return qpc

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def query_perf(self, entity, format='normal', interval_id=None, 
                   max_sample=None, metric_id=None, start_time=None):
        """Returns performance statistics for the entity. The client can limit
        the returned information by specifying a list of metrics and a suggested
        sample interval ID. Server accepts either the refreshRate or one of the
        historical intervals as input interval.
        entity [mor]: The ManagedObject managed object whose performance
            statistics are being queried.
        format [string]: The format to be used while returning the statistics.
        interval_id [int]: The interval (samplingPeriod) in seconds for which
            performance statistics are queried. There is a set of intervals for
            historical statistics. Refer HistoricalInterval for more more 
            information about these intervals. To retrieve the greatest 
            available level of detail, the provider's refreshRate may be used 
            for this property.
        max_sample [int]: The maximum number of samples to be returned from 
            server. The number of samples returned are more recent samples in 
            the time range specified. For example, if the user specifies a 
            maxSample of 1, but not a given time range, the most recent sample 
            collected is returned. This parameter can be used only when querying
            for real-time statistics by setting the intervalId parameter to the
            provider's refreshRate.
            This argument is ignored for historical statistics.
        metric_id: [PerfMetricId]: The performance metrics to be retrieved.
        start_time [dateTime]: The time from which statistics are to be
            retrieved. Corresponds to server time. When startTime is omitted,
            the returned metrics start from the first available metric in the
            system. When a startTime is specified, the returned samples do not
            include the sample at startTime.
        """

        if interval_id:
            if not isinstance(interval_id, int) or interval_id < 0:
                raise VIException("interval_id must be a positive integer",
                                  FaultTypes.PARAMETER_ERROR)
        if max_sample:
            if not isinstance(max_sample, int) or max_sample < 0:
                raise VIException("max_sample must be a positive integer",
                                  FaultTypes.PARAMETER_ERROR)
        # TODO: Proper checks
        if metric_id:
            if not isinstance(metric_id, list):
                raise VIException("metric_id must be a list of integers",
                                  FaultTypes.PARAMETER_ERROR)
        if start_time:
            if not isinstance(start_time, datetime.datetime):
                raise VIException("start_time must be datetime instance",
                                  FaultTypes.PARAMETER_ERROR)
        try:
            request = VI.QueryPerfRequestMsg()
            mor_qp = request.new__this(self._mor)
            mor_qp.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(mor_qp)

            query_spec_set = []
            query_spec = request.new_querySpec()

            spec_entity = query_spec.new_entity(entity)
            spec_entity.set_attribute_type(entity.get_attribute_type())
            query_spec.set_element_entity(spec_entity)

            if format != "normal":
                if format == "csv":
                    query_spec.set_element_format(format)
                else:
                    raise VIException("accepted formats are 'normal' and 'csv'",
                                  FaultTypes.PARAMETER_ERROR)
            if interval_id:
                query_spec.set_element_intervalId(interval_id)
            if max_sample:
                query_spec.set_element_maxSample(max_sample)
            if metric_id:
                query_spec.set_element_metricId(metric_id)
            if start_time:
                query_spec.set_element_startTime(start_time)

            query_spec_set.append(query_spec)
            request.set_element_querySpec(query_spec_set)

            query_perf = self._server._proxy.QueryPerf(request)._returnval

            return query_perf

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)
