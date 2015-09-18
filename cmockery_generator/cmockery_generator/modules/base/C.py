from pycparser import c_parser as c, c_generator, c_ast , parse_file
from pycparser.c_ast import TypeDecl, PtrDecl , IdentifierType, FuncDecl
import os
from ntpath import basename
class param(object):
    types = []
    @property
    def Type(self):
        return self.types
    @Type.setter
    def Type(self,types):
        for type in types:
            self.types.append(type)
    name = ""
    @property
    def Name(self):
        return self.name
    @Name.setter
    def Name(self,value):
        self.name = value
    def __init__(self, *args, **kwargs):
        super(param, self).__init__(*args, **kwargs)
        self.types = []

class function(param):
    __args__ = []
    @property
    def Args(self):
        return self.__args__
    
    @Args.setter
    def Args(self , val):
        self.__args__ = val

    __line__ = ""
    @property
    def Line(self):
        return self.__line__

    __file__ = ""
    @property
    def File(self):
        return self.__file__

    __depend__ = []
    @property
    def Dependence(self):
        return self.__depend__
    
    __mock__ = False
    @property
    def Mock(self):
        return self.__mock__
    @Mock.setter
    def Mock(self,val):
        self.__mock__ = val

    def _build_params(self, node):
        try:
            params = node.type.args
            if params is None:
                return
            for param_obj in params.params:
                arg = param()
                arg.Name = param_obj.name
                self._recurive_search(param_obj.type , arg )
                self.Args.append(arg)
            return
        except:
            pass

    def _initialize(self, node):
        self.types = []
        self.__depend__ = []
        self.__args__ = []
        self._recurive_search(node,self)
        self.__line__ = str(node.coord.line)
        
        filename = basename(node.coord.file)
        self.__file__ = str(filename)
        self.Name = node.name

    def __init__(self, node , *args, **kwargs):
        super(function, self).__init__(*args, **kwargs)
        self._initialize(node)
        return self._build_params(node)
    
    def _recurive_search(self,obj , arg ):
        try:
            if(type(obj) is PtrDecl):
                obj.type.type.names.append("*")
                return self._recurive_search(obj.type , arg )
            if type(obj) is TypeDecl and len(obj.quals) > 0:
                arr = [x for x in obj.quals]
                for val in obj.type.names:
                    arr.append(val)
                obj.type.names = arr
                return self._recurive_search(obj.type , arg )
            if type(obj) is not IdentifierType:
                return self._recurive_search(obj.type , arg )
            arg.Type = obj.names
        except:
            pass

class FuncCallVisitor(c_ast.NodeVisitor):
    __func__ = None
    Files = []
    def __init__(self, func ):
        self.__func__ = func
    def visit_FuncCall(self, node):
        #print('%s ' % ( node.name.name ))
        for file in self.Files:
            for key,value in self.__func__[file].iteritems() : 
                if node.name.name == value.Name :
                    #print('%s called at %s' % (value.Name, node.name.coord))
                    value.Dependence.append(value)
                    value.Mock = True

class DeclVisitor(c_ast.NodeVisitor):
    _search_dir =[]
    __func__ = []
    files = {}
    @property
    def functions(self):
        return self.__func__
    def __init__(self , search):
        self._search_dir = search
        pass
    def in_search_rulse(self, node):
        filename = basename(node.coord.file)
        if self.files.has_key(filename):
            return True
        for dir in self._search_dir:
            file = ""
            for file in os.listdir(dir):
                if file == filename:
                    self.files[file] = ""
                    return True
        return False

    def visit_Decl(self, node):
        #print('%s ' % (node.name))
        if self.in_search_rulse(node) is False:
            return
        if type(node.type) is not FuncDecl:
            return
        func = function(node)
        self.__func__.append(func)
class FuncDefVisitor(c_ast.NodeVisitor):
    __func__ = []
    @property
    def functions(self):
        return self.__func__
    def __init__(self):
        pass
    def visit_FuncDef(self, node):
        #print('%s at %s' % (node.decl.name, node.decl.coord))
        func = function(node.decl)
        self.__func__.append(func)
class functions(object):
    _cpp = None
    _files = []
    __map__ = {}
    @property
    def map(self):
        return self.__map__
    
    def _in_search_rules(self, func ):
        if func.File.endswith(".h") is False:
            return True
        if func.File in self._files:
            return True
        
        for file in self._cpp.skip:
            if file == func.File:
                return False

        for dir in self._cpp.search_dir:
            file = ""
            for file in os.listdir(dir):
                if file == func.File:
                    self._files.append(file)               
                    return True
        return False
    def __init__(self, ast , cpp = None ,*args, **kwargs):
        super(functions, self).__init__(*args, **kwargs)
        self._files = []
        self._cpp = None if cpp is None else cpp
        funcs = DeclVisitor(cpp.search_dir)
        funcs.visit(ast)
        for func in funcs.functions:
            if self._in_search_rules(func) is not True:
                continue
            if self.map.has_key(func.File) is not True:
                self.map[func.File] = {}
            self.map[func.File][func.Line] = func

        depend = FuncCallVisitor(self.map)
        depend.Files = self._files
        depend.visit(ast)

class CppArgs(object):
    __slots__ = ('includes', 'src', 'search_dir', 'skip')
    def __init__(self, *args, **kwargs):
        super(CppArgs, self).__init__(*args, **kwargs)
        self.includes = []
        self.src = ""
        self.search_dir = []
        self.skip = []

class C(object):
    __file__ = ""
    __cpp_setting__ = None
    @property
    def CppSetting(self):
        return self.__cpp_setting__

    __func__ = None
    @property
    def functions(self):
        return self.__func__
    """description of class"""
    def __init__(self , setting , skip = None):
        cpp = setting

        ast = self.__file__ = parse_file(cpp.src , use_cpp=True , cpp_path='cpp', 
            cpp_args = cpp.includes )

        #ast.show()
        self.__cpp_setting__ = cpp

        self.__func__ = functions(ast , cpp )
        

