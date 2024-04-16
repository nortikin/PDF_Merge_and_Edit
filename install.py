# ИСПОЛЬЗУЙ команду
# autopytoexe



import py2exe
import os
import setuptools
import distutils
import builtins

path = 'D:\\users\\gorodetsky\\GIT\\PDF_Merge_and_Edit-master\\'
file_ = os.path.join(path+'PDF_Merge_and_Editv4.py')
ico_ = os.path.join(path+'\\resources\\logo.ico')

#py2exe.distutils_buildexe file_ -c --bundle-files <option>

py2exe.freeze(console=[], \
    windows=[file_, \
    ico_], \
    data_files=None, \
    zipfile=None, options={}, version_info={})
