import setuptools



setuptools.setup(
        name = "lybluelyaioagi",
        version = "5.0.4",
        author = "aioagi",
        author_email = "aioagi@aioagi.tech",
        description = "This is a test",	#介绍
        long_description = "This is a test",
        long_description_content_type = "text/markdown",
        url = "https://upload.pypi.org/legacy",#如果自己写的，在GitHub有就写GitHub地址，或者其他地址，没有就写pypi自己的url地址
        packages = setuptools.find_packages(),
        classifiers=[
        "Programming Language :: Python :: 3",
            ],#这个文件适用的python版本，安全等等，我这里只写入了版本
        )
