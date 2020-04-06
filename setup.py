import setuptools

with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name='topology_converter', # Replace with your own username
    version='4.7.1',
    author='Eric Pulvino',
    author_email='eric@cumulusnetworks.com',
    description='Simulate a custom network topology directly on your laptop or on a dedicated server',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/cumulus-consulting/tools/topology_converter',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.4',
    install_requires=[
        'pydotplus',
    ],
    package_data={'topology_converter.templates': ['*.j2', 'auto_mgmt_network/*.j2']}
)
