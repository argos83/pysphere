import inspect

class VIProperty(object):
    
    def __init__(self, server, obj):
        self._server = server
        self._obj = obj        
        self._values_set = False
        self._type = obj.typecode.type[1]
        
    def _get_all(self):
        #If this is a MOR we need to recurse
        if self._type == 'ManagedObjectReference':
            oc = self._server._get_object_properties(self._obj, get_all=True)
            ps = oc[0].get_element_propSet()
            self._values = dict([(i.Name, i.Val) for i in ps])
        #Just inspect the attributes
        else:
            methods = getmembers(self._obj, predicate=inspect.ismethod)
            self._values = {}
            for name, method in methods:
                try:
                    if name.startswith("get_element_"):
                        self._values[name[12:]] = method()
                except AttributeError:
                    continue 
        self._values_set = True
        
        
    def __getattr__(self, name):
        if not self._values_set:
            self._get_all()
            
        if not name in self._values:
            raise AttributeError("object has not attribute %s" % name)
        
        ret = self._get_prop_value(self._values[name])
        #cache the object
        self.__setattr__(name, ret)
        return ret
        
        
    def _get_prop_value(self, prop):
        basic_types = (bool, int, float, basestring, tuple, long)
        class_name = prop.__class__.__name__
        
        #Holder is also a str, so this "if" must be first
        #if is a managed object reference
        if class_name == "Holder" and hasattr(prop, "get_attribute_type"):
            return VIProperty(self._server, prop)
        
        #Other Holder classes as enumerations can be treated as strings
        if isinstance(prop, basic_types):
            return prop
        if isinstance(prop, list):
            ret = []
            for i in prop:
                ret.append(self._get_prop_value(i))
            return ret
        
        if class_name == "DynamicData_Holder":
            return VIProperty(self._server, prop)
        
        if class_name.startswith("ArrayOf") and class_name.endswith("_Holder"):
            inner_prop = class_name[7:-7]
            ret = []
            for i in getattr(prop, "get_element_" + inner_prop)():
                ret.append(self._get_prop_value(i))
            return ret
         
        else:
            return prop
                
        
#PYTHON 2.5 inspect.getmembers does not catches AttributeError, this will do        
def getmembers(object, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
    results = []
    for key in dir(object):
        
        try:
            value = getattr(object, key)
        except AttributeError:
            continue
        if not predicate or predicate(value):
            results.append((key, value))
    results.sort()
    return results  