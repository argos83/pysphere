#--
# Copyright (c) 2014, Sebastian Tello
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

import urllib, urllib2
import sys
import re

from pysphere.resources import VimService_services as VI
from pysphere import VIProperty, VIMor, MORTypes
from pysphere.vi_task import VITask
from pysphere.resources.vi_exception import VIException, VIApiException, \
                                            VITaskException, FaultTypes
from pysphere.vi_snapshot import VISnapshot
from pysphere.vi_managed_entity import VIManagedEntity


class VIFileManager:

    def __init__(self, server, mor):
        self._server = server
        self._mor = mor
        self._properties = VIProperty(server, mor)
        self._re_path = re.compile(r'\[(.*?)\] (.*)')

    def list_files(self, path, case_insensitive=True,
                   folders_first=True, match_patterns=[]):
        """Return a list of files in folder @path
        """

        ds_name, file_name = re.match(self._re_path, path).groups()
        ds = [k for k,v in self._server.get_datastores().items() if v == ds_name][0]
        browser_mor = VIProperty(self._server, ds).browser._obj

        request = VI.SearchDatastore_TaskRequestMsg()
        _this = request.new__this(browser_mor)
        _this.set_attribute_type(browser_mor.get_attribute_type())
        request.set_element__this(_this)
        request.set_element_datastorePath(path)

        search_spec = request.new_searchSpec()

        query = [VI.ns0.FloppyImageFileQuery_Def('floppy').pyclass(),
                 VI.ns0.FileQuery_Def('file').pyclass(),
                 VI.ns0.FolderFileQuery_Def('folder').pyclass(),
                 VI.ns0.IsoImageFileQuery_Def('iso').pyclass(),
                 VI.ns0.VmConfigFileQuery_Def('vm').pyclass(),
                 VI.ns0.TemplateConfigFileQuery_Def('template').pyclass(),
                 VI.ns0.VmDiskFileQuery_Def('vm_disk').pyclass(),
                 VI.ns0.VmLogFileQuery_Def('vm_log').pyclass(),
                 VI.ns0.VmNvramFileQuery_Def('vm_ram').pyclass(),
                 VI.ns0.VmSnapshotFileQuery_Def('vm_snapshot').pyclass()]
        search_spec.set_element_query(query)
        details = search_spec.new_details()
        details.set_element_fileOwner(True)
        details.set_element_fileSize(True)
        details.set_element_fileType(True)
        details.set_element_modification(True)
        search_spec.set_element_details(details)
        search_spec.set_element_searchCaseInsensitive(case_insensitive)
        search_spec.set_element_sortFoldersFirst(folders_first)
        search_spec.set_element_matchPattern(match_patterns)
        request.set_element_searchSpec(search_spec)
        response = self._server._proxy.SearchDatastore_Task(request)._returnval
        vi_task = VITask(response, self._server)
        if vi_task.wait_for_state([vi_task.STATE_ERROR, vi_task.STATE_SUCCESS]) == vi_task.STATE_ERROR:
            raise VITaskException(vi_task.info.error)
        info = vi_task.get_result()
        # return info

        if not hasattr(info, "file"):
            return []
        # for fi in info.file:
        #     fi._get_all()
        return [{'type':fi._type,
                 'path':fi.path,
                 'size':fi.fileSize,
                 'modified':fi.modification,
                 'owner':fi.owner
                } for fi in info.file]

    def make_directory(self, path, create_parent=False):
        """Creates new directory with given @path on datastore
        """
        try:
            request = VI.MakeDirectoryRequestMsg()
            _this = request.new__this(self._mor)
            _this.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(_this)
            request.set_element_name(path)
            request.set_element_createParentDirectories(create_parent)
            self._server._proxy.MakeDirectory(request)
        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def move_file(self, source_path, dest_path, source_datacenter=None,
                  dest_datacenter=None, force=False, sync_run=True):
        """Moves the source file or folder to the destination. If the destination
        file does not exist, it is created. If the destination file exists, the
        @force parameter determines whether to overwrite it with the source or not.
        Folders can be copied recursively. In this case, the destination, if it
        exists, must be a folder, else one will be created. Existing files on
        the destination that conflict with source files can be overwritten
        using the @force parameter.
        """
        try:
            request = VI.MoveDatastoreFile_TaskRequestMsg()
            _this = request.new__this(self._mor)
            _this.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(_this)
            request.set_element_sourceName(source_path)
            request.set_element_destinationName(dest_path)
            if source_datacenter:
                request.set_element_sourceDatacenter(source_datacenter)
            if dest_datacenter:
                request.set_element_destinationDatacenter(dest_datacenter)
            request.set_element_force(force)

            task = self._server._proxy.MoveDatastoreFile_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VITaskException(vi_task.info.error)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def copy_file(self, source_path, dest_path, source_datacenter=None,
                  dest_datacenter=None, force=False, sync_run=True):
        """Copies the source file or folder to the destination. If the destination
        file does not exist, it is created. If the destination file exists, the
        @force parameter determines whether to overwrite it with the source or not.
        Folders can be copied recursively. In this case, the destination, if it
        exists, must be a folder, else one will be created. Existing files on
        the destination that conflict with source files can be overwritten
        using the @force parameter.
        """
        try:
            request = VI.CopyDatastoreFile_TaskRequestMsg()
            _this = request.new__this(self._mor)
            _this.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(_this)
            request.set_element_sourceName(source_path)
            request.set_element_destinationName(dest_path)
            if source_datacenter:
                request.set_element_sourceDatacenter(source_datacenter)
            if dest_datacenter:
                request.set_element_destinationDatacenter(dest_datacenter)
            request.set_element_force(force)

            task = self._server._proxy.CopyDatastoreFile_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VITaskException(vi_task.info.error)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def delete_file(self, path, datacenter=None, sync_run=True):
        """Deletes the specified file or folder from the datastore.
        If a file of a virtual machine is deleted, it may corrupt
        that virtual machine. Folder deletes are always recursive.
        """
        try:
            request = VI.DeleteDatastoreFile_TaskRequestMsg()
            _this = request.new__this(self._mor)
            _this.set_attribute_type(self._mor.get_attribute_type())
            request.set_element__this(_this)
            request.set_element_name(path)
            if datacenter:
                request.set_element_datacenter(datacenter)

            task = self._server._proxy.DeleteDatastoreFile_Task(request)._returnval
            vi_task = VITask(task, self._server)
            if sync_run:
                status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                                 vi_task.STATE_ERROR])
                if status == vi_task.STATE_ERROR:
                    raise VITaskException(vi_task.info.error)
                return

            return vi_task

        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)

    def upload(self, local_file_path, remote_file_path):
        """Uploads @local_file_path to @remote_file_path on datastore
        replacing existing file. Returns True if @remote_file_path was replaced,
        otherwise False.
        """
        ds_name, file_name = re.match(self._re_path, remote_file_path).groups()
        fd = open(local_file_path, "r")
        data = fd.read()
        fd.close()
        resource = "/folder/%s" % file_name.lstrip("/")
        url = self._get_url(ds_name, resource)
        resp = self._do_request(url, data)
        return resp.code == 200

    def download(self, remote_file_path, local_file_path):
        """Downloads @remote_file_path from datastore to @local_file_path
        replacing existing file.
        """
        ds_name, file_name = re.match(self._re_path, remote_file_path).groups()
        resource = "/folder/%s" % file_name.lstrip("/")
        url = self._get_url(ds_name, resource)
        resp = self._do_request(url)
        CHUNK = 16 * 1024
        with open(local_file_path, "wb") as fd:
            while True:
                chunk = resp.read(CHUNK)
                if not chunk: break
                fd.write(chunk)

    def _do_request(self, url, data=None):
        opener = urllib2.build_opener()
        for cname, morsel in self._server._proxy.binding.cookies.iteritems():
            attrs = []
            value = morsel.get('version', '')
            if value != '' and value != '0':
                attrs.append('$Version=%s' % value)
            attrs.append('%s=%s' % (cname, morsel.coded_value))
            value = morsel.get('path')
            if value:
                attrs.append('$Path=%s' % value)
            value = morsel.get('domain')
            if value:
                attrs.append('$Domain=%s' % value)
            opener.addheaders.append(('Cookie', "; ".join(attrs)))
        request = urllib2.Request(url, data=data)
        if data:
            request.get_method = lambda: 'PUT'
        return opener.open(request)

    def _get_url(self, datastore, resource, datacenter=None):
        if not resource.startswith("/"):
            resource = "/" + resource
        resource = urllib.quote(resource)

        params = {"dsName":datastore}
        if datacenter:
            params["dcPath": datacenter]
        params = urllib.urlencode(params)

        return "%s%s?%s" % (self._get_service_url(), resource, params)

    def _get_service_url(self):
        service_url = self._server._proxy.binding.url
        return service_url[:service_url.rindex("/sdk")]
