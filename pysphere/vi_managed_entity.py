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

from pysphere.resources import VimService_services as VI
from pysphere.vi_task import VITask
from pysphere.resources.vi_exception import VIException, VIApiException, \
                                            FaultTypes

class VIManagedEntity(object):

    def __init__(self, server, mor):
        self._server = server
        self._mor = mor
        
    def rename(self, new_name, sync_run=True):
        """
        Renames this managed entity.
          * new_name: Any / (slash), \ (backslash), character used in this name
            element will be escaped. Similarly, any % (percent) character used
            in this name element will be escaped, unless it is used to start an
            escape sequence. A slash is escaped as %2F or %2f. A backslash is
            escaped as %5C or %5c, and a percent is escaped as %25.
          * sync_run: (default True), If False does not wait for the task to
            finish and returns an instance of a VITask for the user to monitor
            its progress 
        """
        try:
            request = VI.Rename_TaskRequestMsg()
            _this = request.new__this(self._mor)
            _this.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(_this)
            request.set_element_newName(new_name)

            task = self._server._proxy.Rename_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                      FaultTypes.TASK_ERROR)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)
        
    def reload(self):
        """
        Reload the entity state.
        Clients only need to call this method if they changed some external
        state that affects the service without using the Web service interface
        to perform the change. For example, hand-editing a virtual machine 
        configuration file affects the configuration of the associated virtual
        machine but the service managing the virtual machine might not monitor
        the file for changes. In this case, after such an edit, a client would
        call "reload" on the associated virtual machine to ensure the service
        and its clients have current data for the virtual machine.
        """
        try:
            request = VI.ReloadRequestMsg()
            _this = request.new__this(self._mor)
            _this.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(_this)
            self._server._proxy.Reload(request)
        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)
        
    def destroy(self, sync_run=True):
        """
        Destroys this object, deleting its contents and removing it from its 
        parent folder (if any)
        * sync_run: (default True), If False does not wait for the task to
            finish and returns an instance of a VITask for the user to monitor
            its progress
        """
        try:
            request = VI.Destroy_TaskRequestMsg()
            _this = request.new__this(self._mor)
            _this.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(_this)
            

            task = self._server._proxy.Destroy_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VIException(vi_task.get_error_message(),
                                      FaultTypes.TASK_ERROR)
                return

            return vi_task
        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)