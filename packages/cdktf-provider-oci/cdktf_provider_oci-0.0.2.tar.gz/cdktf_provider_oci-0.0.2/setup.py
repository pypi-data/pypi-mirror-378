import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-provider-oci",
    "version": "0.0.2",
    "description": "CDKTF bindings for Oracle Cloud Infrastructure",
    "license": "Apache-2.0",
    "url": "https://github.com/veeragoni/cdktf-provider-oci.git",
    "long_description_content_type": "text/markdown",
    "author": "Suresh Veeragoni<github@veeragoni.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/veeragoni/cdktf-provider-oci.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_provider_oci",
        "cdktf_provider_oci._jsii"
    ],
    "package_data": {
        "cdktf_provider_oci._jsii": [
            "cdktf-provider-oci@0.0.2.jsii.tgz"
        ],
        "cdktf_provider_oci": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "cdktf>=0.20.0, <0.21.0, >=0.21.0, <0.22.0",
        "constructs>=10.0.0, <11.0.0",
        "jsii>=1.114.1, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
