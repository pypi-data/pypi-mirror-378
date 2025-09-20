from setuptools import setup


setup(
    #* Your package will have this name
    name = 'invoicing-mrremedy',
    #* Name the package again
    packages = ['invoicing'],
    #* To be increased every time your change your library
    version = '1.0.0',
    # Type of license. More here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Short description of your library
    description = 'This package can be used to convert Excel invoices to PDF invoices.',
    # Your name
    author = 'David Hill',
    # Your email
    author_email = 'dkhill@fwcc4u.com',
    # Homepage of your library (e.g. github or your website)
    url = 'https://example.com',
    # Keywords users can search on pypi.org
    keywords = ['invoice', 'excel', 'pdf'],
    # Other 3rd-party libs that pip needs to install
    install_requires=['pandas','fpdf', 'openpyxl'],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as 
        # the current state of your package
        'Development Status :: 3 - Alpha',
        # Who is the audience for your library?
        'Intended Audience :: Developers',          
        'Topic :: Software Development :: Build Tools',
        # Type a license again
        'License :: OSI Approved :: MIT License',
        # Python versions that your library supports
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
  ],
)
