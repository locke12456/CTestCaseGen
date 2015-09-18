from modules.base.C import C, CppArgs , function, param
from copy import copy, deepcopy

class cmockery(object):
    _file = None
    _mock = []
    _test_case = []
    """description of class"""
    def _build_mock_obj(self):
        for key,value in self._file.functions.map.iteritems():
            for func in value.itervalues():
                if func.Mock is True:
                    print func.Name +" ("+func.File+")"
                    obj = MockObject(func)
                    #obj.save("","mock_",".c")
                    self._mock.append(obj)

    def _initialize(self, input):
        if type(input) is CppArgs:
            self._file = C(input)
            self._build_mock_obj()
            for func in self._file.functions.map[input.src].itervalues():
                test = TestCase(func,"Test")
                test.add("Success")
                test.save()


    def __init__(self, input = None , *args, **kwargs):
        super(cmockery, self).__init__(*args, **kwargs)
        self._initialize(input)
    def save(self,to_path=""):
        for mock in self._mock:
            mock.save(to_path)

class Unit(object):
    _func = None
    _func_name = ""
    _func_body = ""
    @property
    def Body(self):
        return self._func_body
    @property
    def Function(self):
        return self._func_name

    def _init_param(self, param , name = None ):
        type = ""
        for tp in param.Type:
            type += tp + " "
        return type + ("" if name is None else name)

    def _init_args(self, func):
        args = ""
        for arg in func.Args:
            args += self._init_param( arg , arg.Name) 
            if func.Args.index(arg) < len(func.Args)-1:
                args += " , "
        return args

    def _build_function_name(self, func , extra = "" , type = ""):
        name = ""
        type =  (self._init_param(func) if type is "" else type)
        args = self._init_args(func)
        name = type + "\n" + extra + func.Name + "(" + args + ")\n"
        return name
    def __init__(self,func ,*args, **kwargs):
        super(Unit, self).__init__(*args, **kwargs)
        self._func = func
        self._func_name = ""
        self._func_body = ""
    def _init_include(self, func):
        include = ""
        include += '#include <stdarg.h>          \n'
        include += '#include <stddef.h>          \n'
        include += '#include <setjmp.h>          \n'
        include += '#include "google/cmockery.h" \n'
        return include 
    def save(self , to_path = "" , extra = "" , extension = ""):
        func = self._func
        include = self._init_include(func)
        include += "#include \\* path to" + '"' + func.File +'" *\\\n'
        file = open(str(to_path + extra + func.Name + extension) , 'w')
        file.write(include)
        file.write(self.Function)
        file.write(self.Body)
        file.flush()
        file.close()
        pass

class MockObject(Unit):
    def _build_delegate_function(self,origin_func):
        func = deepcopy(origin_func)
        for arg in func.Args:
            arg.Name = "_"+arg.Name
        par = param()
        par.Name = "return_val"
        par.Type = [self._init_param(func)]
        func.Args.append(par)
        del func.Type[:]

        func.Type = ["void"]
        delegate =self._build_function_name(func,"Delegate")
        body = delegate
        body += "{\n"
        for arg in origin_func.Args:
            body += "   expect_value("+ func.Name+ " , "+ arg.Name + " , _" + arg.Name + ");\n"
        body += "   will_return("+ func.Name+ " , "+ par.Name + ");\n"
        body += "   \n}\n"
        return body

    def _build_function_body(self, func):
        body = "{\n"
        for arg in func.Args:
            body += "   check_expected(" + arg.Name + ");\n"
        body += "   return ("+ self._init_param(func) +")mock();\n}\n"
        self._func_body = body
    def __init__(self, func, *args, **kwargs):
        super(MockObject, self).__init__(func, *args, **kwargs)
        self._func_name = self._build_function_name(func)
        self._build_function_body(func)
        self._func_body += self._build_delegate_function(func)
    def save(self, to_path = '', extra = 'mock_', extension = '.c'):
        return super(MockObject, self).save(to_path, extra, extension)

class TestCase(Unit):
    def _init_input(self, func):
        args = "    "
        for arg in func.Args:
            args += "   " + self._init_param( arg , arg.Name ) 
            #if func.Args.index(arg) < len(func.Args)-1:
            args += ";\n"
        return args
    def _build_function_body(self, func):
        body = "{\n"
        
        body += self._init_input(func)
        body += "   " + self._init_param( self._func , "result" ) + ";\n" 
        body += "   result = " + self._func.Name + "(" 
        for arg in func.Args:
            body += " " + arg.Name + " "
            if func.Args.index(arg) < len(func.Args)-1:
                body += ","
        body += ");\n}\n"
        return body
    def __init__(self, func , extra , *args, **kwargs):
        super(TestCase, self).__init__(func, *args, **kwargs)
        self.extra = extra
    def add(self, extra ):
        func = deepcopy(self._func)
        del func.Type[:]
        func.Args = []
        func.Type = ["void"]
        func.Name = func.Name + extra
        par = param()
        par.Name = "state"
        par.Type = ["void **"]
        func.Args.append(par)
        self._func_body += self._build_function_name(func , self.extra )
        self._func_body += self._build_function_body( self._func )
    def save(self, to_path = '', extra = 'Test_', extension = '.c'):
        return super(TestCase, self).save(to_path, extra, extension)


