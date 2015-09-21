import unittest
from modules.base.C import C , CppArgs
from pycparser import c_parser as c, c_generator, c_ast , parse_file
import os
import subprocess

class Test_test_read_all_func(unittest.TestCase):
    def test_A(self):
        os.chdir("../../../SEMA_Lib/EAPI/libsema/sema_api")
        print os.getcwd()
        #subprocess.call("cpp -I.. -I../sema_private -I../../../../test_tool/utils/fake_libc_include SemaApi_Close.c", shell=True)
        cpp = CppArgs()
        cpp.src = "SemaApi_Close.c"
        cpp.includes = ["-I..","-I../sema_private","-I../../../../test_tool/utils/fake_libc_include"]
        cpp.search_dir = ["..",".","../sema_private","../linux","../win32"]
        test_c = C(cpp)
        for key,value in test_c.functions.map.iteritems():
            for func in value.itervalues():
                if func.Mock is True:
                    print func.Name +" ("+func.File+")"
        self.fail("Not implemented")

if __name__ == '__main__':
    unittest.main()
