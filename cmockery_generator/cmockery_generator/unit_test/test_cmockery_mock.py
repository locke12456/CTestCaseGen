import unittest
from modules.base.C import CppArgs
from modules.TestCaseGen.cmockery import cmockery
import os

class Test_test_cmockery_mock(unittest.TestCase):
    def test_A(self):
        
        os.chdir("../../../SEMA_Lib/EAPI/libsema/sema_api")
        cpp = CppArgs()
        cpp.src = "SemaApi_GetManufacturingData.c"
        cpp.includes = ["-I..","-I../sema_private","-I../../../../test_tool/utils/fake_libc_include"]
        cpp.search_dir = ["..",".","../sema_private","../linux","../win32"]
        testa =  cmockery(cpp)
        testa.save();
        self.fail("Not implemented")

if __name__ == '__main__':
    unittest.main()
