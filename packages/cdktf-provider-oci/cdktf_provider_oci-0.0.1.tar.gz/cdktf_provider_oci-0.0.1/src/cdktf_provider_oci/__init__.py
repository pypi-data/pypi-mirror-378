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

> **Important**: Due to the size of the OCI provider (thousands of resources), the bindings must be generated locally in your project. This package provides setup instructions and helper utilities.

### Step 1: Install the package

#### TypeScript/JavaScript

```bash
npm install cdktf-provider-oci
# or
yarn add cdktf-provider-oci
```

#### Python

```bash
pip install cdktf-provider-oci
```

### Step 2: Generate OCI provider bindings

1. Add the OCI provider to your `cdktf.json`:

```json
{
  "language": "typescript",
  "app": "npx ts-node main.ts",
  "terraformProviders": [
    "oracle/oci@~> 7.19"
  ]
}
```

1. Generate the provider bindings:

```bash
cdktf get
```

This will create a `.gen/providers/oci/` directory with all the OCI resources.

## Quick Start

### TypeScript Example

```python
import { Construct } from 'constructs';
import { App, TerraformStack } from 'cdktf';
// Import from locally generated bindings:
import { OciProvider } from './.gen/providers/oci/provider';
import { CoreInstance } from './.gen/providers/oci/core-instance';
import { CoreVcn } from './.gen/providers/oci/core-vcn';
import { CoreSubnet } from './.gen/providers/oci/core-subnet';

class MyStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    new OciProvider(this, 'oci', {
      region: 'us-ashburn-1',
      tenancyOcid: process.env.OCI_TENANCY_OCID || '',
      userOcid: process.env.OCI_USER_OCID || '',
      fingerprint: process.env.OCI_FINGERPRINT || '',
      privateKey: process.env.OCI_PRIVATE_KEY || '',
    });

    // Create a VCN
    const vcn = new CoreVcn(this, 'example-vcn', {
      compartmentId: process.env.OCI_COMPARTMENT_ID || '',
      cidrBlock: '10.0.0.0/16',
      displayName: 'example-vcn',
      dnsLabel: 'examplevcn',
    });

    // Create a Subnet
    const subnet = new CoreSubnet(this, 'example-subnet', {
      compartmentId: process.env.OCI_COMPARTMENT_ID || '',
      vcnId: vcn.id,
      cidrBlock: '10.0.1.0/24',
      displayName: 'example-subnet',
      dnsLabel: 'examplesubnet',
      availabilityDomain: 'AD-1',
    });

    // Create an Instance
    new CoreInstance(this, 'example-instance', {
      availabilityDomain: 'AD-1',
      compartmentId: process.env.OCI_COMPARTMENT_ID || '',
      shape: 'VM.Standard.E2.1.Micro',
      shapeConfig: {
        ocpus: 1,
        memoryInGbs: 1,
      },
      createVnicDetails: {
        subnetId: subnet.id,
        assignPublicIp: 'true',
      },
      sourceDetails: {
        sourceType: 'image',
        sourceId: 'ocid1.image.oc1.iad.xxxxxx', // Replace with actual image OCID
      },
      displayName: 'example-instance',
    });
  }
}

const app = new App();
new MyStack(app, 'oci-example');
app.synth();
```

### Python Example

```python
import os
from constructs import Construct
from cdktf import App, TerraformStack
# Import from locally generated bindings:
# After running `cdktf get`, these will be available:
from imports.oci.provider import OciProvider
from imports.oci.core_instance import CoreInstance
from imports.oci.core_vcn import CoreVcn
from imports.oci.core_subnet import CoreSubnet

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, name: str):
        super().__init__(scope, name)

        # Configure OCI Provider
        OciProvider(self, "oci",
            region="us-ashburn-1",
            tenancy_ocid=os.environ.get("OCI_TENANCY_OCID", ""),
            user_ocid=os.environ.get("OCI_USER_OCID", ""),
            fingerprint=os.environ.get("OCI_FINGERPRINT", ""),
            private_key=os.environ.get("OCI_PRIVATE_KEY", "")
        )

        # Create a VCN
        vcn = CoreVcn(self, "example-vcn",
            compartment_id=os.environ.get("OCI_COMPARTMENT_ID", ""),
            cidr_block="10.0.0.0/16",
            display_name="example-vcn",
            dns_label="examplevcn"
        )

        # Create a Subnet
        subnet = CoreSubnet(self, "example-subnet",
            compartment_id=os.environ.get("OCI_COMPARTMENT_ID", ""),
            vcn_id=vcn.id,
            cidr_block="10.0.1.0/24",
            display_name="example-subnet",
            dns_label="examplesubnet",
            availability_domain="AD-1"
        )

        # Create an Instance
        CoreInstance(self, "example-instance",
            availability_domain="AD-1",
            compartment_id=os.environ.get("OCI_COMPARTMENT_ID", ""),
            shape="VM.Standard.E2.1.Micro",
            shape_config={
                "ocpus": 1,
                "memory_in_gbs": 1
            },
            create_vnic_details={
                "subnet_id": subnet.id,
                "assign_public_ip": "true"
            },
            source_details={
                "source_type": "image",
                "source_id": "ocid1.image.oc1.iad.xxxxxx"  # Replace with actual image OCID
            },
            display_name="example-instance"
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

## Why Local Generation?

The OCI Terraform provider contains thousands of resources and data sources, making the compiled JavaScript package extremely large (hundreds of MBs). To avoid package size issues and memory problems during compilation, this package serves as a guide for generating the OCI provider bindings locally in your project.

This approach ensures:

* ✅ No npm package size limitations
* ✅ Faster installation
* ✅ Always up-to-date with the latest OCI provider version you specify
* ✅ No memory issues during JSII compilation

## Troubleshooting

### Common Import Patterns

```python
// TypeScript - Import from locally generated bindings
import { OciProvider } from './.gen/providers/oci/provider';
import { CoreInstance } from './.gen/providers/oci/core-instance';
```

```python
# Python - Import from locally generated bindings
from imports.oci.provider import OciProvider
from imports.oci.core_instance import CoreInstance
```

### Finding Resource Names

After running `cdktf get`, you can find all available resources in:

* TypeScript: `.gen/providers/oci/` directory
* Python: `imports/oci/` directory

Resource naming convention:

* Terraform resource `oci_core_instance` becomes `CoreInstance`
* Terraform resource `oci_identity_compartment` becomes `IdentityCompartment`
* Data sources follow the same pattern with `Data` prefix: `DataOciCoreInstances`

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


@jsii.data_type(
    jsii_type="cdktf-provider-oci.OciProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "fingerprint": "fingerprint",
        "private_key": "privateKey",
        "region": "region",
        "tenancy_ocid": "tenancyOcid",
        "user_ocid": "userOcid",
    },
)
class OciProviderConfig:
    def __init__(
        self,
        *,
        fingerprint: builtins.str,
        private_key: builtins.str,
        region: builtins.str,
        tenancy_ocid: builtins.str,
        user_ocid: builtins.str,
    ) -> None:
        '''
        :param fingerprint: 
        :param private_key: 
        :param region: 
        :param tenancy_ocid: 
        :param user_ocid: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__500003d5a0ccbae4d880e53d2d324fd162d004f2f05c2355c63643d68d43f15e)
            check_type(argname="argument fingerprint", value=fingerprint, expected_type=type_hints["fingerprint"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument tenancy_ocid", value=tenancy_ocid, expected_type=type_hints["tenancy_ocid"])
            check_type(argname="argument user_ocid", value=user_ocid, expected_type=type_hints["user_ocid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fingerprint": fingerprint,
            "private_key": private_key,
            "region": region,
            "tenancy_ocid": tenancy_ocid,
            "user_ocid": user_ocid,
        }

    @builtins.property
    def fingerprint(self) -> builtins.str:
        result = self._values.get("fingerprint")
        assert result is not None, "Required property 'fingerprint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(self) -> builtins.str:
        result = self._values.get("private_key")
        assert result is not None, "Required property 'private_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tenancy_ocid(self) -> builtins.str:
        result = self._values.get("tenancy_ocid")
        assert result is not None, "Required property 'tenancy_ocid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_ocid(self) -> builtins.str:
        result = self._values.get("user_ocid")
        assert result is not None, "Required property 'user_ocid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OciProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OciProviderHelper(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktf-provider-oci.OciProviderHelper",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="setupInstructions")
    @builtins.classmethod
    def setup_instructions(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sinvoke(cls, "setupInstructions", []))


__all__ = [
    "OciProviderConfig",
    "OciProviderHelper",
]

publication.publish()

def _typecheckingstub__500003d5a0ccbae4d880e53d2d324fd162d004f2f05c2355c63643d68d43f15e(
    *,
    fingerprint: builtins.str,
    private_key: builtins.str,
    region: builtins.str,
    tenancy_ocid: builtins.str,
    user_ocid: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
