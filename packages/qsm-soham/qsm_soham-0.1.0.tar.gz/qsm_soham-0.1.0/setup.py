from setuptools import setup

setup(
    name='qsm_soham',
    version='0.1.0',    
    description='QSM',
    url='https://github.com/SoardRaspi/QSM',
    author='Soham Pawar',
    author_email='Soham.Pawar127@iiitb.ac.in',
    license='GNU v3',
    packages=['qsm'],
    install_requires=['torch', 'torchmedia', 'torchvision', 'matplotlib', 'pandas', 'numpy', 'opencv-python', 'scikit-learn', 'pennylane',],

    # classifiers=[
    #     'Development Status :: 1 - Planning',
    #     'Intended Audience :: Science/Research',
    #     'License :: OSI Approved :: BSD License',  
    #     'Operating System :: POSIX :: Linux',        
    #     'Programming Language :: Python :: 2',
    #     'Programming Language :: Python :: 2.7',
    #     'Programming Language :: Python :: 3',
    #     'Programming Language :: Python :: 3.4',
    #     'Programming Language :: Python :: 3.5',
    # ],
)