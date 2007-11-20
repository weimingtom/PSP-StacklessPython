# This script generates a Python interface for an Apple Macintosh Manager.
# It uses the "bgen" package to generate C code.
# The function specifications are generated by scanning the mamager's header file,
# using the "scantools" package (customized for this particular manager).
#
# XXXX TO DO:
# - Implement correct missing FSSpec handling for Alias methods
# - Implement FInfo

import string

# Declarations that change for each manager
#MACHEADERFILE = 'Files.h'              # The Apple header file
MODNAME = '_File'                               # The name of the module
LONGMODNAME = 'Carbon.File'             # The "normal" external name of the module

# The following is *usually* unchanged but may still require tuning
MODPREFIX = 'File'                      # The prefix for module-wide routines
INPUTFILE = string.lower(MODPREFIX) + 'gen.py' # The file generated by the scanner
OUTPUTFILE = MODNAME + "module.c"       # The file generated by this program

from macsupport import *

# Various integers:
SInt64 = Type("SInt64", "L")
UInt64 = Type("UInt64", "L")
FNMessage = Type("FNMessage", "l")
FSAllocationFlags = Type("FSAllocationFlags", "H")
FSCatalogInfoBitmap = Type("FSCatalogInfoBitmap", "l")
FSIteratorFlags = Type("FSIteratorFlags", "l")
FSVolumeRefNum = Type("FSVolumeRefNum", "h")
AliasInfoType = Type("AliasInfoType", "h")

# Various types of strings:
#class UniCharCountBuffer(InputOnlyType):
#       pass
class VarReverseInputBufferType(ReverseInputBufferMixin, VarInputBufferType):
    pass
FullPathName = VarReverseInputBufferType()
ConstStr31Param = OpaqueArrayType("Str31", "PyMac_BuildStr255", "PyMac_GetStr255")
ConstStr32Param = OpaqueArrayType("Str32", "PyMac_BuildStr255", "PyMac_GetStr255")
ConstStr63Param = OpaqueArrayType("Str63", "PyMac_BuildStr255", "PyMac_GetStr255")
Str63 = OpaqueArrayType("Str63", "PyMac_BuildStr255", "PyMac_GetStr255")

HFSUniStr255 = OpaqueType("HFSUniStr255", "PyMac_BuildHFSUniStr255", "PyMac_GetHFSUniStr255")
UInt8_ptr = InputOnlyType("UInt8 *", "s")

# Other types:
class OptionalFSxxxType(OpaqueByValueType):
    def declare(self, name):
        Output("%s %s__buf__;", self.typeName, name)
        Output("%s *%s = &%s__buf__;", self.typeName, name, name)

class FSCatalogInfoAndBitmapType(InputOnlyType):

    def __init__(self):
        InputOnlyType.__init__(self, "BUG", "BUG")

    def declare(self, name):
        Output("PyObject *%s__object = NULL;", name)
        Output("FSCatalogInfoBitmap %s__bitmap = 0;", name)
        Output("FSCatalogInfo %s;", name)

    def getargsFormat(self):
        return "lO"

    def getargsArgs(self, name):
        return "%s__bitmap, %s__object"%(name, name)

    def getargsCheck(self, name):
        Output("if (!convert_FSCatalogInfo(%s__object, %s__bitmap, &%s)) return NULL;", name, name, name)

    def passInput(self, name):
        return "%s__bitmap, &%s"% (name, name)

    def passOutput(self, name):
        return "%s__bitmap, &%s"% (name, name)

    def mkvalueFormat(self):
        return "O"

    def mkvalueArgs(self, name):
        return "%s__object" % (name)

    def xxxxmkvalueCheck(self, name):
        Output("if ((%s__object = new_FSCatalogInfo(%s__bitmap, &%s)) == NULL) return NULL;", name, name)

class FSCatalogInfoAndBitmap_inType(FSCatalogInfoAndBitmapType, InputOnlyMixIn):

    def xxxxmkvalueCheck(self, name):
        pass

class FSCatalogInfoAndBitmap_outType(FSCatalogInfoAndBitmapType):

    def getargsFormat(self):
        return "l"

    def getargsArgs(self, name):
        return "%s__bitmap" % name

    def getargsCheck(self, name):
        pass

FInfo = OpaqueType("FInfo", "FInfo")
FInfo_ptr = OpaqueType("FInfo", "FInfo")
AliasHandle = OpaqueByValueType("AliasHandle", "Alias")
FSSpec = OpaqueType("FSSpec", "FSSpec")
FSSpec_ptr = OpaqueType("FSSpec", "FSSpec")
OptFSSpecPtr = OptionalFSxxxType("FSSpec", "BUG", "myPyMac_GetOptFSSpecPtr")
FSRef = OpaqueType("FSRef", "FSRef")
FSRef_ptr = OpaqueType("FSRef", "FSRef")
OptFSRefPtr = OptionalFSxxxType("FSRef", "BUG", "myPyMac_GetOptFSRefPtr")
FSCatalogInfo = OpaqueType("FSCatalogInfo", "FSCatalogInfo")
FSCatalogInfo_ptr = OpaqueType("FSCatalogInfo", "FSCatalogInfo")

# To be done:
#CatPositionRec
#FSCatalogInfo
#FSForkInfo
#FSIterator
#FSVolumeInfo
#FSSpecArrayPtr

includestuff = includestuff + """
#include <Carbon/Carbon.h>

#ifdef USE_TOOLBOX_OBJECT_GLUE
extern int _PyMac_GetFSSpec(PyObject *v, FSSpec *spec);
extern int _PyMac_GetFSRef(PyObject *v, FSRef *fsr);
extern PyObject *_PyMac_BuildFSSpec(FSSpec *spec);
extern PyObject *_PyMac_BuildFSRef(FSRef *spec);

#define PyMac_GetFSSpec _PyMac_GetFSSpec
#define PyMac_GetFSRef _PyMac_GetFSRef
#define PyMac_BuildFSSpec _PyMac_BuildFSSpec
#define PyMac_BuildFSRef _PyMac_BuildFSRef
#else
extern int PyMac_GetFSSpec(PyObject *v, FSSpec *spec);
extern int PyMac_GetFSRef(PyObject *v, FSRef *fsr);
extern PyObject *PyMac_BuildFSSpec(FSSpec *spec);
extern PyObject *PyMac_BuildFSRef(FSRef *spec);
#endif

/* Forward declarations */
static PyObject *FInfo_New(FInfo *itself);
static PyObject *FSRef_New(FSRef *itself);
static PyObject *FSSpec_New(FSSpec *itself);
static PyObject *Alias_New(AliasHandle itself);
static int FInfo_Convert(PyObject *v, FInfo *p_itself);
#define FSRef_Convert PyMac_GetFSRef
#define FSSpec_Convert PyMac_GetFSSpec
static int Alias_Convert(PyObject *v, AliasHandle *p_itself);

/*
** UTCDateTime records
*/
static int
UTCDateTime_Convert(PyObject *v, UTCDateTime *ptr)
{
        return PyArg_Parse(v, "(HlH)", &ptr->highSeconds, &ptr->lowSeconds, &ptr->fraction);
}

static PyObject *
UTCDateTime_New(UTCDateTime *ptr)
{
        return Py_BuildValue("(HlH)", ptr->highSeconds, ptr->lowSeconds, ptr->fraction);
}

/*
** Optional fsspec and fsref pointers. None will pass NULL
*/
static int
myPyMac_GetOptFSSpecPtr(PyObject *v, FSSpec **spec)
{
        if (v == Py_None) {
                *spec = NULL;
                return 1;
        }
        return PyMac_GetFSSpec(v, *spec);
}

static int
myPyMac_GetOptFSRefPtr(PyObject *v, FSRef **ref)
{
        if (v == Py_None) {
                *ref = NULL;
                return 1;
        }
        return PyMac_GetFSRef(v, *ref);
}

/*
** Parse/generate objsect
*/
static PyObject *
PyMac_BuildHFSUniStr255(HFSUniStr255 *itself)
{

        return Py_BuildValue("u#", itself->unicode, itself->length);
}

/*
** Get pathname for a given FSSpec
*/
static OSErr
_PyMac_GetFullPathname(FSSpec *fss, char *path, int len)
{
        FSRef fsr;
        OSErr err;

        *path = '\0';
        err = FSpMakeFSRef(fss, &fsr);
        if (err == fnfErr) {
                /* FSSpecs can point to non-existing files, fsrefs can't. */
                FSSpec fss2;
                int tocopy;

                err = FSMakeFSSpec(fss->vRefNum, fss->parID, "", &fss2);
                if (err)
                        return err;
                err = FSpMakeFSRef(&fss2, &fsr);
                if (err)
                        return err;
                err = (OSErr)FSRefMakePath(&fsr, path, len-1);
                if (err)
                        return err;
                /* This part is not 100% safe: we append the filename part, but
                ** I'm not sure that we don't run afoul of the various 8bit
                ** encodings here. Will have to look this up at some point...
                */
                strcat(path, "/");
                tocopy = fss->name[0];
                if ((strlen(path) + tocopy) >= len)
                        tocopy = len - strlen(path) - 1;
                if (tocopy > 0)
                        strncat(path, fss->name+1, tocopy);
        }
        else {
                if (err)
                        return err;
                err = (OSErr)FSRefMakePath(&fsr, path, len);
                if (err)
                        return err;
        }
        return 0;
}

"""

finalstuff = finalstuff + """
int
PyMac_GetFSSpec(PyObject *v, FSSpec *spec)
{
        Str255 path;
        short refnum;
        long parid;
        OSErr err;
        FSRef fsr;

        if (FSSpec_Check(v)) {
                *spec = ((FSSpecObject *)v)->ob_itself;
                return 1;
        }

        if (PyArg_Parse(v, "(hlO&)",
                                                &refnum, &parid, PyMac_GetStr255, &path)) {
                err = FSMakeFSSpec(refnum, parid, path, spec);
                if ( err && err != fnfErr ) {
                        PyMac_Error(err);
                        return 0;
                }
                return 1;
        }
        PyErr_Clear();
        /* Otherwise we try to go via an FSRef. On OSX we go all the way,
        ** on OS9 we accept only a real FSRef object
        */
        if ( PyMac_GetFSRef(v, &fsr) ) {
                err = FSGetCatalogInfo(&fsr, kFSCatInfoNone, NULL, NULL, spec, NULL);
                if (err != noErr) {
                        PyMac_Error(err);
                        return 0;
                }
                return 1;
        }
        return 0;
}

int
PyMac_GetFSRef(PyObject *v, FSRef *fsr)
{
        OSStatus err;
        FSSpec fss;

        if (FSRef_Check(v)) {
                *fsr = ((FSRefObject *)v)->ob_itself;
                return 1;
        }

        /* On OSX we now try a pathname */
        if ( PyString_Check(v) || PyUnicode_Check(v)) {
                char *path = NULL;
                if (!PyArg_Parse(v, "et", Py_FileSystemDefaultEncoding, &path))
                        return 0;
                if ( (err=FSPathMakeRef(path, fsr, NULL)) )
                        PyMac_Error(err);
                PyMem_Free(path);
                return !err;
        }
        /* XXXX Should try unicode here too */
        /* Otherwise we try to go via an FSSpec */
        if (FSSpec_Check(v)) {
                fss = ((FSSpecObject *)v)->ob_itself;
                if ((err=FSpMakeFSRef(&fss, fsr)) == 0)
                        return 1;
                PyMac_Error(err);
                return 0;
        }
        PyErr_SetString(PyExc_TypeError, "FSRef, FSSpec or pathname required");
        return 0;
}

extern PyObject *
PyMac_BuildFSSpec(FSSpec *spec)
{
        return FSSpec_New(spec);
}

extern PyObject *
PyMac_BuildFSRef(FSRef *spec)
{
        return FSRef_New(spec);
}
"""

initstuff = initstuff + """
PyMac_INIT_TOOLBOX_OBJECT_NEW(FSSpec *, PyMac_BuildFSSpec);
PyMac_INIT_TOOLBOX_OBJECT_NEW(FSRef *, PyMac_BuildFSRef);
PyMac_INIT_TOOLBOX_OBJECT_CONVERT(FSSpec, PyMac_GetFSSpec);
PyMac_INIT_TOOLBOX_OBJECT_CONVERT(FSRef, PyMac_GetFSRef);
"""

execfile(string.lower(MODPREFIX) + 'typetest.py')

# Our object types:
class FSCatalogInfoDefinition(PEP253Mixin, ObjectDefinition):
    getsetlist = [
            ("nodeFlags",
             "return Py_BuildValue(\"H\", self->ob_itself.nodeFlags);",
             "return PyArg_Parse(v, \"H\", &self->ob_itself.nodeFlags)-1;",
             None
            ),
            ("volume",
             "return Py_BuildValue(\"h\", self->ob_itself.volume);",
             "return PyArg_Parse(v, \"h\", &self->ob_itself.volume)-1;",
             None
            ),
            ("parentDirID",
             "return Py_BuildValue(\"l\", self->ob_itself.parentDirID);",
             "return PyArg_Parse(v, \"l\", &self->ob_itself.parentDirID)-1;",
             None
            ),
            ("nodeID",
             "return Py_BuildValue(\"l\", self->ob_itself.nodeID);",
             "return PyArg_Parse(v, \"l\", &self->ob_itself.nodeID)-1;",
             None
            ),
            ("createDate",
             "return Py_BuildValue(\"O&\", UTCDateTime_New, &self->ob_itself.createDate);",
             "return PyArg_Parse(v, \"O&\", UTCDateTime_Convert, &self->ob_itself.createDate)-1;",
             None
            ),
            ("contentModDate",
             "return Py_BuildValue(\"O&\", UTCDateTime_New, &self->ob_itself.contentModDate);",
             "return PyArg_Parse(v, \"O&\", UTCDateTime_Convert, &self->ob_itself.contentModDate)-1;",
             None
            ),
            ("attributeModDate",
             "return Py_BuildValue(\"O&\", UTCDateTime_New, &self->ob_itself.attributeModDate);",
             "return PyArg_Parse(v, \"O&\", UTCDateTime_Convert, &self->ob_itself.attributeModDate)-1;",
             None
            ),
            ("accessDate",
             "return Py_BuildValue(\"O&\", UTCDateTime_New, &self->ob_itself.accessDate);",
             "return PyArg_Parse(v, \"O&\", UTCDateTime_Convert, &self->ob_itself.accessDate)-1;",
             None
            ),
            ("backupDate",
             "return Py_BuildValue(\"O&\", UTCDateTime_New, &self->ob_itself.backupDate);",
             "return PyArg_Parse(v, \"O&\", UTCDateTime_Convert, &self->ob_itself.backupDate)-1;",
             None
            ),
            ("permissions",
             "return Py_BuildValue(\"(llll)\", self->ob_itself.permissions[0], self->ob_itself.permissions[1], self->ob_itself.permissions[2], self->ob_itself.permissions[3]);",
             "return PyArg_Parse(v, \"(llll)\", &self->ob_itself.permissions[0], &self->ob_itself.permissions[1], &self->ob_itself.permissions[2], &self->ob_itself.permissions[3])-1;",
             None
            ),
            # XXXX FinderInfo TBD
            # XXXX FinderXInfo TBD
            ("valence",
             "return Py_BuildValue(\"l\", self->ob_itself.valence);",
             "return PyArg_Parse(v, \"l\", &self->ob_itself.valence)-1;",
             None
            ),
            ("dataLogicalSize",
             "return Py_BuildValue(\"l\", self->ob_itself.dataLogicalSize);",
             "return PyArg_Parse(v, \"l\", &self->ob_itself.dataLogicalSize)-1;",
             None
            ),
            ("dataPhysicalSize",
             "return Py_BuildValue(\"l\", self->ob_itself.dataPhysicalSize);",
             "return PyArg_Parse(v, \"l\", &self->ob_itself.dataPhysicalSize)-1;",
             None
            ),
            ("rsrcLogicalSize",
             "return Py_BuildValue(\"l\", self->ob_itself.rsrcLogicalSize);",
             "return PyArg_Parse(v, \"l\", &self->ob_itself.rsrcLogicalSize)-1;",
             None
            ),
            ("rsrcPhysicalSize",
             "return Py_BuildValue(\"l\", self->ob_itself.rsrcPhysicalSize);",
             "return PyArg_Parse(v, \"l\", &self->ob_itself.rsrcPhysicalSize)-1;",
             None
            ),
            ("sharingFlags",
             "return Py_BuildValue(\"l\", self->ob_itself.sharingFlags);",
             "return PyArg_Parse(v, \"l\", &self->ob_itself.sharingFlags)-1;",
             None
            ),
            ("userPrivileges",
             "return Py_BuildValue(\"b\", self->ob_itself.userPrivileges);",
             "return PyArg_Parse(v, \"b\", &self->ob_itself.userPrivileges)-1;",
             None
            ),
    ]
    # The same info, but in a different form
    INITFORMAT = "HhllO&O&O&O&O&llllllb"
    INITARGS = """&((FSCatalogInfoObject *)_self)->ob_itself.nodeFlags,
            &((FSCatalogInfoObject *)_self)->ob_itself.volume,
            &((FSCatalogInfoObject *)_self)->ob_itself.parentDirID,
            &((FSCatalogInfoObject *)_self)->ob_itself.nodeID,
            UTCDateTime_Convert, &((FSCatalogInfoObject *)_self)->ob_itself.createDate,
            UTCDateTime_Convert, &((FSCatalogInfoObject *)_self)->ob_itself.contentModDate,
            UTCDateTime_Convert, &((FSCatalogInfoObject *)_self)->ob_itself.attributeModDate,
            UTCDateTime_Convert, &((FSCatalogInfoObject *)_self)->ob_itself.accessDate,
            UTCDateTime_Convert, &((FSCatalogInfoObject *)_self)->ob_itself.backupDate,
            &((FSCatalogInfoObject *)_self)->ob_itself.valence,
            &((FSCatalogInfoObject *)_self)->ob_itself.dataLogicalSize,
            &((FSCatalogInfoObject *)_self)->ob_itself.dataPhysicalSize,
            &((FSCatalogInfoObject *)_self)->ob_itself.rsrcLogicalSize,
            &((FSCatalogInfoObject *)_self)->ob_itself.rsrcPhysicalSize,
            &((FSCatalogInfoObject *)_self)->ob_itself.sharingFlags,
            &((FSCatalogInfoObject *)_self)->ob_itself.userPrivileges"""
    INITNAMES = """
            "nodeFlags",
            "volume",
            "parentDirID",
            "nodeID",
            "createDate",
            "contentModDate",
            "atributeModDate",
            "accessDate",
            "backupDate",
            "valence",
            "dataLogicalSize",
            "dataPhysicalSize",
            "rsrcLogicalSize",
            "rsrcPhysicalSize",
            "sharingFlags",
            "userPrivileges"
            """

    def __init__(self, name, prefix, itselftype):
        ObjectDefinition.__init__(self, name, prefix, itselftype)
        self.argref = "*"       # Store FSSpecs, but pass them by address

    def outputCheckNewArg(self):
        Output("if (itself == NULL) { Py_INCREF(Py_None); return Py_None; }")

    def output_tp_newBody(self):
        Output("PyObject *self;");
        Output()
        Output("if ((self = type->tp_alloc(type, 0)) == NULL) return NULL;")
        Output("memset(&((%s *)self)->ob_itself, 0, sizeof(%s));",
                self.objecttype, self.itselftype)
        Output("return self;")

    def output_tp_initBody(self):
        Output("static char *kw[] = {%s, 0};", self.INITNAMES)
        Output()
        Output("if (!PyArg_ParseTupleAndKeywords(_args, _kwds, \"|%s\", kw, %s))",
                self.INITFORMAT, self.INITARGS)
        OutLbrace()
        Output("return -1;")
        OutRbrace()
        Output("return 0;")

class FInfoDefinition(PEP253Mixin, ObjectDefinition):
    getsetlist = [
            ("Type",
             "return Py_BuildValue(\"O&\", PyMac_BuildOSType, self->ob_itself.fdType);",
             "return PyArg_Parse(v, \"O&\", PyMac_GetOSType, &self->ob_itself.fdType)-1;",
             "4-char file type"
            ),
            ("Creator",
             "return Py_BuildValue(\"O&\", PyMac_BuildOSType, self->ob_itself.fdCreator);",
             "return PyArg_Parse(v, \"O&\", PyMac_GetOSType, &self->ob_itself.fdCreator)-1;",
             "4-char file creator"
            ),
            ("Flags",
             "return Py_BuildValue(\"H\", self->ob_itself.fdFlags);",
             "return PyArg_Parse(v, \"H\", &self->ob_itself.fdFlags)-1;",
             "Finder flag bits"
            ),
            ("Location",
             "return Py_BuildValue(\"O&\", PyMac_BuildPoint, self->ob_itself.fdLocation);",
             "return PyArg_Parse(v, \"O&\", PyMac_GetPoint, &self->ob_itself.fdLocation)-1;",
             "(x, y) location of the file's icon in its parent finder window"
            ),
            ("Fldr",
             "return Py_BuildValue(\"h\", self->ob_itself.fdFldr);",
             "return PyArg_Parse(v, \"h\", &self->ob_itself.fdFldr)-1;",
             "Original folder, for 'put away'"
            ),

    ]

    def __init__(self, name, prefix, itselftype):
        ObjectDefinition.__init__(self, name, prefix, itselftype)
        self.argref = "*"       # Store FSSpecs, but pass them by address

    def outputCheckNewArg(self):
        Output("if (itself == NULL) return PyMac_Error(resNotFound);")

    def output_tp_newBody(self):
        Output("PyObject *self;");
        Output()
        Output("if ((self = type->tp_alloc(type, 0)) == NULL) return NULL;")
        Output("memset(&((%s *)self)->ob_itself, 0, sizeof(%s));",
                self.objecttype, self.itselftype)
        Output("return self;")

    def output_tp_initBody(self):
        Output("%s *itself = NULL;", self.itselftype)
        Output("static char *kw[] = {\"itself\", 0};")
        Output()
        Output("if (PyArg_ParseTupleAndKeywords(_args, _kwds, \"|O&\", kw, FInfo_Convert, &itself))")
        OutLbrace()
        Output("if (itself) memcpy(&((%s *)_self)->ob_itself, itself, sizeof(%s));",
                self.objecttype, self.itselftype)
        Output("return 0;")
        OutRbrace()
        Output("return -1;")

class FSSpecDefinition(PEP253Mixin, ObjectDefinition):
    getsetlist = [
            ("data",
             "return PyString_FromStringAndSize((char *)&self->ob_itself, sizeof(self->ob_itself));",
             None,
             "Raw data of the FSSpec object"
            )
    ]

    def __init__(self, name, prefix, itselftype):
        ObjectDefinition.__init__(self, name, prefix, itselftype)
        self.argref = "*"       # Store FSSpecs, but pass them by address

    def outputCheckNewArg(self):
        Output("if (itself == NULL) return PyMac_Error(resNotFound);")

    # We do Convert ourselves (with PyMac_GetFSxxx)
    def outputConvert(self):
        pass

    def output_tp_newBody(self):
        Output("PyObject *self;");
        Output()
        Output("if ((self = type->tp_alloc(type, 0)) == NULL) return NULL;")
        Output("memset(&((%s *)self)->ob_itself, 0, sizeof(%s));",
                self.objecttype, self.itselftype)
        Output("return self;")

    def output_tp_initBody(self):
        Output("PyObject *v = NULL;")
        Output("char *rawdata = NULL;")
        Output("int rawdatalen = 0;")
        Output("static char *kw[] = {\"itself\", \"rawdata\", 0};")
        Output()
        Output("if (!PyArg_ParseTupleAndKeywords(_args, _kwds, \"|Os#\", kw, &v, &rawdata, &rawdatalen))")
        Output("return -1;")
        Output("if (v && rawdata)")
        OutLbrace()
        Output("PyErr_SetString(PyExc_TypeError, \"Only one of itself or rawdata may be specified\");")
        Output("return -1;")
        OutRbrace()
        Output("if (!v && !rawdata)")
        OutLbrace()
        Output("PyErr_SetString(PyExc_TypeError, \"One of itself or rawdata must be specified\");")
        Output("return -1;")
        OutRbrace()
        Output("if (rawdata)")
        OutLbrace()
        Output("if (rawdatalen != sizeof(%s))", self.itselftype)
        OutLbrace()
        Output("PyErr_SetString(PyExc_TypeError, \"%s rawdata incorrect size\");",
                self.itselftype)
        Output("return -1;")
        OutRbrace()
        Output("memcpy(&((%s *)_self)->ob_itself, rawdata, rawdatalen);", self.objecttype)
        Output("return 0;")
        OutRbrace()
        Output("if (PyMac_GetFSSpec(v, &((%s *)_self)->ob_itself)) return 0;", self.objecttype)
        Output("return -1;")

    def outputRepr(self):
        Output()
        Output("static PyObject * %s_repr(%s *self)", self.prefix, self.objecttype)
        OutLbrace()
        Output("char buf[512];")
        Output("""PyOS_snprintf(buf, sizeof(buf), \"%%s((%%d, %%ld, '%%.*s'))\",
        self->ob_type->tp_name,
        self->ob_itself.vRefNum,
        self->ob_itself.parID,
        self->ob_itself.name[0], self->ob_itself.name+1);""")
        Output("return PyString_FromString(buf);")
        OutRbrace()

class FSRefDefinition(PEP253Mixin, ObjectDefinition):
    getsetlist = [
            ("data",
             "return PyString_FromStringAndSize((char *)&self->ob_itself, sizeof(self->ob_itself));",
             None,
             "Raw data of the FSRef object"
            )
    ]

    def __init__(self, name, prefix, itselftype):
        ObjectDefinition.__init__(self, name, prefix, itselftype)
        self.argref = "*"       # Store FSRefs, but pass them by address

    def outputCheckNewArg(self):
        Output("if (itself == NULL) return PyMac_Error(resNotFound);")

    # We do Convert ourselves (with PyMac_GetFSxxx)
    def outputConvert(self):
        pass

    def output_tp_newBody(self):
        Output("PyObject *self;");
        Output()
        Output("if ((self = type->tp_alloc(type, 0)) == NULL) return NULL;")
        Output("memset(&((%s *)self)->ob_itself, 0, sizeof(%s));",
                self.objecttype, self.itselftype)
        Output("return self;")

    def output_tp_initBody(self):
        Output("PyObject *v = NULL;")
        Output("char *rawdata = NULL;")
        Output("int rawdatalen = 0;")
        Output("static char *kw[] = {\"itself\", \"rawdata\", 0};")
        Output()
        Output("if (!PyArg_ParseTupleAndKeywords(_args, _kwds, \"|Os#\", kw, &v, &rawdata, &rawdatalen))")
        Output("return -1;")
        Output("if (v && rawdata)")
        OutLbrace()
        Output("PyErr_SetString(PyExc_TypeError, \"Only one of itself or rawdata may be specified\");")
        Output("return -1;")
        OutRbrace()
        Output("if (!v && !rawdata)")
        OutLbrace()
        Output("PyErr_SetString(PyExc_TypeError, \"One of itself or rawdata must be specified\");")
        Output("return -1;")
        OutRbrace()
        Output("if (rawdata)")
        OutLbrace()
        Output("if (rawdatalen != sizeof(%s))", self.itselftype)
        OutLbrace()
        Output("PyErr_SetString(PyExc_TypeError, \"%s rawdata incorrect size\");",
                self.itselftype)
        Output("return -1;")
        OutRbrace()
        Output("memcpy(&((%s *)_self)->ob_itself, rawdata, rawdatalen);", self.objecttype)
        Output("return 0;")
        OutRbrace()
        Output("if (PyMac_GetFSRef(v, &((%s *)_self)->ob_itself)) return 0;", self.objecttype)
        Output("return -1;")

class AliasDefinition(PEP253Mixin, ObjectDefinition):
    # XXXX Should inherit from resource?
    getsetlist = [
            ("data",
             """int size;
                    PyObject *rv;

                    size = GetHandleSize((Handle)self->ob_itself);
                    HLock((Handle)self->ob_itself);
                    rv = PyString_FromStringAndSize(*(Handle)self->ob_itself, size);
                    HUnlock((Handle)self->ob_itself);
                    return rv;
            """,
             None,
             "Raw data of the alias object"
            )
    ]

    def outputCheckNewArg(self):
        Output("if (itself == NULL) return PyMac_Error(resNotFound);")

    def outputStructMembers(self):
        ObjectDefinition.outputStructMembers(self)
        Output("void (*ob_freeit)(%s ptr);", self.itselftype)

    def outputInitStructMembers(self):
        ObjectDefinition.outputInitStructMembers(self)
        Output("it->ob_freeit = NULL;")

    def outputCleanupStructMembers(self):
        Output("if (self->ob_freeit && self->ob_itself)")
        OutLbrace()
        Output("self->ob_freeit(self->ob_itself);")
        OutRbrace()
        Output("self->ob_itself = NULL;")

    def output_tp_newBody(self):
        Output("PyObject *self;");
        Output()
        Output("if ((self = type->tp_alloc(type, 0)) == NULL) return NULL;")
        Output("((%s *)self)->ob_itself = NULL;", self.objecttype)
        Output("return self;")

    def output_tp_initBody(self):
        Output("%s itself = NULL;", self.itselftype)
        Output("char *rawdata = NULL;")
        Output("int rawdatalen = 0;")
        Output("Handle h;")
        Output("static char *kw[] = {\"itself\", \"rawdata\", 0};")
        Output()
        Output("if (!PyArg_ParseTupleAndKeywords(_args, _kwds, \"|O&s#\", kw, %s_Convert, &itself, &rawdata, &rawdatalen))",
                self.prefix)
        Output("return -1;")
        Output("if (itself && rawdata)")
        OutLbrace()
        Output("PyErr_SetString(PyExc_TypeError, \"Only one of itself or rawdata may be specified\");")
        Output("return -1;")
        OutRbrace()
        Output("if (!itself && !rawdata)")
        OutLbrace()
        Output("PyErr_SetString(PyExc_TypeError, \"One of itself or rawdata must be specified\");")
        Output("return -1;")
        OutRbrace()
        Output("if (rawdata)")
        OutLbrace()
        Output("if ((h = NewHandle(rawdatalen)) == NULL)")
        OutLbrace()
        Output("PyErr_NoMemory();")
        Output("return -1;")
        OutRbrace()
        Output("HLock(h);")
        Output("memcpy((char *)*h, rawdata, rawdatalen);")
        Output("HUnlock(h);")
        Output("((%s *)_self)->ob_itself = (%s)h;", self.objecttype, self.itselftype)
        Output("return 0;")
        OutRbrace()
        Output("((%s *)_self)->ob_itself = itself;", self.objecttype)
        Output("return 0;")

# Alias methods come in two flavors: those with the alias as arg1 and
# those with the alias as arg 2.
class Arg2MethodGenerator(OSErrMethodGenerator):
    """Similar to MethodGenerator, but has self as second argument"""

    def parseArgumentList(self, args):
        args0, arg1, argsrest = args[:1], args[1], args[2:]
        t0, n0, m0 = arg1
        args = args0 + argsrest
        if m0 != InMode:
            raise ValueError, "method's 'self' must be 'InMode'"
        self.itself = Variable(t0, "_self->ob_itself", SelfMode)
        FunctionGenerator.parseArgumentList(self, args)
        self.argumentList.insert(2, self.itself)

# From here on it's basically all boiler plate...

# Create the generator groups and link them
module = MacModule(MODNAME, MODPREFIX, includestuff, finalstuff, initstuff,
        longname=LONGMODNAME)

fscataloginfoobject = FSCatalogInfoDefinition('FSCatalogInfo', 'FSCatalogInfo', 'FSCatalogInfo')
finfoobject = FInfoDefinition('FInfo', 'FInfo', 'FInfo')
aliasobject = AliasDefinition('Alias', 'Alias', 'AliasHandle')
fsspecobject = FSSpecDefinition('FSSpec', 'FSSpec', 'FSSpec')
fsrefobject = FSRefDefinition('FSRef', 'FSRef', 'FSRef')

module.addobject(fscataloginfoobject)
module.addobject(finfoobject)
module.addobject(aliasobject)
module.addobject(fsspecobject)
module.addobject(fsrefobject)

# Create the generator classes used to populate the lists
Function = OSErrFunctionGenerator
Method = OSErrMethodGenerator

# Create and populate the lists
functions = []
alias_methods = []
fsref_methods = []
fsspec_methods = []
execfile(INPUTFILE)

# Manual generators:
FSRefMakePath_body = """
OSStatus _err;
#define MAXPATHNAME 1024
UInt8 path[MAXPATHNAME];
UInt32 maxPathSize = MAXPATHNAME;

if (!PyArg_ParseTuple(_args, ""))
        return NULL;
_err = FSRefMakePath(&_self->ob_itself,
                                         path,
                                         maxPathSize);
if (_err != noErr) return PyMac_Error(_err);
_res = Py_BuildValue("s", path);
return _res;
"""
f = ManualGenerator("FSRefMakePath", FSRefMakePath_body)
f.docstring = lambda: "() -> string"
fsref_methods.append(f)

FSRef_as_pathname_body = """
if (!PyArg_ParseTuple(_args, ""))
        return NULL;
_res = FSRef_FSRefMakePath(_self, _args);
return _res;
"""
f = ManualGenerator("as_pathname", FSRef_as_pathname_body)
f.docstring = lambda: "() -> string"
fsref_methods.append(f)

FSSpec_as_pathname_body = """
char strbuf[1024];
OSErr err;

if (!PyArg_ParseTuple(_args, ""))
        return NULL;
err = _PyMac_GetFullPathname(&_self->ob_itself, strbuf, sizeof(strbuf));
if ( err ) {
        PyMac_Error(err);
        return NULL;
}
_res = PyString_FromString(strbuf);
return _res;
"""
f = ManualGenerator("as_pathname", FSSpec_as_pathname_body)
f.docstring = lambda: "() -> string"
fsspec_methods.append(f)

FSSpec_as_tuple_body = """
if (!PyArg_ParseTuple(_args, ""))
        return NULL;
_res = Py_BuildValue("(iis#)", _self->ob_itself.vRefNum, _self->ob_itself.parID,
                                        &_self->ob_itself.name[1], _self->ob_itself.name[0]);
return _res;
"""
f = ManualGenerator("as_tuple", FSSpec_as_tuple_body)
f.docstring = lambda: "() -> (vRefNum, dirID, name)"
fsspec_methods.append(f)

pathname_body = """
PyObject *obj;

if (!PyArg_ParseTuple(_args, "O", &obj))
        return NULL;
if (PyString_Check(obj)) {
        Py_INCREF(obj);
        return obj;
}
if (PyUnicode_Check(obj))
        return PyUnicode_AsEncodedString(obj, "utf8", "strict");
_res = PyObject_CallMethod(obj, "as_pathname", NULL);
return _res;
"""
f = ManualGenerator("pathname", pathname_body)
f.docstring = lambda: "(str|unicode|FSSpec|FSref) -> pathname"
functions.append(f)

# add the populated lists to the generator groups
# (in a different wordl the scan program would generate this)
for f in functions: module.add(f)
for f in alias_methods: aliasobject.add(f)
for f in fsspec_methods: fsspecobject.add(f)
for f in fsref_methods: fsrefobject.add(f)

# generate output (open the output file as late as possible)
SetOutputFileName(OUTPUTFILE)
module.generate()
