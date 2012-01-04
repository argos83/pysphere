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

import time

from resources.vi_exception import VIException, FaultTypes, VIApiException
from resources import VimService_services as VI

class VITask:

    STATE_ERROR   =   'error'
    STATE_QUEUED  =   'queued'
    STATE_RUNNING =   'running'
    STATE_SUCCESS =   'success'

    def __init__(self, mor, server):
        self._mor = mor
        self._server = server
        self._task_info = None

    def get_state(self):
        """Returns the current state of the task"""
        
        self.__poll_task_info()
        if self._task_info:
            return self._task_info.State

    def wait_for_state(self, states, check_interval=2, timeout=-1):
        """Waits for the task to be in any of the given states
        checking the status every @check_interval seconds.
        Raises an exception if @timeout is reached
        If @timeout is 0 or negative, waits indefinitely"""
        
        if type(states).__name__ != 'list':
            states = [str(states)]
        start_time = time.clock()
        while True:
            cur_state = self.get_state()
            if cur_state in states:
                return cur_state

            if timeout > 0:
                if (time.clock() - start_time) > timeout:
                    raise VIException("Timed out waiting for task state.", 
                                      FaultTypes.TIME_OUT)

            time.sleep(check_interval)

    def get_error_message(self):
        """If the task finished with error, returns the related message"""
        
        if self._task_info and self._task_info.Error.LocalizedMessage:
            return self._task_info.Error.LocalizedMessage

    def get_result(self):
        "Returns the task result (if any) if it has successfully finished"
        
        if self._task_info and hasattr(self._task_info, "Result"):
            return self._task_info.Result

    def get_progress(self):
        """Returns a progress from 0 to 100 if the task is running and has
        available progress info, returns None otherwise"""
        self.__poll_task_info()
        if self._task_info and hasattr(self._task_info, "Progress"):
            return self._task_info.Progress

    def cancel(self):
        """Attempts to cancel this task"""
        try:
            request = VI.CancelTaskRequestMsg()
            _this = request.new__this(self._mor)
            _this.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(_this)
            
            self._server._proxy.CancelTask(request)
            
        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)
        
    def __poll_task_info(self, retries=3, interval=2):
        for i in range(retries):
            try:
                do_object_content = self._server._get_object_properties(
                                                        self._mor, get_all=True)
                if do_object_content is None:
                    raise Exception("do_object_content is None")

                for oc in do_object_content:
                    properties = oc.PropSet
                    for prop in properties:
                        if prop.Name == 'info':
                            self._task_info = prop.Val
                            return True
            except Exception, e:
                if i == retries -1:
                    raise e
            time.sleep(interval)