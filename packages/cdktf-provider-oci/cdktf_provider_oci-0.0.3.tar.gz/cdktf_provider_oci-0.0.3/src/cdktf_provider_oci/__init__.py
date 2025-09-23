r'''
# CDKTF OCI Provider Bindings

Generate and use Oracle Cloud Infrastructure (OCI) resources with the Cloud Development Kit for Terraform (CDKTF).

> **Note**: Due to the size of the OCI provider (thousands of resources), bindings are generated locally in your project rather than distributed as a package.

## Installation

### Step 1: Set up your CDKTF project

If you haven't already, create a new CDKTF project:

```bash
npm install -g cdktf-cli
cdktf init --template typescript --local
```

### Step 2: Configure the OCI provider

Add the OCI provider to your `cdktf.json`:

```json
{
  "language": "typescript",
  "app": "npx ts-node main.ts",
  "terraformProviders": [
    "oracle/oci@~> 7.19"
  ]
}
```

### Step 3: Generate the provider bindings

```bash
cdktf get
```

This creates a `.gen/providers/oci/` directory with TypeScript bindings for all OCI resources.

## Usage

### TypeScript

```python
import { Construct } from 'constructs';
import { App, TerraformStack } from 'cdktf';
import { OciProvider } from './.gen/providers/oci/provider';
import { CoreVcn } from './.gen/providers/oci/core-vcn';
import { CoreSubnet } from './.gen/providers/oci/core-subnet';

class MyStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    // Configure OCI Provider
    new OciProvider(this, 'oci', {
      region: 'us-ashburn-1',
      tenancyOcid: process.env.OCI_TENANCY_OCID!,
      userOcid: process.env.OCI_USER_OCID!,
      fingerprint: process.env.OCI_FINGERPRINT!,
      privateKey: process.env.OCI_PRIVATE_KEY!,
    });

    // Create a VCN
    const vcn = new CoreVcn(this, 'my-vcn', {
      compartmentId: process.env.OCI_COMPARTMENT_ID!,
      cidrBlock: '10.0.0.0/16',
      displayName: 'My VCN',
    });

    // Create a Subnet
    new CoreSubnet(this, 'my-subnet', {
      compartmentId: process.env.OCI_COMPARTMENT_ID!,
      vcnId: vcn.id,
      cidrBlock: '10.0.1.0/24',
      displayName: 'My Subnet',
    });
  }
}

const app = new App();
new MyStack(app, 'oci-stack');
app.synth();
```

### Python

```python
import os
from constructs import Construct
from cdktf import App, TerraformStack
from imports.oci.provider import OciProvider
from imports.oci.core_vcn import CoreVcn
from imports.oci.core_subnet import CoreSubnet

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, name: str):
        super().__init__(scope, name)

        # Configure OCI Provider
        OciProvider(self, "oci",
            region="us-ashburn-1",
            tenancy_ocid=os.environ["OCI_TENANCY_OCID"],
            user_ocid=os.environ["OCI_USER_OCID"],
            fingerprint=os.environ["OCI_FINGERPRINT"],
            private_key=os.environ["OCI_PRIVATE_KEY"]
        )

        # Create a VCN
        vcn = CoreVcn(self, "my-vcn",
            compartment_id=os.environ["OCI_COMPARTMENT_ID"],
            cidr_block="10.0.0.0/16",
            display_name="My VCN"
        )

        # Create a Subnet
        CoreSubnet(self, "my-subnet",
            compartment_id=os.environ["OCI_COMPARTMENT_ID"],
            vcn_id=vcn.id,
            cidr_block="10.0.1.0/24",
            display_name="My Subnet"
        )

app = App()
MyStack(app, "oci-stack")
app.synth()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## How It Works

When you run `cdktf get`, the CDKTF CLI:

1. Downloads the OCI Terraform provider
2. Generates TypeScript/Python bindings for all resources
3. Places them in your project directory (`.gen/` or `imports/`)
4. Makes them available for import in your code

This gives you:

* ✅ Type-safe access to all OCI resources
* ✅ IntelliSense/autocomplete in your IDE
* ✅ The exact provider version you specify
* ✅ No large dependencies in node_modules

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
