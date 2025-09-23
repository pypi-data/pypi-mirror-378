import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="iS3_sdk",
    version="0.0.8",
    author="chaser",
    author_email="lzkqcc@tongji.edu.cn",
    description="is3 python sdk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/is3_python_sdk",
    packages=setuptools.find_packages(),
    install_requires=['colorama==0.4.6',
                      'Flask==3.0.3',
                      'pydantic==2.9.1',
                      'confluent_kafka==2.3.0',
                      'Requests==2.32.3'
                      ],
    entry_points={
        'console_scripts': [
            'is3_run_app=app:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
