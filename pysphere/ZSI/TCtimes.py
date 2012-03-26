#! /usr/bin/env python
# $Header$
'''Typecodes for dates and times.
'''

from pysphere.ZSI import _copyright, _floattypes, _inttypes, EvaluateException
from pysphere.ZSI.TC import SimpleType
from pysphere.ZSI.wstools.Namespaces import SCHEMA
import operator, re, time as _time
from time import mktime as _mktime, localtime as _localtime, gmtime as _gmtime
from datetime import tzinfo as _tzinfo, timedelta as _timedelta,\
    datetime as _datetime, MAXYEAR
from math import modf as _modf

MINYEAR = 1970

# Year, month or day may be None
_niltime = [None] * 3 + [0] * 6

#### Code added to check current timezone offset
_zero = _timedelta(0)

class _localtimezone(_tzinfo):
    def __init__(self, *a, **kw):
        _tzinfo.__init__(self, *a, **kw)
        self.__dstoffset = self.__stdoffset = _timedelta(seconds=-_time.timezone)
        if _time.daylight: self.__dstoffset = _timedelta(seconds=-_time.altzone)
        self.__dstdiff = self.__dstoffset - self.__stdoffset

    """ """
    def dst(self, dt):
        """datetime -> DST offset in minutes east of UTC."""
        tt = _localtime(_mktime((dt.year, dt.month, dt.day,
                 dt.hour, dt.minute, dt.second, dt.weekday(), 0, -1)))
        if tt.tm_isdst > 0: return self.__dstdiff
        return _zero

    #def fromutc(...)
    #datetime in UTC -> datetime in local time.

    def tzname(self, dt):
        """datetime -> string name of time zone."""
        tt = _localtime(_mktime((dt.year, dt.month, dt.day,
                 dt.hour, dt.minute, dt.second, dt.weekday(), 0, -1)))
        return _time.tzname[tt.tm_isdst > 0]

    def utcoffset(self, dt):
        """datetime -> minutes east of UTC (negative for west of UTC)."""
        tt = _localtime(_mktime((dt.year, dt.month, dt.day,
                 dt.hour, dt.minute, dt.second, dt.weekday(), 0, -1)))
        if tt.tm_isdst > 0: return self.__dstoffset
        return self.__stdoffset

class _fixedoffset(_tzinfo):
    """Fixed offset in minutes east from UTC.

    A class building tzinfo objects for fixed-offset time zones.
    Note that _fixedoffset(0, "UTC") is a different way to build a
    UTC tzinfo object.
    """
    #def __init__(self, offset, name):
    def __init__(self, offset):
        self.__offset = _timedelta(minutes=offset)
        #self.__name = name

    def dst(self, dt):
        """datetime -> DST offset in minutes east of UTC."""
        return _zero

    def tzname(self, dt):
        """datetime -> string name of time zone."""
        #return self.__name
        return "server"

    def utcoffset(self, dt):
        """datetime -> minutes east of UTC (negative for west of UTC)."""
        return self.__offset

def _tz_to_tzinfo(tz):
    if not tz:
        return _localtimezone()
    if tz == "Z": tz = "+00:00"
    h, m = map(int, tz.split(':'))
    if h < 0: m = -m
    return _fixedoffset(60 * h + m)

def _fix_timezone(tv, tz_from = "Z", tz_to = None):
    if None in tv[3:5]: # Hour or minute is absent
        return tv

    # Fix local copy of time tuple
    ltv = list(_fix_none_fields(tv))

    if ltv[0] < MINYEAR + 1 or ltv[0] > MAXYEAR - 1:
        return tv # Unable to fix timestamp

    _tz_from = _tz_to_tzinfo(tz_from)
    _tz_to   = _tz_to_tzinfo(tz_to)

    ltv[:6] = _datetime(*(ltv[:6] + [0, _tz_from])).astimezone(_tz_to).timetuple()[:6]

    # Patch local copy with original values
    for i in range(0, 6):
        if tv[i] is None: ltv[i] = None

    return tuple(ltv)

def _fix_none_fields(tv):
    ltv = list(tv)
    if ltv[0] is None: ltv[0] = MINYEAR + 1 # Year is absent
    if ltv[1] is None: ltv[1] = 1 # Month is absent
    if ltv[2] is None: ltv[2] = 1 # Day is absent
    return tuple(ltv)

def _dict_to_tuple(d):
    '''Convert a dictionary to a time tuple.  Depends on key values in the
    regexp pattern!
    '''
    # TODO: Adding a ms field to struct_time tuples is problematic
    # since they don't have this field.  Should use datetime
    # which has a microseconds field, else no ms..  When mapping struct_time
    # to gDateTime the last 3 fields are irrelevant, here using dummy values to make
    # everything happy.
    #

    retval = _niltime[:]
    for k,i in ( ('Y', 0), ('M', 1), ('D', 2), ('h', 3), ('m', 4), ):
        v = d.get(k)
        if v: retval[i] = int(v)

    v = d.get('s')
    if v:
        msec,sec = _modf(float(v))
        retval[6],retval[5] = int(round(msec*1000)), int(sec)

    if d.get('neg', 0):
        retval[0:5] = map(lambda x: (x is not None or x) and operator.__neg__(x), retval[0:5])

    return tuple(retval)


class Duration(SimpleType):
    '''Time duration.
    '''
    parselist = [ (None,'duration') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)P' \
                    r'((?P<Y>\d+)Y)?' r'((?P<M>\d+)M)?' r'((?P<D>\d+)D)?' \
                    r'(?P<T>T?)' r'((?P<h>\d+)H)?' r'((?P<m>\d+)M)?' \
                    r'((?P<s>\d*(\.\d+)?)S)?' '$')
    type = (SCHEMA.XSD3, 'duration')


    def text_to_data(self, text, elt, ps):
        '''convert text into typecode specific data.
        '''
        if text is None:
            return None
        m = Duration.lex_pattern.match(text)
        if m is None:
            raise EvaluateException('Illegal duration', ps.Backtrace(elt))
        d = m.groupdict()
        if d['T'] and (d['h'] is None and d['m'] is None and d['s'] is None):
            raise EvaluateException('Duration has T without time')
        try:
            retval = _dict_to_tuple(d)
        except ValueError, e:
            raise EvaluateException(str(e))

        if self.pyclass is not None:
            return self.pyclass(retval)
        return retval

    def get_formatted_content(self, pyobj):
        if isinstance(pyobj, _floattypes) or isinstance(pyobj, _inttypes):
            pyobj = _gmtime(pyobj)

        pyobj = tuple(pyobj)
        if 1 in map(lambda x: x < 0, pyobj[0:6]):
            pyobj = map(abs, pyobj)
            neg = '-'
        else:
            neg = ''

        val = '%sP%dY%dM%dDT%dH%dM%dS' % \
            ( neg, pyobj[0], pyobj[1], pyobj[2], pyobj[3], pyobj[4], pyobj[5])

        return val


class Gregorian(SimpleType):
    '''Gregorian times.
    '''
    lex_pattern = tag = format = None
    fix_timezone = False

    def text_to_data(self, text, elt, ps):
        '''convert text into typecode specific data.
        '''
        if text is None:
            return None

        m = self.lex_pattern.match(text)
        if not m:
            raise EvaluateException('Bad Gregorian: %s' %text, ps.Backtrace(elt))
        try:
            retval = _dict_to_tuple(m.groupdict())
        except ValueError:
            raise

        if self.fix_timezone:
            retval = _fix_timezone(retval, tz_from = m.groupdict().get('tz'), tz_to = None)

        retval = _fix_none_fields(retval)

        if self.pyclass is not None:
            return self.pyclass(retval)
        return retval

    def get_formatted_content(self, pyobj):
        if isinstance(pyobj, _floattypes) or isinstance(pyobj, _inttypes):
            pyobj = _gmtime(pyobj)

        if self.fix_timezone:
            pyobj = _fix_timezone(pyobj, tz_from = None, tz_to = "Z")

        d = {}
        pyobj = tuple(pyobj)
        if 1 in map(lambda x: x < 0, pyobj[0:6]):
            pyobj = map(abs, pyobj)
            d['neg'] = '-'
        else:
            d['neg'] = ''

        d = {}
        for k,i in [ ('Y', 0), ('M', 1), ('D', 2), ('h', 3), ('m', 4), ('s', 5) ]:
            d[k] = pyobj[i]

        ms = pyobj[6]
        if not ms or not hasattr(self, 'format_ms'):
            return self.format % d

        if  ms > 999:
            raise ValueError, 'milliseconds must be a integer between 0 and 999'

        d['ms'] = ms
        return self.format_ms % d


class gDateTime(Gregorian):
    '''A date and time.
    '''
    parselist = [ (None,'dateTime') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        '(?P<Y>\d{4,})-' r'(?P<M>\d\d)-' r'(?P<D>\d\d)' 'T' \
                        r'(?P<h>\d\d):' r'(?P<m>\d\d):' r'(?P<s>\d*(\.\d+)?)' \
                        r'(?P<tz>(Z|([-+]\d\d:\d\d))?)' '$')
    tag, format = 'dateTime', '%(Y)04d-%(M)02d-%(D)02dT%(h)02d:%(m)02d:%(s)02dZ'
    format_ms = format[:-1] + '.%(ms)03dZ'
    type = (SCHEMA.XSD3, 'dateTime')
    fix_timezone = True

class gDate(Gregorian):
    '''A date.
    '''
    parselist = [ (None,'date') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        '(?P<Y>\d{4,})-' r'(?P<M>\d\d)-' r'(?P<D>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'date', '%(Y)04d-%(M)02d-%(D)02d'
    type = (SCHEMA.XSD3, 'date')

class gYearMonth(Gregorian):
    '''A date.
    '''
    parselist = [ (None,'gYearMonth') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        '(?P<Y>\d{4,})-' r'(?P<M>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gYearMonth', '%(Y)04d-%(M)02d'
    type = (SCHEMA.XSD3, 'gYearMonth')

class gYear(Gregorian):
    '''A date.
    '''
    parselist = [ (None,'gYear') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        '(?P<Y>\d{4,})' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gYear', '%(Y)04d'
    type = (SCHEMA.XSD3, 'gYear')

class gMonthDay(Gregorian):
    '''A gMonthDay.
    '''
    parselist = [ (None,'gMonthDay') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        r'--(?P<M>\d\d)-' r'(?P<D>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gMonthDay', '--%(M)02d-%(D)02d'
    type = (SCHEMA.XSD3, 'gMonthDay')


class gDay(Gregorian):
    '''A gDay.
    '''
    parselist = [ (None,'gDay') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        r'---(?P<D>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gDay', '---%(D)02d'
    type = (SCHEMA.XSD3, 'gDay')

class gMonth(Gregorian):
    '''A gMonth.
    '''
    parselist = [ (None,'gMonth') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        r'--(?P<M>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gMonth', '--%(M)02d'
    type = (SCHEMA.XSD3, 'gMonth')

class gTime(Gregorian):
    '''A time.
    '''
    parselist = [ (None,'time') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        r'(?P<h>\d\d):' r'(?P<m>\d\d):' r'(?P<s>\d*(\.\d+)?)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'time', '%(h)02d:%(m)02d:%(s)02dZ'
    format_ms = format[:-1] + '.%(ms)03dZ'
    type = (SCHEMA.XSD3, 'time')
    fix_timezone = True

if __name__ == '__main__': print _copyright
