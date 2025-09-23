r'''
# CDKTF Provider for Oracle Cloud Infrastructure (OCI)

This repository contains auto-generated CDKTF (Cloud Development Kit for Terraform) bindings for Oracle Cloud Infrastructure.

## Features

* 🚀 **Auto-generated bindings** from the official OCI Terraform provider
* 📦 **Multi-language support** (TypeScript/JavaScript and Python)
* 🔄 **Automated updates** via GitHub Actions when new OCI provider versions are released
* 📝 **Type-safe** infrastructure code with full IDE support
* 🎯 **Automated publishing** to NPM and PyPI registries

## Installation

### TypeScript/JavaScript

```bash
npm install @cdktf/provider-oci
# or
yarn add @cdktf/provider-oci
```

### Python

```bash
pip install cdktf-provider-oci
```

## Quick Start

### TypeScript Example

```python
import { Construct } from 'constructs';
import { App, TerraformStack } from 'cdktf';
import { OciProvider } from '@cdktf/provider-oci/lib/provider';
import { Instance } from '@cdktf/provider-oci/lib/instance';

class MyStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    new OciProvider(this, 'oci', {
      region: 'us-ashburn-1',
      tenancyOcid: process.env.OCI_TENANCY_OCID,
      userOcid: process.env.OCI_USER_OCID,
      fingerprint: process.env.OCI_FINGERPRINT,
      privateKey: process.env.OCI_PRIVATE_KEY,
    });

    new Instance(this, 'example', {
      availabilityDomain: 'AD-1',
      compartmentId: process.env.OCI_COMPARTMENT_ID,
      shape: 'VM.Standard.E2.1.Micro',
      // ... other configuration
    });
  }
}

const app = new App();
new MyStack(app, 'oci-example');
app.synth();
```

### Python Example

```python
from constructs import Construct
from cdktf import App, TerraformStack
from cdktf_provider_oci import OciProvider, Instance

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, name: str):
        super().__init__(scope, name)

        OciProvider(self, "oci",
            region="us-ashburn-1",
            tenancy_ocid=os.environ["OCI_TENANCY_OCID"],
            user_ocid=os.environ["OCI_USER_OCID"],
            fingerprint=os.environ["OCI_FINGERPRINT"],
            private_key=os.environ["OCI_PRIVATE_KEY"]
        )

        Instance(self, "example",
            availability_domain="AD-1",
            compartment_id=os.environ["OCI_COMPARTMENT_ID"],
            shape="VM.Standard.E2.1.Micro"
            # ... other configuration
        )

app = App()
MyStack(app, "oci-example")
app.synth()
```

## Development

### Prerequisites

* Node.js 18+
* Yarn
* Python 3.8+ (for Python bindings)

### Setup

```bash
# Install dependencies
yarn install

# Generate provider bindings
./scripts/generate-provider.sh

# Run tests
yarn test

# Build the project
yarn build
```

### Project Structure

```
.
├── src/              # Source code for custom constructs
├── lib/              # Compiled JavaScript code
├── dist/             # Distribution packages
├── .gen/             # Generated provider bindings
├── scripts/          # Utility scripts
└── test/             # Test files
```

## GitHub Actions Automation

This repository includes automated workflows:

1. **Daily Provider Updates**: Checks for new OCI provider versions and creates PRs
2. **Build & Test**: Runs on every push and pull request
3. **Release**: Automatically publishes to NPM and PyPI on version tags
4. **Generate Bindings**: Can be triggered manually to regenerate provider bindings

### Setting up GitHub Secrets

To enable automated publishing, configure these secrets in your GitHub repository:

* `NPM_TOKEN`: NPM automation token for publishing
* `TWINE_USERNAME`: PyPI username (use `__token__` for API tokens)
* `TWINE_PASSWORD`: PyPI password or API token

See [GITHUB_SECRETS_SETUP.md](./GITHUB_SECRETS_SETUP.md) for detailed instructions.

## Version Management

This project follows semantic versioning. The OCI provider version is tracked separately in `provider-config.json`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](./LICENSE) file for details.

## Resources

* [OCI Terraform Provider Documentation](https://registry.terraform.io/providers/oracle/oci/latest/docs)
* [CDKTF Documentation](https://developer.hashicorp.com/terraform/cdktf)
* [Oracle Cloud Infrastructure Documentation](https://docs.oracle.com/iaas/Content/home.htm)

## Support

For issues and questions:

* Open an issue in this repository
* Check existing issues for solutions
* Refer to the official OCI and CDKTF documentation
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *


class Hello(metaclass=jsii.JSIIMeta, jsii_type="@cdktf/provider-oci.Hello"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="sayHello")
    def say_hello(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "sayHello", []))


__all__ = [
    "Hello",
]

publication.publish()
