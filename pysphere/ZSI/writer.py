#! /usr/bin/env python
# $Id$
'''SOAP message serialization.
'''

from pysphere.ZSI import _copyright, _get_idstr, ZSI_SCHEMA_URI
from pysphere.ZSI import _backtrace, _stringtypes, _seqtypes
from pysphere.ZSI.wstools.Utility import MessageInterface, ElementProxy
from pysphere.ZSI.wstools.Namespaces import XMLNS, SOAP, SCHEMA
from pysphere.ZSI.wstools.c14n import Canonicalize
from pysphere.ZSI.wstools.MIMEAttachment import MIMEMessage

import types

_standard_ns = [ ('xml', XMLNS.XML), ('xmlns', XMLNS.BASE) ]

_reserved_ns = {
        'soapenv': SOAP.ENV,
        'soapenc': SOAP.ENC,
        'ZSI': ZSI_SCHEMA_URI,
        'xsd': SCHEMA.BASE,
        'xsi': SCHEMA.BASE + '-instance',
}

class SoapWriter:
    '''SOAP output formatter.
       Instance Data:
           memo -- memory for id/href
           envelope -- add Envelope?
           encodingStyle --
           header -- add SOAP Header?
           outputclass -- ElementProxy class.
    '''

    def __init__(self, envelope=True, encodingStyle=None, header=True,
    nsdict={}, outputclass=None, **kw):
        '''Initialize.
        '''
        outputclass = outputclass or ElementProxy
        if not issubclass(outputclass, MessageInterface):
            raise TypeError, 'outputclass must subclass MessageInterface'

        self.dom, self.memo, self.nsdict= \
            outputclass(self), [], nsdict
        self.envelope = envelope
        self.encodingStyle = encodingStyle
        self.header = header
        self.body = None
        self.callbacks = []
        self.closed = False
        self._attachments = []
        self._MIMEBoundary = ""
        self._startCID = ""

    def __str__(self):
        self.close()
        if len(self._attachments) == 0:
            #we have no attachment let's return the SOAP message
            return str(self.dom)
        else:
            #we have some files to attach let's create the MIME message
            #first part the SOAP message
            msg = MIMEMessage()
            msg.addXMLMessage(str(self.dom))
            for file in self._attachments:
                msg.attachFile(file)
            msg.makeBoundary()
            self._MIMEBoundary = msg.getBoundary()
            self._startCID = msg.getStartCID()
            return msg.toString()

    def getMIMEBoundary(self):
        #return the httpHeader if any
        return self._MIMEBoundary

    def getStartCID(self):
        #return the CID of the xml part
        return self._startCID


    def getSOAPHeader(self):
        if self.header in (True, False):
            return None
        return self.header

    def serialize_header(self, pyobj, typecode=None, **kw):
        '''Serialize a Python object in soapenv:Header, make
        sure everything in Header unique (no #href).  Must call
        serialize first to create a document.

        Parameters:
            pyobjs -- instances to serialize in SOAP Header
            typecode -- default typecode
        '''
        kw['unique'] = True
        soap_env = _reserved_ns['soapenv']
        #header = self.dom.getElement(soap_env, 'Header')
        header = self._header
        if header is None:
            header = self._header = self.dom.createAppendElement(soap_env,
                                                                 'Header')

        typecode = getattr(pyobj, 'typecode', typecode)
        if typecode is None:
            raise RuntimeError(
                   'typecode is required to serialize pyobj in header')

        helt = typecode.serialize(header, self, pyobj, **kw)

    def serialize(self, pyobj, typecode=None, root=None, header_pyobjs=(), **kw):
        '''Serialize a Python object to the output stream.
           pyobj -- python instance to serialize in body.
           typecode -- typecode describing body
           root -- soapenc:root
           header_pyobjs -- list of pyobj for soap header inclusion, each
              instance must specify the typecode attribute.
        '''
        self.body = None
        if self.envelope:
            soap_env = _reserved_ns['soapenv']
            self.dom.createDocument(soap_env, 'Envelope')
            for prefix, nsuri in _reserved_ns.items():
                self.dom.setNamespaceAttribute(prefix, nsuri)
            self.writeNSdict(self.nsdict)
            if self.encodingStyle:
                self.dom.setAttributeNS(soap_env, 'encodingStyle',
                                        self.encodingStyle)
            if self.header:
                self._header = self.dom.createAppendElement(soap_env, 'Header')

                for h in header_pyobjs:
                    self.serialize_header(h, **kw)

            self.body = self.dom.createAppendElement(soap_env, 'Body')
        else:
            self.dom.createDocument(None,None)

        if typecode is None:
            typecode = pyobj.__class__.typecode

        if self.body is None:
            elt = typecode.serialize(self.dom, self, pyobj, **kw)
        else:
            elt = typecode.serialize(self.body, self, pyobj, **kw)

        if root is not None:
            if root not in [ 0, 1 ]:
                raise ValueError, "soapenc root attribute not in [0,1]"
            elt.setAttributeNS(SOAP.ENC, 'root', root)

        return self

    def writeNSdict(self, nsdict):
        '''Write a namespace dictionary, taking care to not clobber the
        standard (or reserved by us) prefixes.
        '''
        for k,v in nsdict.items():
            if (k,v) in _standard_ns: continue
            rv = _reserved_ns.get(k)
            if rv:
                if rv != v:
                    raise KeyError("Reserved namespace " + str((k,v)) + " used")
                continue
            if k:
                self.dom.setNamespaceAttribute(k, v)
            else:
                self.dom.setNamespaceAttribute('xmlns', v)


    def ReservedNS(self, prefix, uri):
        '''Is this namespace (prefix,uri) reserved by us?
        '''
        return _reserved_ns.get(prefix, uri) != uri

    def AddCallback(self, func, *arglist):
        '''Add a callback function and argument list to be invoked before
        closing off the SOAP Body.
        '''
        self.callbacks.append((func, arglist))

    def Known(self, obj):
        '''Seen this object (known by its id()?  Return 1 if so,
        otherwise add it to our memory and return 0.
        '''
        obj = _get_idstr(obj)
        if obj in self.memo: return 1
        self.memo.append(obj)
        return 0

    def Forget(self, obj):
        '''Forget we've seen this object.
        '''
        obj = _get_idstr(obj)
        try:
            self.memo.remove(obj)
        except ValueError:
            pass

    def Backtrace(self, elt):
        '''Return a human-readable "backtrace" from the document root to
        the specified element.
        '''
        return _backtrace(elt._getNode(), self.dom._getNode())


    def addAttachment(self, fileDesc):
        '''This function add an attachment to the SaopMessage
        '''
        self._attachments.append(fileDesc)

    def close(self):
        '''Invoke all the callbacks, and close off the SOAP message.
        '''
        if self.closed: return
        for func,arglist in self.callbacks:
            apply(func, arglist)
        self.closed = True

    def __del__(self):
        if not self.closed: self.close()


if __name__ == '__main__': print _copyright
