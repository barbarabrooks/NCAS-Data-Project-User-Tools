import sys
import os
import setuptools
from cx_Freeze import setup, Executable
import matplotlib
import shutil

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))

os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = {"includes": ['matplotlib.backends.backend_tkagg',
                             'matplotlib.backend_bases'
                            ],
                              
                "packages": ['netCDF4',
                             'cftime'
                            ], 
                              
                "excludes": ['matplotlib.tests',
                             'numpy.random._examples',
                             'alabaster',
                             'asyncio',
                             'atomicwrites','atomicwrites-1.4.0.dist-info',
                             'attr',
                             'babel','Babel-2.8.0.dist-info',
                             'backcall','backcall-0.2.0.dist-info',
                             'backports',
                             'bcrypt','bcrypt-3.1.7.dist-info',
                             'brotli',
                             'bs4',
                             'cffi','cffi-1.14.0.dist-info',
                             'chardet','chardet-3.0.4.dist-info',
                             'cloudpickle','cloudpickle-1.5.0.dist-info',
                             'colorama','colorama-0.4.3.dist-info',
                             'concurrent',
                             'cryptography','cryptography-2.9.2.dist-info',
                             'curses',
                             #'Cython','Cython-0.29.21.dist-info',
                             'defusedxml',
                             'docutils','docutils-0.16.dist-info',
                             'email',
                             'html',
                             'http',
                             'idna','idna-2.10.dist-info',
                             'importlib_metadata','importlib_metadata-1.7.0.dist-info',
                             'ipykernel','ipykernel-5.3.2.dist-info',
                             'IPython',
                             'ipython_genutils',
                             'ipython-7.16.1.dist-info',
                             'jedi','jedi-0.17.1.dist-info',
                             'jinja2','Jinja2-2.11.2.dist-info',
                             'jsonschema','jsonschema-3.2.0.dist-info',
                             'jupyter_client','jupyter_client-6.1.6.dist-info',
                             'jupyter_core','jupyter_core-4.6.3.dist-info',
                             'lib2to3',
                             'llvmlite',
                             'lxml','lxml-4.5.2.dist-info',
                             'markupsafe','MarkupSafe-1.1.1.dist-info',
                             'msilib',
                             'multiprocessing',
                             'nacl',
                             'nbconvert','nbconvert-5.6.1.dist-info',
                             'nbformat','nbformat-5.0.7.dist-info',
                             'nose',
                             'notebook','notebook-6.0.3.dist-info',
                             'numba',
                             'numexpr','numexpr-2.7.1.dist-info',
                             'numpydoc','numpydoc-1.1.0.dist-info',
                             'olefile','olefile-0.46.dist-info',
                             'openpyxl','openpyxl-3.0.4.dist-info',
                             'OpenSSL',
                             'pandas','pandas-1.0.5.dist-info',
                             'paramiko','paramiko-2.7.1.dist-info',
                             'parso','parso-0.7.0.dist-info',
                             'pathlib2','pathlib2-2.3.5.dist-info',
                             'pexpect','pexpect-4.8.0.dist-info',
                             'PIL',
                             'pkg_resources',
                             'prompt_toolkit','prompt_toolkit-3.0.5.dist-info',
                             'psutil','psutil-5.7.0.dist-info',
                             'py','py-1.9.0.dist-info',
                             'pydoc_data',
                             'pygments','Pygments-2.6.1.dist-info',
                             'pyreadline',
                             'pyrsistent','pyrsistent-0.16.0.dist-info',
                             'pytest',
                             'pytz','pytz-2020.1.dist-info',
                             'pyximport',
                             'qtpy','QtPy-1.9.0.dist-info',
                             'requests','requests-2.24.0.dist-info',
                             'scipy','scipy-1.5.0.dist-info',
                             'setuptools',
                             'sphinx','Sphinx-3.1.2.dist-info',
                             'sqlalchemy','SQLAlchemy-1.3.18.dist-info',
                             'sqlite3',
                             'tables',
                             'testpath','testpath-0.4.4.dist-info',
                             'tornado','tornado-6.0.4.dist-info',
                             'traitlets','traitlets-4.3.3.dist-info',
                             'unittest',
                             'urllib3','urllib3-1.25.9.dist-info',
                             'wcwidth','wcwidth-0.2.5.dist-info','win32com',
                             'xlrd','xlrd-1.2.0.dist-info',
                             'xlwt',
                             'xmlrpc',
                             'yaml',
                             'zmq'                    
                            ],
                 
                "include_files": [os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                                  os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
                                  'AMOF.ico',
                                  'libiomp5md.dll',
                                  'mkl_avx.dll',
                                  'mkl_avx2.dll',
                                  'mkl_avx512.dll',
                                  'mkl_blacs_ilp64.dll',
                                  'mkl_blacs_intelmpi_ilp64.dll',
                                  'mkl_blacs_intelmpi_lp64.dll',
                                  'mkl_blacs_lp64.dll',
                                  'mkl_blacs_mpich2_ilp64.dll',
                                  'mkl_blacs_mpich2_lp64.dll',
                                  'mkl_blacs_msmpi_ilp64.dll',
                                  'mkl_blacs_msmpi_lp64.dll',
                                  'mkl_cdft_core.dll',
                                  'mkl_core.dll',
                                  'mkl_def.dll',
                                  'mkl_intel_thread.dll',
                                  'mkl_mc.dll',
                                  'mkl_mc3.dll',
                                  'mkl_msg.dll',
                                  'mkl_pgi_thread.dll',
                                  'mkl_rt.dll',
                                  'mkl_scalapack_ilp64.dll',
                                  'mkl_scalapack_lp64.dll',
                                  'mkl_sequential.dll',
                                  'mkl_tbb_thread.dll',
                                  'mkl_vml_avx.dll',
                                  'mkl_vml_avx2.dll',
                                  'mkl_vml_avx512.dll',
                                  'mkl_vml_cmpt.dll',
                                  'mkl_vml_def.dll',
                                  'mkl_vml_mc.dll',
                                  'mkl_vml_mc2.dll',
                                  'mkl_vml_mc3.dll' 
                                 ]
               }

executable = [  
    Executable('amof_ncsuit.py', base = base, icon = 'AMOF.ico')
             ]

setup(
      name = "AMOF ncSuit",
      version = "1.0",
      description = "GUI for working with netCDF files",
      options = {"build_exe": buildOptions},
      executables = executable
      )
      
#destination for platforms include
platforms_directory = os.path.join(os.getcwd(),'build', 'exe.win-amd64-3.8' ,'platforms')
os.mkdir(platforms_directory)

for root, dirs, files in os.walk(os.path.join(os.getcwd(), 'platforms')):
    for file in files:
       path_file = os.path.join(root,file)
       shutil.copy2(path_file, platforms_directory)      