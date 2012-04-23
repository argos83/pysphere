############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################

import pydoc, sys
from pysphere.ZSI import TC

# If function.__name__ is read-only, fail
def _x(): return
try:
    _x.func_name = '_y'
except:
    raise RuntimeError(
        'use python-2.4 or later, cannot set function names in python "%s"'
        %sys.version)
del _x


#def GetNil(typecode=None):
#    """returns the nilled element, use to set an element
#    as nilled for immutable instance.
#    """
#
#    nil = TC.Nilled()
#    if typecode is not None: nil.typecode = typecode
#    return nil
#
#
#def GetNilAsSelf(cls, typecode=None):
#    """returns the nilled element with typecode specified,
#    use returned instance to set this element as nilled.
#
#    Key Word Parameters:
#        typecode -- use to specify a derived type or wildcard as nilled.
#    """
#    if typecode is not None and not isinstance(typecode, TC.TypeCode):
#        raise TypeError, "Expecting a TypeCode instance"
#
#    nil = TC.Nilled()
#    nil.typecode = typecode or cls.typecode
#    return nil


class pyclass_type(type):
    """Stability: Unstable

    type for pyclasses used with typecodes.  expects the typecode to
    be available in the classdict.  creates python properties for accessing
    and setting the elements specified in the ofwhat list, and factory methods
    for constructing the elements.

    Known Limitations:
        1)Uses XML Schema element names directly to create method names,
           using characters in this set will cause Syntax Errors:

              (NCNAME)-(letter U digit U "_")

    """
    def __new__(cls, classname, bases, classdict):
        """
        """
        #import new
        typecode = classdict.get('typecode')
        assert typecode is not None, 'MUST HAVE A TYPECODE.'

        # Assume this means immutable type. ie. str
        if len(bases) > 0:
            #classdict['new_Nill'] = classmethod(GetNilAsSelf)
            pass
        # Assume this means mutable type. ie. ofwhat.
        else:
            assert hasattr(typecode, 'ofwhat'), 'typecode has no ofwhat list??'
            assert hasattr(typecode, 'attribute_typecode_dict'),\
                'typecode has no attribute_typecode_dict??'

            #classdict['new_Nill'] = staticmethod(GetNil)

            if typecode.mixed:
                get,_set = cls.__create_text_functions_from_what(typecode)

                if get.__name__ in classdict:
                    raise AttributeError('attribute %s previously defined.' %get.__name__)

                if _set.__name__ in classdict:
                    raise AttributeError('attribute %s previously defined.' %_set.__name__)

                classdict[get.__name__] = get
                classdict[_set.__name__] = _set

            for what in typecode.ofwhat:
                get,_set,new_func = cls.__create_functions_from_what(what)

                if get.__name__ in  classdict:
                    raise AttributeError('attribute %s previously defined.' %get.__name__)

                classdict[get.__name__] = get
                if _set.__name__ in classdict:
                    raise AttributeError('attribute %s previously defined.' %_set.__name__)

                classdict[_set.__name__] = _set
                if new_func is not None:
                    if new_func.__name__ in classdict:
                        raise AttributeError('attribute %s previously defined.' %new_func.__name__)
                    classdict[new_func.__name__] = new_func

                assert what.pname not in classdict,\
                    'collision with pname="%s", bail..' %what.pname

                pname = what.pname
                if pname is None and isinstance(what, TC.AnyElement): pname = 'any'
                assert pname is not None, 'Element with no name: %s' %what

                # TODO: for pname if keyword just uppercase first letter.
                pname = pname[0].upper() + pname[1:]
                assert pname not in pydoc.Helper.keywords, 'unexpected keyword: %s' %pname

                classdict[pname] =\
                    property(get, _set, None,
                        'property for element (%s,%s), minOccurs="%s" maxOccurs="%s" nillable="%s"'\
                        %(what.nspname,what.pname,what.minOccurs,what.maxOccurs,what.nillable)
                        )

        #
        # mutable type <complexType> complexContent | modelGroup
        # or immutable type <complexType> simpleContent (float, str, etc)
        #
        if hasattr(typecode, 'attribute_typecode_dict'):
            attribute_typecode_dict = typecode.attribute_typecode_dict or {}
            for key,what in attribute_typecode_dict.iteritems():
                get,_set = cls.__create_attr_functions_from_what(key, what)
                if get.__name__ in classdict:
                    raise AttributeError,\
                        'attribute %s previously defined.' %get.__name__

                if _set.__name__ in classdict:
                    raise AttributeError,\
                        'attribute %s previously defined.' %_set.__name__

                classdict[get.__name__] = get
                classdict[_set.__name__] = _set

        return type.__new__(cls,classname,bases,classdict)

    def __create_functions_from_what(what):
        if not callable(what):
            def get(self):
                return getattr(self, what.aname)

            if what.maxOccurs > 1:
                def _set(self, value):
                    if not (value is None or hasattr(value, '__iter__')):
                        raise TypeError('expecting an iterable instance')
                    setattr(self, what.aname, value)
            else:
                def _set(self, value):
                    setattr(self, what.aname, value)
        else:
            def get(self):
                return getattr(self, what().aname)

            if what.maxOccurs > 1:
                def _set(self, value):
                    if not (value is None or hasattr(value, '__iter__')):
                        raise TypeError, 'expecting an iterable instance'
                    setattr(self, what().aname, value)
            else:
                def _set(self, value):
                    setattr(self, what().aname, value)

        #
        # new factory function
        # if pyclass is None, skip
        #
        if not callable(what) and getattr(what, 'pyclass', None) is None:
            new_func = None
        elif (isinstance(what, TC.ComplexType) or
            isinstance(what, TC.Array)):

            def new_func(self):
                '''returns a mutable type
                '''
                return what.pyclass()

        elif not callable(what):

            def new_func(self, value):
                '''value -- initialize value
                returns an immutable type
                '''
                return what.pyclass(value)

        elif (issubclass(what.klass, TC.ComplexType) or
              issubclass(what.klass, TC.Array)):

            def new_func(self):
                '''returns a mutable type or None (if no pyclass).
                '''
                p = what().pyclass
                if p is None: return
                return p()

        else:

            def new_func(self, value=None):
                '''if simpleType provide initialization value, else
                if complexType value should be left as None.
                Parameters:
                    value -- initialize value or None

                returns a mutable instance (value is None)
                    or an immutable instance or None (if no pyclass)
                '''
                p = what().pyclass
                if p is None: return
                if value is None: return p()
                return p(value)

        #TODO: sub all illegal characters in _set
        #    (NCNAME)-(letter U digit U "_")
        if new_func is not None:
            new_func.__name__ = 'new_%s' %what.pname
        get.func_name = 'get_element_%s' %what.pname
        _set.func_name = 'set_element_%s' %what.pname
        return get,_set,new_func
    __create_functions_from_what = staticmethod(__create_functions_from_what)

    def __create_attr_functions_from_what(key, what):

        def get(self):
            '''returns attribute value for attribute %s, else None.
            ''' %str(key)
            return getattr(self, what.attrs_aname, {}).get(key, None)

        def _set(self, value):
            '''set value for attribute %s.
            value -- initialize value, immutable type
            ''' %str(key)
            if not hasattr(self, what.attrs_aname):
                setattr(self, what.attrs_aname, {})
            getattr(self, what.attrs_aname)[key] = value

        #TODO: sub all illegal characters in set
        #    (NCNAME)-(letter U digit U "_")
        if isinstance(key, (tuple, list)):
            get.__name__ = 'get_attribute_%s' %key[1]
            _set.__name__ = 'set_attribute_%s' %key[1]
        else:
            get.__name__ = 'get_attribute_%s' %key
            _set.__name__ = 'set_attribute_%s' %key

        return get,_set
    __create_attr_functions_from_what = \
        staticmethod(__create_attr_functions_from_what)

    def __create_text_functions_from_what(what):

        def get(self):
            '''returns text content, else None.
            '''
            return getattr(self, what.mixed_aname, None)

        get.im_func = 'get_text'

        def _set(self, value):
            '''set text content.
            value -- initialize value, immutable type
            '''
            setattr(self, what.mixed_aname, value)

        get.im_func = 'set_text'

        return get,_set
    __create_text_functions_from_what = \
        staticmethod(__create_text_functions_from_what)



