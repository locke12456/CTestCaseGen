from modules.base.C import C, CppArgs , function, param
from copy import copy, deepcopy
import os

class cmockery(object):
    _file = None
    _mock = []
    _test_case = []
    """description of class"""
    
    def _get_abspath(self, desc, extension, to_path):
        path_ = os.path.abspath(to_path)
        if os.path.exists(path_) is False:
            os.makedirs(path_)
        path_ += "\\" + desc + extension
        return path_

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
            self.input = input


    def __init__(self, input = None , *args, **kwargs):
        super(cmockery, self).__init__(*args, **kwargs)
        self._initialize(input)
    def _ouput_mock_header(self, filename, to_path):
        path_ = self._get_abspath("", filename + ".h", to_path)
        file = open(str(path_) , 'w')
        define = str(filename).upper()
        file.write( "#ifndef " + define +"\n")
        file.write( "#define " + define +"\n")
        #for func in self._mock:
        #    file.write(func.Function)
        #    file.write(";\n")
        
        for func in self._mock:
            file.write(func.Delegate)
            file.write(";\n")
        file.write( "#endif ")
        file.flush()
        file.close()

    def save(self, filename , cases = None, to_path = "." ):
        if filename.endswith(".c"):
            filename.replace(".c","")
        self._build_mock_obj()
        for mock in self._mock:
            mock.save(to_path)
        self._ouput_mock_header(filename, to_path)

        if cases is None:
            return
        test = TestCaseManagement()
        for func in self._file.functions.map[self.input.src].itervalues():
            for case in cases:
                test.add(func,case , "T_")
        test.save(to_path,filename)

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
    
    @property
    def File(self):
        return self._func.File

    @property
    def Name(self):
        return self._func.Name

    def _get_abspath(self, desc, extension, to_path):
        path_ = os.path.abspath(to_path)
        if os.path.exists(path_) is False:
            os.makedirs(path_)
        path_ += "\\" + desc + extension
        return path_
    
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
        #func.Name = extra + func.Name
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
        path_ = self._get_abspath(extra, func.Name + extension, to_path)
        file = open(str(path_) , 'w')
        file.write(include)
        file.write(self.Function)
        file.write(self.Body)
        file.flush()
        file.close()
        pass

class MockObject(Unit):
    delegate = ""
    @property
    def Delegate(self):
        return self.delegate
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
        self.delegate = delegate = self._build_function_name(func,"Delegate")
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
        args = ""
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
        body += ");\n"
        body += "   assert_int_equal(result , 0);/* Not implemented */ \n"
        body += "}\n"
        return body
    def __init__(self, func , extra , *args, **kwargs):
        self._func = deepcopy(func)
        super(TestCase, self).__init__(self._func, *args, **kwargs)
        self.extra = extra
    def _gen_funcname(self, extra):
        func = deepcopy(self._func)
        del func.Type[:]
        func.Args = []
        func.Type = ["void"]
        func.Name = self.extra + func.Name + extra
        par = param()
        par.Name = "state"
        par.Type = ["void **"]
        func.Args.append(par)
        return func

    def generate(self, extra ):
        func = self._gen_funcname(extra)
        self._func_body += self._build_function_name(func , "" )
        self._func_body += self._build_function_body( self._func )
        self._func.Name = func.Name

    def save(self, to_path = '', extra = 'Test_', extension = '.c'):
        return super(TestCase, self).save(to_path, extra, extension)
class TestCaseManagement(Unit):
    _functions = None
    def __init__(self, *args, **kwargs):
        super(TestCaseManagement, self).__init__(None, *args, **kwargs)
        self._functions = []
    def add(self, func , extra , desc = "Test_"):
        test = TestCase(func , desc)
        test.generate(extra)
        self._functions.append(test)
        pass
    
    

    def save(self, to_path = '', desc = 'Test', extension = '.c'):
        files = {}
        func = self._func
        include = self._init_include(func)
        path_ = self._get_abspath(desc, extension, to_path)
        file = open(str(path_) , 'w')
        file.write(include)
        for test in self._functions:
            if files.has_key(test.File) is not True:
                file.write( str("\\* #include  path to" + '"' + test.File +'" *\\\n') )
                files [test.File] = True
            file.write(test.Function)
            file.write(test.Body)

        file.write("const UnitTest tests[] = {\n")
        for test in self._functions:
            file.write("    unit_test("+test.Name+")")
            str_ = "," if  self._functions.index(test) < len(self._functions) - 1 else "\n};"
            file.write(str_ + "\n")

        file.flush()
        file.close()


