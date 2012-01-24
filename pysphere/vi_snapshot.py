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

class VISnapshot:

    def __init__(self, snapshot_tree_prop, parent=None):
        self._parent = parent
        self._mor = snapshot_tree_prop.snapshot._obj
        self._state = snapshot_tree_prop.state
        self._name = snapshot_tree_prop.name
        self._description = snapshot_tree_prop.description
        self._create_time = snapshot_tree_prop.createTime
        self.__children = []
        for child in getattr(snapshot_tree_prop, 'childSnapshotList', []):
            snap = VISnapshot(child, self)
            self.__children.append(snap)
        self._index = 0

        
    def get_children(self):
        """Returns a list of VISnapshot instances representing this snapshot's
        children"""
        return self.__children[:]

    def get_create_time(self):
        """Returns the time of creation of this snapshot.
        A time tuple, e.g. (2010, 3, 29, 11, 12, 15, 21, 0, 0) """
        return self._create_time

    def get_description(self):
        """Returns the description string for this snapshot"""
        return self._description

    def get_name(self):
        """Returns the name of this snapshot"""
        return self._name

    def get_parent(self):
        """Returns an instance of VISnapshot representing this snapshot's parent
        snapshot. Or None if this is a root snapshot"""
        return self._parent

    def get_path(self):
        """returns the full path of this snapshot. This path is formed with the
        names of all the ancestors starting with and separated by '/'.
        E.g. /base/base2/child"""
        path= ''
        if(self._parent is not None):
            parent_path = self._parent.get_path()
            path = parent_path + '/' + self._name
        else:
            path = '/' + self._name

        return path

    def get_state(self):
        """Returns either 'poweredOff', 'poweredOn', or 'suspended' which
        represents the state in which the VM was when this snapshot was taken"""
        return self._state