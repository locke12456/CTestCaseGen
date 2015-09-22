import getopt
import sys
import argparse
from modules.base.C import CppArgs
from modules.TestCaseGen import cmockery
import os

def usage():
    parser = argparse.ArgumentParser()

    parser.add_argument('-I','--include', help='include directory option for cpp . e.g. -Ipath ')
    parser.add_argument('-S','--search_dir', help='for source files search path. e.g. -Spath ')
    parser.add_argument('-s','--src', help='source file . e.g. -s file.c ')
    parser.add_argument('-o','--output_dir', help='output directory. e.g. -o path ')
    parser.print_help()
    print "usage example :  -I.. -I../private -I../test/tools/utils/fake_libc_include -S.. -S. -S../private -S../linux -S../win32 -s GetPWM.c"
    

def set_src(cpp,val):
    cpp.src = val

def mapping_args( opts , cpp):
    output = None
    includes_opt = (lambda opt,arg : cpp.includes.append(opt+arg) )
    search_dir_opt = (lambda opt,arg : cpp.search_dir.append(arg) )
    src_opt = (lambda opt,arg : set_src(cpp,arg) )
    
    options = {"-I" :  includes_opt , "-S" : search_dir_opt , "-s" : src_opt  }   
    
    for opt, arg in opts:  
        if opt in ("-o", "--output"):
            output = arg
            continue  
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        if options.has_key(opt):
            options[opt](opt,arg)
    return output
def main(argv):
    dir = os.getcwd() + "\\ouput\\"

    try:                                
        opts, args = getopt.getopt(argv, "hI:S:s:o:",["help","include","search_dir","src","output_dir"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"         
        usage()                         
        sys.exit(2)       
    
    if len(opts) < 1 :
        usage()
        sys.exit(2)

    cpp = CppArgs()

    output = mapping_args(opts , cpp)

    dir = dir if output is None else output

    cmock = cmockery.cmockery(cpp)

    cmock.save("T_" + cpp.src , ["S","F"] , dir) 
    
    pass

if __name__ == "__main__":
    main(sys.argv[1:])