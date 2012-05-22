from pysphere import VIProperty, VITask, VIMor
from pysphere.resources import VimService_services as VI
from pysphere import VIException, VIApiException, FaultTypes

class Recursion:
    ALL      = "all"
    CHILDREN = "children"
    SELF     = "self"
    
class States:
    ERROR   = "error"
    QUEUED  = "queued"
    RUNNING = "running"
    SUCCESS = "success"

class VITaskHistoryCollector(object):
    """
    TaskHistoryCollector provides a mechanism for retrieving historical data and 
    updates when the server appends new tasks.
    """
    
    RECURSION = Recursion
    STATES = States
    
    def __init__(self, server, entity=None, recursion=None, states=None):
        """Creates a Task History Collector that gathers Task info objects.
        based on the provides filters.
          * server: the connected VIServer instance
          * entity: Entity MOR, if provided filters tasks related to this entity
          * recursion: If 'entity' is provided then recursion is mandatory.
          specification of related managed entities in the inventory hierarchy
          should be either: 'all', 'children', or 'self'
          * states: if provided, limits the set of collected tasks by their 
          states. Should be a list or one of 'queued', 'running', 'error', or
          'success'  
        """
        
        self._server = server
        self._mor = None
        
        if entity and not VIMor.is_mor(entity):
            raise VIException("Entity should be a MOR object",
                              FaultTypes.PARAMETER_ERROR)
        
        if entity and not recursion in [Recursion.ALL, Recursion.CHILDREN,
                                        Recursion.SELF]:
            raise VIException("Recursion should be either: " 
                              "'all', 'children', or 'self'", 
                              FaultTypes.PARAMETER_ERROR)
        
        try:
            task_manager = server._do_service_content.TaskManager
            request = VI.CreateCollectorForTasksRequestMsg()
            _this = request.new__this(task_manager)
            _this.set_attribute_type(task_manager.get_attribute_type())
            request.set_element__this(_this)
                   
            _filter = request.new_filter()
            
            if states and not isinstance(states, list):
                states = [states]
            if states:
                _filter.set_element_state(states)
            
            if entity:
                entity_filter = _filter.new_entity()
                mor_entity = entity_filter.new_entity(entity)
                mor_entity.set_attribute_type(entity.get_attribute_type())
                entity_filter.set_element_entity(mor_entity)
                entity_filter.set_element_recursion(recursion)
                _filter.set_element_entity(entity_filter)
            
            request.set_element_filter(_filter)
            resp = server._proxy.CreateCollectorForTasks(request)._returnval
        
        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)
        
        self._mor = resp
        self._props = VIProperty(self._server, self._mor)
        

    def get_latest_tasks(self):
        """
        Returns a list of task items in the 'viewable latest page'. As new tasks
        that match the collector's filter are created, they are added to this
        page, and the oldest tasks are removed from the collector to keep the 
        size of the page.
        The "oldest task" is the one with the oldest creation time. 
        The tasks in the returned page are unordered. 
        """
        self._props._flush_cache()
        if not hasattr(self._props, "latestPage"):
            return []
        
        ret = []
        for task in self._props.latestPage:
            ret.append(VITask(task.task._obj, self._server))
        return ret
    
    def read_next_tasks(self, max_count):
        """
        Reads the 'scrollable view' from the current position. 
        The scrollable position is moved to the next newer page after the read.
        No item is returned when the end of the collector is reached.
        """
        return self.__read_tasks(max_count, True)
    
    def read_previous_tasks(self, max_count):
        """
        Reads the 'scrollable view' from the current position. The scrollable 
        position is then moved to the next older page after the read. No item is
        returned when the head of the collector is reached.
        """
        return self.__read_tasks(max_count, False)
    
    
    def __read_tasks(self, max_count, next_page):
        
        if not isinstance(max_count, int):
            raise VIException("max_count should be an integer", 
                              FaultTypes.PARAMETER_ERROR)
        
        if next_page:
            request = VI.ReadNextTasksRequestMsg()
        else:
            request = VI.ReadPreviousTasksRequestMsg()
            
        _this = request.new__this(self._mor)
        _this.set_attribute_type(self._mor.get_attribute_type())
        request.set_element__this(_this)
        
        request.set_element_maxCount(max_count)
        try:
            if next_page:
                resp = self._server._proxy.ReadNextTasks(request)._returnval
            else:
                resp = self._server._proxy.ReadPreviousTasks(request)._returnval
            
            ret = []
            for task in resp:
                ret.append(VITask(task.Task, self._server))
        
        except (VI.ZSI.FaultException), e:
            raise VIApiException(e)
        
        return ret