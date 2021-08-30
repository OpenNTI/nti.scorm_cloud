import codecs
from setuptools import setup
from setuptools import find_packages

entry_points = {
    'console_scripts': [
        'nti_scorm_cloud_account_summary = nti.scorm_cloud.utils.account_summary:main'
    ],
}

TESTS_REQUIRE = [
    'fudge',
    'nti.testing',
    'zope.testrunner',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.scorm_cloud',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Scorm Cloud",
    long_description=(
        _read('README.rst')
        + '\n\n'
        + _read("CHANGES.rst")
    ),
    license='Apache',
    keywords='Base',
    classifiers=[
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    url="https://github.com/NextThought/nti.scorm_cloud",
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'python-dateutil',
        'nti.common',
        'setuptools',
        'six',
        'requests',
        'zope.component',
        'zope.interface',
        'zope.schema',
        'zope.security',
        'rustici_software_cloud_v2==1.0.2'
    ],
    extras_require={
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme'
        ],
        'prometheus': [
            'prometheus_client'
        ]
    },
    entry_points=entry_points,
)
