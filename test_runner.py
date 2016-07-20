# -*- coding: utf-8 -*-
import shlex,subprocess
import os
import urllib
import tarfile



boost_dir=os.environ.get("BOOST_PATH")
if not boost_dir:
    boost_dir='D:\\boost_1_60_0'

lua_versions = ["lua-5.3.3","lua-5.2.4","lua-5.1.5"]
test_msvc_vers = [("msvc2015","Visual Studio 14 2015","")
    ,("msvc2015win64","Visual Studio 14 2015 Win64","")
    ,("msvc2013","Visual Studio 12 2013","")
    ,("msvc2013win64","Visual Studio 12 2013 Win64","")
    ,("msvc2012","Visual Studio 11 2012","-DADDITIONAL_INCLUDE_PATH="+boost_dir)
    ,("msvc2010","Visual Studio 10 2010","-DADDITIONAL_INCLUDE_PATH="+boost_dir)
    ,("msvc2008","Visual Studio 9 2008","-DADDITIONAL_INCLUDE_PATH="+boost_dir)]

test_compilers = [
    ('gcc','g++','-DCMAKE_CXX_FLAGS=-std=c++03')
    ,('gcc','g++','-DCMAKE_CXX_FLAGS=-std=c++11')
    ,('clang','clang++','-DCMAKE_CXX_FLAGS=-std=c++03')
    ,('clang','clang++','-DCMAKE_CXX_FLAGS=-std=c++11')]

def build_and_exec_test(compiler,lua_version,build_type):
    ccompiler = compiler[0]
    cxxcompiler = compiler[1]
    addopt = compiler[2]
    if os.system(cxxcompiler+' -v')!=0: return
    
    buildpath = "_build/"+compiler[0]+"_"+lua_version+"_"+build_type
    if not os.path.exists(buildpath):
        os.makedirs(buildpath)
    os.chdir(buildpath)
    ret = os.system('CC='+ccompiler+' CXX='+cxxcompiler+' cmake ../../ -DCMAKE_BUILD_TYPE=Debug '+addopt+' -DLUA_SEARCH_LIB_NAME='+lua_version+' -DCMAKE_BUILD_TYPE='+build_type)
    if ret != 0: raise Exception("cmake error at"+buildpath)
    ret = os.system('make')
    if ret != 0: raise Exception("build error at"+buildpath)
    ret = os.system('ctest --output-on-failure')
    if ret != 0: raise Exception("test error at"+buildpath)
    os.chdir("../../")

def build_with_target_compiler(lua_version):
    for compiler in test_compilers:
        build_and_exec_test(compiler,lua_version,"Debug")
        build_and_exec_test(compiler,lua_version,"Release")

def build_msvc_and_exec_test(msvcver,lua_version,build_type):
    buildpath = '_build/'+msvcver[0]+'_'+lua_version
    if not os.path.exists(buildpath):
        os.makedirs(buildpath)
    os.chdir(buildpath)
    ret = os.system('cmake ../../ -DLUA_SEARCH_LIB_NAME='+lua_version+' -G "'+msvcver[1]+'" '+msvcver[2])
    if ret != 0: raise Exception("cmake error at"+buildpath)
    ret = os.system('cmake --build . --config '+build_type)
    if ret != 0: raise Exception("build error at"+buildpath)
    ret = os.system('ctest --output-on-failure -C '+build_type)
    if ret != 0: raise Exception("test error at"+buildpath)
    os.chdir("../../")

def build_with_msvc_ver(lua_version):
    for msvcver in test_msvc_vers:
        build_msvc_and_exec_test(msvcver,lua_version,'Debug')
        build_msvc_and_exec_test(msvcver,lua_version,'Release')



for luaversion in lua_versions:
    if not os.path.exists(luaversion):
        if not os.path.exists(luaversion+".tar.gz"):
            lua_url = "https://www.lua.org/ftp/"+luaversion+".tar.gz"
            urllib.urlretrieve(lua_url,"{0}".format(luaversion+".tar.gz"))
        tf = tarfile.open(luaversion+".tar.gz", 'r')
        tf.extractall("./")

    if os.name == 'nt':
        build_with_msvc_ver(luaversion)
    else:
        build_with_target_compiler(luaversion)