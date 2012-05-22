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

from pysphere import VIException, FaultTypes, VIApiException
from pysphere.vi_property import VIProperty
from pysphere.resources import VimService_services as VI

class VITask:

    STATE_ERROR   =   'error'
    STATE_QUEUED  =   'queued'
    STATE_RUNNING =   'running'
    STATE_SUCCESS =   'success'

    def __init__(self, mor, server):
        self._mor = mor
        self._server = server
        self.info = None

    def get_info(self):
        """Returns a VIProperty object with information of this task"""
        self.__poll_task_info()
        return self.info
    
    def get_state(self):
        """Returns the current state of the task"""
        self.__poll_task_info()
        if hasattr(self.info, "state"):
            return self.info.state

    def wait_for_state(self, states, check_interval=2, timeout=-1):
        """Waits for the task to be in any of the given states
        checking the status every @check_interval seconds.
        Raises an exception if @timeout is reached
        If @timeout is 0 or negative, waits indefinitely"""
        
        if not isinstance(states, list):
            states = [states]
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
        self.__poll_task_info()
        if hasattr(self.info, "error") and hasattr(self.info.error, 
                                                   "localizedMessage"):
            return self.info.error.localizedMessage

    def get_result(self):
        "Returns the task result (if any) if it has successfully finished"
        self.__poll_task_info()
        if hasattr(self.info, "result"):
            return self.info.result

    def get_progress(self):
        """Returns a progress from 0 to 100 if the task is running and has
        available progress info, returns None otherwise"""
        self.__poll_task_info()
        if hasattr(self.info, "progress"):
            return self.info.progress

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
                self.info = VIProperty(self._server, self._mor).info
                return True
            except Exception, e:
                if i == retries -1:
                    raise e
            time.sleep(interval)