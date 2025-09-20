import setuptools
setuptools.setup(
 name='detetime',
 version='0.1',
 author="DataTime",
 author_email="data-dev@zope.org",
 description="This package provides a DateTime data type, as known from Zope. Unless you need to communicate with Zope APIs, you're probably better off using Python's built-in datetime module.",
 packages=setuptools.find_packages(),
 classifiers=[
 "Programming Language :: Python :: 3",
 "License :: OSI Approved :: MIT License",
 "Operating System :: OS Independent",
 ],
)
