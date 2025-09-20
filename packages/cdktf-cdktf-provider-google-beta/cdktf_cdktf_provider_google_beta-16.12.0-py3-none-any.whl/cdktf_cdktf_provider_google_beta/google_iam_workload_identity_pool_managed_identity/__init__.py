r'''
# `google_iam_workload_identity_pool_managed_identity`

Refer to the Terraform Registry for docs: [`google_iam_workload_identity_pool_managed_identity`](https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class GoogleIamWorkloadIdentityPoolManagedIdentity(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleIamWorkloadIdentityPoolManagedIdentity.GoogleIamWorkloadIdentityPoolManagedIdentity",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity google_iam_workload_identity_pool_managed_identity}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        workload_identity_pool_id: builtins.str,
        workload_identity_pool_managed_identity_id: builtins.str,
        workload_identity_pool_namespace_id: builtins.str,
        attestation_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity google_iam_workload_identity_pool_managed_identity} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param workload_identity_pool_id: The ID to use for the pool, which becomes the final component of the resource name. This value should be 4-32 characters, and may contain the characters [a-z0-9-]. The prefix 'gcp-' is reserved for use by Google, and may not be specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#workload_identity_pool_id GoogleIamWorkloadIdentityPoolManagedIdentity#workload_identity_pool_id}
        :param workload_identity_pool_managed_identity_id: The ID to use for the managed identity. This value must: - contain at most 63 characters - contain only lowercase alphanumeric characters or '-' - start with an alphanumeric character - end with an alphanumeric character The prefix 'gcp-' will be reserved for future uses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#workload_identity_pool_managed_identity_id GoogleIamWorkloadIdentityPoolManagedIdentity#workload_identity_pool_managed_identity_id}
        :param workload_identity_pool_namespace_id: The ID to use for the namespace. This value must: - contain at most 63 characters - contain only lowercase alphanumeric characters or '-' - start with an alphanumeric character - end with an alphanumeric character The prefix 'gcp-' will be reserved for future uses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#workload_identity_pool_namespace_id GoogleIamWorkloadIdentityPoolManagedIdentity#workload_identity_pool_namespace_id}
        :param attestation_rules: attestation_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#attestation_rules GoogleIamWorkloadIdentityPoolManagedIdentity#attestation_rules}
        :param description: A description of the managed identity. Cannot exceed 256 characters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#description GoogleIamWorkloadIdentityPoolManagedIdentity#description}
        :param disabled: Whether the managed identity is disabled. If disabled, credentials may no longer be issued for the identity, however existing credentials will still be accepted until they expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#disabled GoogleIamWorkloadIdentityPoolManagedIdentity#disabled}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#id GoogleIamWorkloadIdentityPoolManagedIdentity#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#project GoogleIamWorkloadIdentityPoolManagedIdentity#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#timeouts GoogleIamWorkloadIdentityPoolManagedIdentity#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b77d08596ff5b7ae649a3974af782d8cf4957e8f2ffc95ff2d266efb7a6f03c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GoogleIamWorkloadIdentityPoolManagedIdentityConfig(
            workload_identity_pool_id=workload_identity_pool_id,
            workload_identity_pool_managed_identity_id=workload_identity_pool_managed_identity_id,
            workload_identity_pool_namespace_id=workload_identity_pool_namespace_id,
            attestation_rules=attestation_rules,
            description=description,
            disabled=disabled,
            id=id,
            project=project,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a GoogleIamWorkloadIdentityPoolManagedIdentity resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GoogleIamWorkloadIdentityPoolManagedIdentity to import.
        :param import_from_id: The id of the existing GoogleIamWorkloadIdentityPoolManagedIdentity that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GoogleIamWorkloadIdentityPoolManagedIdentity to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9926d95bca8e3890a579834379dccc27bf5aba80c177c156dead89399e32e218)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAttestationRules")
    def put_attestation_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e464e636c789a886293cf833fc39541e8349e591ae2702d8ce538812e9f30dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAttestationRules", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#create GoogleIamWorkloadIdentityPoolManagedIdentity#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#delete GoogleIamWorkloadIdentityPoolManagedIdentity#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#update GoogleIamWorkloadIdentityPoolManagedIdentity#update}.
        '''
        value = GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAttestationRules")
    def reset_attestation_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttestationRules", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisabled")
    def reset_disabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisabled", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="attestationRules")
    def attestation_rules(
        self,
    ) -> "GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesList":
        return typing.cast("GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesList", jsii.get(self, "attestationRules"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(
        self,
    ) -> "GoogleIamWorkloadIdentityPoolManagedIdentityTimeoutsOutputReference":
        return typing.cast("GoogleIamWorkloadIdentityPoolManagedIdentityTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="attestationRulesInput")
    def attestation_rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules"]]], jsii.get(self, "attestationRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="disabledInput")
    def disabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disabledInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadIdentityPoolIdInput")
    def workload_identity_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadIdentityPoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadIdentityPoolManagedIdentityIdInput")
    def workload_identity_pool_managed_identity_id_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadIdentityPoolManagedIdentityIdInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadIdentityPoolNamespaceIdInput")
    def workload_identity_pool_namespace_id_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadIdentityPoolNamespaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76acde39eec4bcf897835e508472d7b3692dfb21a3aef8d667774b48d8572a7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disabled")
    def disabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disabled"))

    @disabled.setter
    def disabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cee27cabb6096622faed7a609eccfc89287d9d904255e6d28c6e74f801e3e59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8e5e3f45b6a59edc438d13aef928f00d4af6e0cf7af39bdd8bc35ad76aa799a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a237231426369d39018fcda6b7b57759f3e4093bcfa32a11b05dd871d06de7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadIdentityPoolId")
    def workload_identity_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadIdentityPoolId"))

    @workload_identity_pool_id.setter
    def workload_identity_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__286610cc362b3fc1dd76f8f5d303ac88c621736891433f59c091d9b3a93965cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadIdentityPoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadIdentityPoolManagedIdentityId")
    def workload_identity_pool_managed_identity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadIdentityPoolManagedIdentityId"))

    @workload_identity_pool_managed_identity_id.setter
    def workload_identity_pool_managed_identity_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e94a3021827e762e0bbe827939e3da808b5ddd69b129acc8c3108d7c15020b43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadIdentityPoolManagedIdentityId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadIdentityPoolNamespaceId")
    def workload_identity_pool_namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadIdentityPoolNamespaceId"))

    @workload_identity_pool_namespace_id.setter
    def workload_identity_pool_namespace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbdc61bb11b44e418df8c54a729cee06a047ec550e67726d1025fe685c8139c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadIdentityPoolNamespaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleIamWorkloadIdentityPoolManagedIdentity.GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules",
    jsii_struct_bases=[],
    name_mapping={"google_cloud_resource": "googleCloudResource"},
)
class GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules:
    def __init__(self, *, google_cloud_resource: builtins.str) -> None:
        '''
        :param google_cloud_resource: A single workload operating on Google Cloud. For example: '//compute.googleapis.com/projects/123/uid/zones/us-central1-a/instances/12345678'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#google_cloud_resource GoogleIamWorkloadIdentityPoolManagedIdentity#google_cloud_resource}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffb88f9099bfaa6b4733331a4324470315be2929bf0cdf1720b26e4c26c33f76)
            check_type(argname="argument google_cloud_resource", value=google_cloud_resource, expected_type=type_hints["google_cloud_resource"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "google_cloud_resource": google_cloud_resource,
        }

    @builtins.property
    def google_cloud_resource(self) -> builtins.str:
        '''A single workload operating on Google Cloud. For example: '//compute.googleapis.com/projects/123/uid/zones/us-central1-a/instances/12345678'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#google_cloud_resource GoogleIamWorkloadIdentityPoolManagedIdentity#google_cloud_resource}
        '''
        result = self._values.get("google_cloud_resource")
        assert result is not None, "Required property 'google_cloud_resource' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleIamWorkloadIdentityPoolManagedIdentity.GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b13aa5057a827535d52c99bd3bd75c84120136b3ff02e07a7c9920ebbf6e9cd2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b02b3065f2d24fb3b69c80aea7c213ced871cc3d0667ffd41e25c6410abf9fc6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91dedfadf79ddaa9f400f2c930c28601dd0429033587442468415b01d65c09d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e5cbaa1ce8c13a0fc3b27fb26df3b5051387ec26fd2aa10735e6a8430340ccf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f050c9f2b8dad0ca04478a57b75fc49b28c67794f6ba531cc58e589ed7bedd1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c90a588ca742df1028d47107c8f9d6f2a75081cea8b9dc7131e081c158064ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleIamWorkloadIdentityPoolManagedIdentity.GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__feab9634fe2ff2e29d67377c5419dcb8a2b98226ff875c089ff0ff54445e51ff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="googleCloudResourceInput")
    def google_cloud_resource_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "googleCloudResourceInput"))

    @builtins.property
    @jsii.member(jsii_name="googleCloudResource")
    def google_cloud_resource(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "googleCloudResource"))

    @google_cloud_resource.setter
    def google_cloud_resource(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0723b737d597fd2bc88d11337c586c10f947816c97bce6b8c90f164ff26f32cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "googleCloudResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c80a3327e9395dbbf435778d7b6ebb3a79ac487c3ac332a4ce9b6297448c555c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleIamWorkloadIdentityPoolManagedIdentity.GoogleIamWorkloadIdentityPoolManagedIdentityConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "workload_identity_pool_id": "workloadIdentityPoolId",
        "workload_identity_pool_managed_identity_id": "workloadIdentityPoolManagedIdentityId",
        "workload_identity_pool_namespace_id": "workloadIdentityPoolNamespaceId",
        "attestation_rules": "attestationRules",
        "description": "description",
        "disabled": "disabled",
        "id": "id",
        "project": "project",
        "timeouts": "timeouts",
    },
)
class GoogleIamWorkloadIdentityPoolManagedIdentityConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        workload_identity_pool_id: builtins.str,
        workload_identity_pool_managed_identity_id: builtins.str,
        workload_identity_pool_namespace_id: builtins.str,
        attestation_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param workload_identity_pool_id: The ID to use for the pool, which becomes the final component of the resource name. This value should be 4-32 characters, and may contain the characters [a-z0-9-]. The prefix 'gcp-' is reserved for use by Google, and may not be specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#workload_identity_pool_id GoogleIamWorkloadIdentityPoolManagedIdentity#workload_identity_pool_id}
        :param workload_identity_pool_managed_identity_id: The ID to use for the managed identity. This value must: - contain at most 63 characters - contain only lowercase alphanumeric characters or '-' - start with an alphanumeric character - end with an alphanumeric character The prefix 'gcp-' will be reserved for future uses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#workload_identity_pool_managed_identity_id GoogleIamWorkloadIdentityPoolManagedIdentity#workload_identity_pool_managed_identity_id}
        :param workload_identity_pool_namespace_id: The ID to use for the namespace. This value must: - contain at most 63 characters - contain only lowercase alphanumeric characters or '-' - start with an alphanumeric character - end with an alphanumeric character The prefix 'gcp-' will be reserved for future uses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#workload_identity_pool_namespace_id GoogleIamWorkloadIdentityPoolManagedIdentity#workload_identity_pool_namespace_id}
        :param attestation_rules: attestation_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#attestation_rules GoogleIamWorkloadIdentityPoolManagedIdentity#attestation_rules}
        :param description: A description of the managed identity. Cannot exceed 256 characters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#description GoogleIamWorkloadIdentityPoolManagedIdentity#description}
        :param disabled: Whether the managed identity is disabled. If disabled, credentials may no longer be issued for the identity, however existing credentials will still be accepted until they expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#disabled GoogleIamWorkloadIdentityPoolManagedIdentity#disabled}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#id GoogleIamWorkloadIdentityPoolManagedIdentity#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#project GoogleIamWorkloadIdentityPoolManagedIdentity#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#timeouts GoogleIamWorkloadIdentityPoolManagedIdentity#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28514ba3ee74c072490233ca090e3944ecf1a83c43de508ddf7e4d126e7983a1)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument workload_identity_pool_id", value=workload_identity_pool_id, expected_type=type_hints["workload_identity_pool_id"])
            check_type(argname="argument workload_identity_pool_managed_identity_id", value=workload_identity_pool_managed_identity_id, expected_type=type_hints["workload_identity_pool_managed_identity_id"])
            check_type(argname="argument workload_identity_pool_namespace_id", value=workload_identity_pool_namespace_id, expected_type=type_hints["workload_identity_pool_namespace_id"])
            check_type(argname="argument attestation_rules", value=attestation_rules, expected_type=type_hints["attestation_rules"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disabled", value=disabled, expected_type=type_hints["disabled"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "workload_identity_pool_id": workload_identity_pool_id,
            "workload_identity_pool_managed_identity_id": workload_identity_pool_managed_identity_id,
            "workload_identity_pool_namespace_id": workload_identity_pool_namespace_id,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if attestation_rules is not None:
            self._values["attestation_rules"] = attestation_rules
        if description is not None:
            self._values["description"] = description
        if disabled is not None:
            self._values["disabled"] = disabled
        if id is not None:
            self._values["id"] = id
        if project is not None:
            self._values["project"] = project
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def workload_identity_pool_id(self) -> builtins.str:
        '''The ID to use for the pool, which becomes the final component of the resource name.

        This
        value should be 4-32 characters, and may contain the characters [a-z0-9-]. The prefix
        'gcp-' is reserved for use by Google, and may not be specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#workload_identity_pool_id GoogleIamWorkloadIdentityPoolManagedIdentity#workload_identity_pool_id}
        '''
        result = self._values.get("workload_identity_pool_id")
        assert result is not None, "Required property 'workload_identity_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workload_identity_pool_managed_identity_id(self) -> builtins.str:
        '''The ID to use for the managed identity.

        This value must:

        - contain at most 63 characters
        - contain only lowercase alphanumeric characters or '-'
        - start with an alphanumeric character
        - end with an alphanumeric character

        The prefix 'gcp-' will be reserved for future uses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#workload_identity_pool_managed_identity_id GoogleIamWorkloadIdentityPoolManagedIdentity#workload_identity_pool_managed_identity_id}
        '''
        result = self._values.get("workload_identity_pool_managed_identity_id")
        assert result is not None, "Required property 'workload_identity_pool_managed_identity_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workload_identity_pool_namespace_id(self) -> builtins.str:
        '''The ID to use for the namespace.

        This value must:

        - contain at most 63 characters
        - contain only lowercase alphanumeric characters or '-'
        - start with an alphanumeric character
        - end with an alphanumeric character

        The prefix 'gcp-' will be reserved for future uses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#workload_identity_pool_namespace_id GoogleIamWorkloadIdentityPoolManagedIdentity#workload_identity_pool_namespace_id}
        '''
        result = self._values.get("workload_identity_pool_namespace_id")
        assert result is not None, "Required property 'workload_identity_pool_namespace_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attestation_rules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]]]:
        '''attestation_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#attestation_rules GoogleIamWorkloadIdentityPoolManagedIdentity#attestation_rules}
        '''
        result = self._values.get("attestation_rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the managed identity. Cannot exceed 256 characters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#description GoogleIamWorkloadIdentityPoolManagedIdentity#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether the managed identity is disabled.

        If disabled, credentials may no longer be issued for
        the identity, however existing credentials will still be accepted until they expire.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#disabled GoogleIamWorkloadIdentityPoolManagedIdentity#disabled}
        '''
        result = self._values.get("disabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#id GoogleIamWorkloadIdentityPoolManagedIdentity#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#project GoogleIamWorkloadIdentityPoolManagedIdentity#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(
        self,
    ) -> typing.Optional["GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#timeouts GoogleIamWorkloadIdentityPoolManagedIdentity#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleIamWorkloadIdentityPoolManagedIdentityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleIamWorkloadIdentityPoolManagedIdentity.GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#create GoogleIamWorkloadIdentityPoolManagedIdentity#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#delete GoogleIamWorkloadIdentityPoolManagedIdentity#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#update GoogleIamWorkloadIdentityPoolManagedIdentity#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9b98f864e633d65e9e7b68ef3753a1a6e43f87274c2bc2f8d410aba6d62bbd0)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#create GoogleIamWorkloadIdentityPoolManagedIdentity#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#delete GoogleIamWorkloadIdentityPoolManagedIdentity#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_iam_workload_identity_pool_managed_identity#update GoogleIamWorkloadIdentityPoolManagedIdentity#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleIamWorkloadIdentityPoolManagedIdentityTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleIamWorkloadIdentityPoolManagedIdentity.GoogleIamWorkloadIdentityPoolManagedIdentityTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__322e94da2cc33d7b569dc959e44e2ccd97bf3d9abfefbdfd771e8efc3500349d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60413f8f09caef6c6ceaa9c7d0c23db0da6b6bef257290044b4f0a677ac849be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21a4f53396948789447ae6caffcfb56ab9f6cf2c85cee2876ade3ed494c3917e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ec6b831305edea292a0393a123f695d2b3da5b0475092212ebe36e574248638)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ed0f746badeee4ae43621ad8c26e16ebe69abff8b0c433b4b788bbf3fd3dbb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "GoogleIamWorkloadIdentityPoolManagedIdentity",
    "GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules",
    "GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesList",
    "GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRulesOutputReference",
    "GoogleIamWorkloadIdentityPoolManagedIdentityConfig",
    "GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts",
    "GoogleIamWorkloadIdentityPoolManagedIdentityTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__3b77d08596ff5b7ae649a3974af782d8cf4957e8f2ffc95ff2d266efb7a6f03c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    workload_identity_pool_id: builtins.str,
    workload_identity_pool_managed_identity_id: builtins.str,
    workload_identity_pool_namespace_id: builtins.str,
    attestation_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9926d95bca8e3890a579834379dccc27bf5aba80c177c156dead89399e32e218(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e464e636c789a886293cf833fc39541e8349e591ae2702d8ce538812e9f30dc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76acde39eec4bcf897835e508472d7b3692dfb21a3aef8d667774b48d8572a7f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cee27cabb6096622faed7a609eccfc89287d9d904255e6d28c6e74f801e3e59(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8e5e3f45b6a59edc438d13aef928f00d4af6e0cf7af39bdd8bc35ad76aa799a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a237231426369d39018fcda6b7b57759f3e4093bcfa32a11b05dd871d06de7e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__286610cc362b3fc1dd76f8f5d303ac88c621736891433f59c091d9b3a93965cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e94a3021827e762e0bbe827939e3da808b5ddd69b129acc8c3108d7c15020b43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbdc61bb11b44e418df8c54a729cee06a047ec550e67726d1025fe685c8139c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffb88f9099bfaa6b4733331a4324470315be2929bf0cdf1720b26e4c26c33f76(
    *,
    google_cloud_resource: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b13aa5057a827535d52c99bd3bd75c84120136b3ff02e07a7c9920ebbf6e9cd2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b02b3065f2d24fb3b69c80aea7c213ced871cc3d0667ffd41e25c6410abf9fc6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91dedfadf79ddaa9f400f2c930c28601dd0429033587442468415b01d65c09d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e5cbaa1ce8c13a0fc3b27fb26df3b5051387ec26fd2aa10735e6a8430340ccf(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f050c9f2b8dad0ca04478a57b75fc49b28c67794f6ba531cc58e589ed7bedd1c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c90a588ca742df1028d47107c8f9d6f2a75081cea8b9dc7131e081c158064ab(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__feab9634fe2ff2e29d67377c5419dcb8a2b98226ff875c089ff0ff54445e51ff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0723b737d597fd2bc88d11337c586c10f947816c97bce6b8c90f164ff26f32cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c80a3327e9395dbbf435778d7b6ebb3a79ac487c3ac332a4ce9b6297448c555c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28514ba3ee74c072490233ca090e3944ecf1a83c43de508ddf7e4d126e7983a1(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    workload_identity_pool_id: builtins.str,
    workload_identity_pool_managed_identity_id: builtins.str,
    workload_identity_pool_namespace_id: builtins.str,
    attestation_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleIamWorkloadIdentityPoolManagedIdentityAttestationRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9b98f864e633d65e9e7b68ef3753a1a6e43f87274c2bc2f8d410aba6d62bbd0(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__322e94da2cc33d7b569dc959e44e2ccd97bf3d9abfefbdfd771e8efc3500349d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60413f8f09caef6c6ceaa9c7d0c23db0da6b6bef257290044b4f0a677ac849be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21a4f53396948789447ae6caffcfb56ab9f6cf2c85cee2876ade3ed494c3917e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ec6b831305edea292a0393a123f695d2b3da5b0475092212ebe36e574248638(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ed0f746badeee4ae43621ad8c26e16ebe69abff8b0c433b4b788bbf3fd3dbb7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleIamWorkloadIdentityPoolManagedIdentityTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
