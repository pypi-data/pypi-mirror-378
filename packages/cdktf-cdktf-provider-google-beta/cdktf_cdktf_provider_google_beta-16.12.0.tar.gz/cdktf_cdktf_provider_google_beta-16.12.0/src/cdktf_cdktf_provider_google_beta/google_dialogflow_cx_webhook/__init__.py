r'''
# `google_dialogflow_cx_webhook`

Refer to the Terraform Registry for docs: [`google_dialogflow_cx_webhook`](https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook).
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


class GoogleDialogflowCxWebhook(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhook",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook google_dialogflow_cx_webhook}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        display_name: builtins.str,
        disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_spell_correction: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_stackdriver_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        generic_web_service: typing.Optional[typing.Union["GoogleDialogflowCxWebhookGenericWebService", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        parent: typing.Optional[builtins.str] = None,
        security_settings: typing.Optional[builtins.str] = None,
        service_directory: typing.Optional[typing.Union["GoogleDialogflowCxWebhookServiceDirectory", typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleDialogflowCxWebhookTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook google_dialogflow_cx_webhook} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param display_name: The human-readable name of the webhook, unique within the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#display_name GoogleDialogflowCxWebhook#display_name}
        :param disabled: Indicates whether the webhook is disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#disabled GoogleDialogflowCxWebhook#disabled}
        :param enable_spell_correction: Deprecated. Indicates if automatic spell correction is enabled in detect intent requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#enable_spell_correction GoogleDialogflowCxWebhook#enable_spell_correction}
        :param enable_stackdriver_logging: Deprecated. Determines whether this agent should log conversation queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#enable_stackdriver_logging GoogleDialogflowCxWebhook#enable_stackdriver_logging}
        :param generic_web_service: generic_web_service block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#generic_web_service GoogleDialogflowCxWebhook#generic_web_service}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#id GoogleDialogflowCxWebhook#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parent: The agent to create a webhook for. Format: projects//locations//agents/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#parent GoogleDialogflowCxWebhook#parent}
        :param security_settings: Deprecated. Name of the SecuritySettings reference for the agent. Format: projects//locations//securitySettings/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#security_settings GoogleDialogflowCxWebhook#security_settings}
        :param service_directory: service_directory block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service_directory GoogleDialogflowCxWebhook#service_directory}
        :param timeout: Webhook execution timeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#timeout GoogleDialogflowCxWebhook#timeout}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#timeouts GoogleDialogflowCxWebhook#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c5806cd7ee91cb43ae92e485e436ca32d7f56effa632c11ffc1cfc41aefb67c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GoogleDialogflowCxWebhookConfig(
            display_name=display_name,
            disabled=disabled,
            enable_spell_correction=enable_spell_correction,
            enable_stackdriver_logging=enable_stackdriver_logging,
            generic_web_service=generic_web_service,
            id=id,
            parent=parent,
            security_settings=security_settings,
            service_directory=service_directory,
            timeout=timeout,
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
        '''Generates CDKTF code for importing a GoogleDialogflowCxWebhook resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GoogleDialogflowCxWebhook to import.
        :param import_from_id: The id of the existing GoogleDialogflowCxWebhook that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GoogleDialogflowCxWebhook to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0363add7e1532c6d6784456d35256c41ae9234a35afdf0b7998a65962c79555d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putGenericWebService")
    def put_generic_web_service(
        self,
        *,
        uri: builtins.str,
        allowed_ca_certs: typing.Optional[typing.Sequence[builtins.str]] = None,
        http_method: typing.Optional[builtins.str] = None,
        oauth_config: typing.Optional[typing.Union["GoogleDialogflowCxWebhookGenericWebServiceOauthConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        parameter_mapping: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        request_body: typing.Optional[builtins.str] = None,
        request_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        secret_version_for_username_password: typing.Optional[builtins.str] = None,
        secret_versions_for_request_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_agent_auth: typing.Optional[builtins.str] = None,
        webhook_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param uri: The webhook URI for receiving POST requests. It must use https protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#uri GoogleDialogflowCxWebhook#uri}
        :param allowed_ca_certs: Specifies a list of allowed custom CA certificates (in DER format) for HTTPS verification. This overrides the default SSL trust store. If this is empty or unspecified, Dialogflow will use Google's default trust store to verify certificates. N.B. Make sure the HTTPS server certificates are signed with "subject alt name". For instance a certificate can be self-signed using the following command, openssl x509 -req -days 200 -in example.com.csr -signkey example.com.key -out example.com.crt -extfile <(printf "\\nsubjectAltName='DNS:www.example.com'") Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#allowed_ca_certs GoogleDialogflowCxWebhook#allowed_ca_certs}
        :param http_method: HTTP method for the flexible webhook calls. Standard webhook always uses POST. Possible values: ["POST", "GET", "HEAD", "PUT", "DELETE", "PATCH", "OPTIONS"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#http_method GoogleDialogflowCxWebhook#http_method}
        :param oauth_config: oauth_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#oauth_config GoogleDialogflowCxWebhook#oauth_config}
        :param parameter_mapping: Maps the values extracted from specific fields of the flexible webhook response into session parameters. - Key: session parameter name - Value: field path in the webhook response Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#parameter_mapping GoogleDialogflowCxWebhook#parameter_mapping}
        :param request_body: Defines a custom JSON object as request body to send to flexible webhook. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_body GoogleDialogflowCxWebhook#request_body}
        :param request_headers: The HTTP request headers to send together with webhook requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_headers GoogleDialogflowCxWebhook#request_headers}
        :param secret_version_for_username_password: The SecretManager secret version resource storing the username:password pair for HTTP Basic authentication. Format: 'projects/{project}/secrets/{secret}/versions/{version}'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_username_password GoogleDialogflowCxWebhook#secret_version_for_username_password}
        :param secret_versions_for_request_headers: secret_versions_for_request_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_versions_for_request_headers GoogleDialogflowCxWebhook#secret_versions_for_request_headers}
        :param service_agent_auth: Indicate the auth token type generated from the `Diglogflow service agent <https://cloud.google.com/iam/docs/service-agents#dialogflow-service-agent>`_. The generated token is sent in the Authorization header. Possible values: ["NONE", "ID_TOKEN", "ACCESS_TOKEN"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service_agent_auth GoogleDialogflowCxWebhook#service_agent_auth}
        :param webhook_type: Type of the webhook. Possible values: ["STANDARD", "FLEXIBLE"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#webhook_type GoogleDialogflowCxWebhook#webhook_type}
        '''
        value = GoogleDialogflowCxWebhookGenericWebService(
            uri=uri,
            allowed_ca_certs=allowed_ca_certs,
            http_method=http_method,
            oauth_config=oauth_config,
            parameter_mapping=parameter_mapping,
            request_body=request_body,
            request_headers=request_headers,
            secret_version_for_username_password=secret_version_for_username_password,
            secret_versions_for_request_headers=secret_versions_for_request_headers,
            service_agent_auth=service_agent_auth,
            webhook_type=webhook_type,
        )

        return typing.cast(None, jsii.invoke(self, "putGenericWebService", [value]))

    @jsii.member(jsii_name="putServiceDirectory")
    def put_service_directory(
        self,
        *,
        service: builtins.str,
        generic_web_service: typing.Optional[typing.Union["GoogleDialogflowCxWebhookServiceDirectoryGenericWebService", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param service: The name of Service Directory service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service GoogleDialogflowCxWebhook#service}
        :param generic_web_service: generic_web_service block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#generic_web_service GoogleDialogflowCxWebhook#generic_web_service}
        '''
        value = GoogleDialogflowCxWebhookServiceDirectory(
            service=service, generic_web_service=generic_web_service
        )

        return typing.cast(None, jsii.invoke(self, "putServiceDirectory", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#create GoogleDialogflowCxWebhook#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#delete GoogleDialogflowCxWebhook#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#update GoogleDialogflowCxWebhook#update}.
        '''
        value = GoogleDialogflowCxWebhookTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDisabled")
    def reset_disabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisabled", []))

    @jsii.member(jsii_name="resetEnableSpellCorrection")
    def reset_enable_spell_correction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableSpellCorrection", []))

    @jsii.member(jsii_name="resetEnableStackdriverLogging")
    def reset_enable_stackdriver_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableStackdriverLogging", []))

    @jsii.member(jsii_name="resetGenericWebService")
    def reset_generic_web_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenericWebService", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetParent")
    def reset_parent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParent", []))

    @jsii.member(jsii_name="resetSecuritySettings")
    def reset_security_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecuritySettings", []))

    @jsii.member(jsii_name="resetServiceDirectory")
    def reset_service_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceDirectory", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

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
    @jsii.member(jsii_name="genericWebService")
    def generic_web_service(
        self,
    ) -> "GoogleDialogflowCxWebhookGenericWebServiceOutputReference":
        return typing.cast("GoogleDialogflowCxWebhookGenericWebServiceOutputReference", jsii.get(self, "genericWebService"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="serviceDirectory")
    def service_directory(
        self,
    ) -> "GoogleDialogflowCxWebhookServiceDirectoryOutputReference":
        return typing.cast("GoogleDialogflowCxWebhookServiceDirectoryOutputReference", jsii.get(self, "serviceDirectory"))

    @builtins.property
    @jsii.member(jsii_name="startFlow")
    def start_flow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startFlow"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "GoogleDialogflowCxWebhookTimeoutsOutputReference":
        return typing.cast("GoogleDialogflowCxWebhookTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="disabledInput")
    def disabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disabledInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="enableSpellCorrectionInput")
    def enable_spell_correction_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableSpellCorrectionInput"))

    @builtins.property
    @jsii.member(jsii_name="enableStackdriverLoggingInput")
    def enable_stackdriver_logging_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableStackdriverLoggingInput"))

    @builtins.property
    @jsii.member(jsii_name="genericWebServiceInput")
    def generic_web_service_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxWebhookGenericWebService"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxWebhookGenericWebService"], jsii.get(self, "genericWebServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="parentInput")
    def parent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentInput"))

    @builtins.property
    @jsii.member(jsii_name="securitySettingsInput")
    def security_settings_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securitySettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceDirectoryInput")
    def service_directory_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxWebhookServiceDirectory"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxWebhookServiceDirectory"], jsii.get(self, "serviceDirectoryInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GoogleDialogflowCxWebhookTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GoogleDialogflowCxWebhookTimeouts"]], jsii.get(self, "timeoutsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__57671b22b640d5b96b87ccd15f9980bd31cfb367dcd322cd5925c5a94e4bfda1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__321d18ff8be8f03e0e143dd55e8e12956f3f690095769766711dfa6a7ab3bca7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableSpellCorrection")
    def enable_spell_correction(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableSpellCorrection"))

    @enable_spell_correction.setter
    def enable_spell_correction(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__942ba817cbf27756624b37c32e0ae9d5412415c1fe9f3cefd1dfef2cd5447394)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSpellCorrection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableStackdriverLogging")
    def enable_stackdriver_logging(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableStackdriverLogging"))

    @enable_stackdriver_logging.setter
    def enable_stackdriver_logging(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05537eebe2014d7c56081cbf103598996d12e93ad54fd331f7dcd486de2fe76a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableStackdriverLogging", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ce610a984435010f0e84513cad937faa230f59ba69bf1f82c68ccdb2aa8ea3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parent")
    def parent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parent"))

    @parent.setter
    def parent(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee1b282adf0b59a187fad6d85c8b797b35f6a134cc3c96ec9c75fa455e8d53bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securitySettings")
    def security_settings(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securitySettings"))

    @security_settings.setter
    def security_settings(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d2ce5233268324c1c7dfe9efb83a3f880d102ad206261015a6df85e6dad7232)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securitySettings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e435387e7ebf3fcba26cd196bd7139c1ac14b09c742045277b05637979a91444)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "display_name": "displayName",
        "disabled": "disabled",
        "enable_spell_correction": "enableSpellCorrection",
        "enable_stackdriver_logging": "enableStackdriverLogging",
        "generic_web_service": "genericWebService",
        "id": "id",
        "parent": "parent",
        "security_settings": "securitySettings",
        "service_directory": "serviceDirectory",
        "timeout": "timeout",
        "timeouts": "timeouts",
    },
)
class GoogleDialogflowCxWebhookConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        display_name: builtins.str,
        disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_spell_correction: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_stackdriver_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        generic_web_service: typing.Optional[typing.Union["GoogleDialogflowCxWebhookGenericWebService", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        parent: typing.Optional[builtins.str] = None,
        security_settings: typing.Optional[builtins.str] = None,
        service_directory: typing.Optional[typing.Union["GoogleDialogflowCxWebhookServiceDirectory", typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleDialogflowCxWebhookTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param display_name: The human-readable name of the webhook, unique within the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#display_name GoogleDialogflowCxWebhook#display_name}
        :param disabled: Indicates whether the webhook is disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#disabled GoogleDialogflowCxWebhook#disabled}
        :param enable_spell_correction: Deprecated. Indicates if automatic spell correction is enabled in detect intent requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#enable_spell_correction GoogleDialogflowCxWebhook#enable_spell_correction}
        :param enable_stackdriver_logging: Deprecated. Determines whether this agent should log conversation queries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#enable_stackdriver_logging GoogleDialogflowCxWebhook#enable_stackdriver_logging}
        :param generic_web_service: generic_web_service block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#generic_web_service GoogleDialogflowCxWebhook#generic_web_service}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#id GoogleDialogflowCxWebhook#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parent: The agent to create a webhook for. Format: projects//locations//agents/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#parent GoogleDialogflowCxWebhook#parent}
        :param security_settings: Deprecated. Name of the SecuritySettings reference for the agent. Format: projects//locations//securitySettings/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#security_settings GoogleDialogflowCxWebhook#security_settings}
        :param service_directory: service_directory block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service_directory GoogleDialogflowCxWebhook#service_directory}
        :param timeout: Webhook execution timeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#timeout GoogleDialogflowCxWebhook#timeout}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#timeouts GoogleDialogflowCxWebhook#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(generic_web_service, dict):
            generic_web_service = GoogleDialogflowCxWebhookGenericWebService(**generic_web_service)
        if isinstance(service_directory, dict):
            service_directory = GoogleDialogflowCxWebhookServiceDirectory(**service_directory)
        if isinstance(timeouts, dict):
            timeouts = GoogleDialogflowCxWebhookTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05bd9ad21b40a120f3ad77aebd59e16e0566fd93fe14321ba3ac8bffdcda4bc4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument disabled", value=disabled, expected_type=type_hints["disabled"])
            check_type(argname="argument enable_spell_correction", value=enable_spell_correction, expected_type=type_hints["enable_spell_correction"])
            check_type(argname="argument enable_stackdriver_logging", value=enable_stackdriver_logging, expected_type=type_hints["enable_stackdriver_logging"])
            check_type(argname="argument generic_web_service", value=generic_web_service, expected_type=type_hints["generic_web_service"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument security_settings", value=security_settings, expected_type=type_hints["security_settings"])
            check_type(argname="argument service_directory", value=service_directory, expected_type=type_hints["service_directory"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "display_name": display_name,
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
        if disabled is not None:
            self._values["disabled"] = disabled
        if enable_spell_correction is not None:
            self._values["enable_spell_correction"] = enable_spell_correction
        if enable_stackdriver_logging is not None:
            self._values["enable_stackdriver_logging"] = enable_stackdriver_logging
        if generic_web_service is not None:
            self._values["generic_web_service"] = generic_web_service
        if id is not None:
            self._values["id"] = id
        if parent is not None:
            self._values["parent"] = parent
        if security_settings is not None:
            self._values["security_settings"] = security_settings
        if service_directory is not None:
            self._values["service_directory"] = service_directory
        if timeout is not None:
            self._values["timeout"] = timeout
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
    def display_name(self) -> builtins.str:
        '''The human-readable name of the webhook, unique within the agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#display_name GoogleDialogflowCxWebhook#display_name}
        '''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def disabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether the webhook is disabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#disabled GoogleDialogflowCxWebhook#disabled}
        '''
        result = self._values.get("disabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_spell_correction(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Deprecated. Indicates if automatic spell correction is enabled in detect intent requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#enable_spell_correction GoogleDialogflowCxWebhook#enable_spell_correction}
        '''
        result = self._values.get("enable_spell_correction")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_stackdriver_logging(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Deprecated. Determines whether this agent should log conversation queries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#enable_stackdriver_logging GoogleDialogflowCxWebhook#enable_stackdriver_logging}
        '''
        result = self._values.get("enable_stackdriver_logging")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def generic_web_service(
        self,
    ) -> typing.Optional["GoogleDialogflowCxWebhookGenericWebService"]:
        '''generic_web_service block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#generic_web_service GoogleDialogflowCxWebhook#generic_web_service}
        '''
        result = self._values.get("generic_web_service")
        return typing.cast(typing.Optional["GoogleDialogflowCxWebhookGenericWebService"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#id GoogleDialogflowCxWebhook#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[builtins.str]:
        '''The agent to create a webhook for. Format: projects//locations//agents/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#parent GoogleDialogflowCxWebhook#parent}
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_settings(self) -> typing.Optional[builtins.str]:
        '''Deprecated. Name of the SecuritySettings reference for the agent. Format: projects//locations//securitySettings/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#security_settings GoogleDialogflowCxWebhook#security_settings}
        '''
        result = self._values.get("security_settings")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_directory(
        self,
    ) -> typing.Optional["GoogleDialogflowCxWebhookServiceDirectory"]:
        '''service_directory block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service_directory GoogleDialogflowCxWebhook#service_directory}
        '''
        result = self._values.get("service_directory")
        return typing.cast(typing.Optional["GoogleDialogflowCxWebhookServiceDirectory"], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''Webhook execution timeout.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#timeout GoogleDialogflowCxWebhook#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GoogleDialogflowCxWebhookTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#timeouts GoogleDialogflowCxWebhook#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GoogleDialogflowCxWebhookTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxWebhookConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookGenericWebService",
    jsii_struct_bases=[],
    name_mapping={
        "uri": "uri",
        "allowed_ca_certs": "allowedCaCerts",
        "http_method": "httpMethod",
        "oauth_config": "oauthConfig",
        "parameter_mapping": "parameterMapping",
        "request_body": "requestBody",
        "request_headers": "requestHeaders",
        "secret_version_for_username_password": "secretVersionForUsernamePassword",
        "secret_versions_for_request_headers": "secretVersionsForRequestHeaders",
        "service_agent_auth": "serviceAgentAuth",
        "webhook_type": "webhookType",
    },
)
class GoogleDialogflowCxWebhookGenericWebService:
    def __init__(
        self,
        *,
        uri: builtins.str,
        allowed_ca_certs: typing.Optional[typing.Sequence[builtins.str]] = None,
        http_method: typing.Optional[builtins.str] = None,
        oauth_config: typing.Optional[typing.Union["GoogleDialogflowCxWebhookGenericWebServiceOauthConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        parameter_mapping: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        request_body: typing.Optional[builtins.str] = None,
        request_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        secret_version_for_username_password: typing.Optional[builtins.str] = None,
        secret_versions_for_request_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_agent_auth: typing.Optional[builtins.str] = None,
        webhook_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param uri: The webhook URI for receiving POST requests. It must use https protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#uri GoogleDialogflowCxWebhook#uri}
        :param allowed_ca_certs: Specifies a list of allowed custom CA certificates (in DER format) for HTTPS verification. This overrides the default SSL trust store. If this is empty or unspecified, Dialogflow will use Google's default trust store to verify certificates. N.B. Make sure the HTTPS server certificates are signed with "subject alt name". For instance a certificate can be self-signed using the following command, openssl x509 -req -days 200 -in example.com.csr -signkey example.com.key -out example.com.crt -extfile <(printf "\\nsubjectAltName='DNS:www.example.com'") Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#allowed_ca_certs GoogleDialogflowCxWebhook#allowed_ca_certs}
        :param http_method: HTTP method for the flexible webhook calls. Standard webhook always uses POST. Possible values: ["POST", "GET", "HEAD", "PUT", "DELETE", "PATCH", "OPTIONS"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#http_method GoogleDialogflowCxWebhook#http_method}
        :param oauth_config: oauth_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#oauth_config GoogleDialogflowCxWebhook#oauth_config}
        :param parameter_mapping: Maps the values extracted from specific fields of the flexible webhook response into session parameters. - Key: session parameter name - Value: field path in the webhook response Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#parameter_mapping GoogleDialogflowCxWebhook#parameter_mapping}
        :param request_body: Defines a custom JSON object as request body to send to flexible webhook. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_body GoogleDialogflowCxWebhook#request_body}
        :param request_headers: The HTTP request headers to send together with webhook requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_headers GoogleDialogflowCxWebhook#request_headers}
        :param secret_version_for_username_password: The SecretManager secret version resource storing the username:password pair for HTTP Basic authentication. Format: 'projects/{project}/secrets/{secret}/versions/{version}'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_username_password GoogleDialogflowCxWebhook#secret_version_for_username_password}
        :param secret_versions_for_request_headers: secret_versions_for_request_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_versions_for_request_headers GoogleDialogflowCxWebhook#secret_versions_for_request_headers}
        :param service_agent_auth: Indicate the auth token type generated from the `Diglogflow service agent <https://cloud.google.com/iam/docs/service-agents#dialogflow-service-agent>`_. The generated token is sent in the Authorization header. Possible values: ["NONE", "ID_TOKEN", "ACCESS_TOKEN"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service_agent_auth GoogleDialogflowCxWebhook#service_agent_auth}
        :param webhook_type: Type of the webhook. Possible values: ["STANDARD", "FLEXIBLE"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#webhook_type GoogleDialogflowCxWebhook#webhook_type}
        '''
        if isinstance(oauth_config, dict):
            oauth_config = GoogleDialogflowCxWebhookGenericWebServiceOauthConfig(**oauth_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aa3096505ab0805b17fab5fedb8b01817af1d2d6b0bca87e5fc88f402c40e0f)
            check_type(argname="argument uri", value=uri, expected_type=type_hints["uri"])
            check_type(argname="argument allowed_ca_certs", value=allowed_ca_certs, expected_type=type_hints["allowed_ca_certs"])
            check_type(argname="argument http_method", value=http_method, expected_type=type_hints["http_method"])
            check_type(argname="argument oauth_config", value=oauth_config, expected_type=type_hints["oauth_config"])
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
            check_type(argname="argument request_body", value=request_body, expected_type=type_hints["request_body"])
            check_type(argname="argument request_headers", value=request_headers, expected_type=type_hints["request_headers"])
            check_type(argname="argument secret_version_for_username_password", value=secret_version_for_username_password, expected_type=type_hints["secret_version_for_username_password"])
            check_type(argname="argument secret_versions_for_request_headers", value=secret_versions_for_request_headers, expected_type=type_hints["secret_versions_for_request_headers"])
            check_type(argname="argument service_agent_auth", value=service_agent_auth, expected_type=type_hints["service_agent_auth"])
            check_type(argname="argument webhook_type", value=webhook_type, expected_type=type_hints["webhook_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "uri": uri,
        }
        if allowed_ca_certs is not None:
            self._values["allowed_ca_certs"] = allowed_ca_certs
        if http_method is not None:
            self._values["http_method"] = http_method
        if oauth_config is not None:
            self._values["oauth_config"] = oauth_config
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if request_body is not None:
            self._values["request_body"] = request_body
        if request_headers is not None:
            self._values["request_headers"] = request_headers
        if secret_version_for_username_password is not None:
            self._values["secret_version_for_username_password"] = secret_version_for_username_password
        if secret_versions_for_request_headers is not None:
            self._values["secret_versions_for_request_headers"] = secret_versions_for_request_headers
        if service_agent_auth is not None:
            self._values["service_agent_auth"] = service_agent_auth
        if webhook_type is not None:
            self._values["webhook_type"] = webhook_type

    @builtins.property
    def uri(self) -> builtins.str:
        '''The webhook URI for receiving POST requests. It must use https protocol.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#uri GoogleDialogflowCxWebhook#uri}
        '''
        result = self._values.get("uri")
        assert result is not None, "Required property 'uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_ca_certs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies a list of allowed custom CA certificates (in DER format) for HTTPS verification.

        This overrides the default SSL trust store. If this
        is empty or unspecified, Dialogflow will use Google's default trust store
        to verify certificates.
        N.B. Make sure the HTTPS server certificates are signed with "subject alt
        name". For instance a certificate can be self-signed using the following
        command,
        openssl x509 -req -days 200 -in example.com.csr
        -signkey example.com.key
        -out example.com.crt
        -extfile <(printf "\\nsubjectAltName='DNS:www.example.com'")

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#allowed_ca_certs GoogleDialogflowCxWebhook#allowed_ca_certs}
        '''
        result = self._values.get("allowed_ca_certs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def http_method(self) -> typing.Optional[builtins.str]:
        '''HTTP method for the flexible webhook calls.

        Standard webhook always uses
        POST. Possible values: ["POST", "GET", "HEAD", "PUT", "DELETE", "PATCH", "OPTIONS"]

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#http_method GoogleDialogflowCxWebhook#http_method}
        '''
        result = self._values.get("http_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oauth_config(
        self,
    ) -> typing.Optional["GoogleDialogflowCxWebhookGenericWebServiceOauthConfig"]:
        '''oauth_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#oauth_config GoogleDialogflowCxWebhook#oauth_config}
        '''
        result = self._values.get("oauth_config")
        return typing.cast(typing.Optional["GoogleDialogflowCxWebhookGenericWebServiceOauthConfig"], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Maps the values extracted from specific fields of the flexible webhook response into session parameters.

        - Key: session parameter name
        - Value: field path in the webhook response

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#parameter_mapping GoogleDialogflowCxWebhook#parameter_mapping}
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def request_body(self) -> typing.Optional[builtins.str]:
        '''Defines a custom JSON object as request body to send to flexible webhook.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_body GoogleDialogflowCxWebhook#request_body}
        '''
        result = self._values.get("request_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_headers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The HTTP request headers to send together with webhook requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_headers GoogleDialogflowCxWebhook#request_headers}
        '''
        result = self._values.get("request_headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def secret_version_for_username_password(self) -> typing.Optional[builtins.str]:
        '''The SecretManager secret version resource storing the username:password pair for HTTP Basic authentication. Format: 'projects/{project}/secrets/{secret}/versions/{version}'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_username_password GoogleDialogflowCxWebhook#secret_version_for_username_password}
        '''
        result = self._values.get("secret_version_for_username_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_versions_for_request_headers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders"]]]:
        '''secret_versions_for_request_headers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_versions_for_request_headers GoogleDialogflowCxWebhook#secret_versions_for_request_headers}
        '''
        result = self._values.get("secret_versions_for_request_headers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders"]]], result)

    @builtins.property
    def service_agent_auth(self) -> typing.Optional[builtins.str]:
        '''Indicate the auth token type generated from the `Diglogflow service agent <https://cloud.google.com/iam/docs/service-agents#dialogflow-service-agent>`_. The generated token is sent in the Authorization header. Possible values: ["NONE", "ID_TOKEN", "ACCESS_TOKEN"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service_agent_auth GoogleDialogflowCxWebhook#service_agent_auth}
        '''
        result = self._values.get("service_agent_auth")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook_type(self) -> typing.Optional[builtins.str]:
        '''Type of the webhook. Possible values: ["STANDARD", "FLEXIBLE"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#webhook_type GoogleDialogflowCxWebhook#webhook_type}
        '''
        result = self._values.get("webhook_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxWebhookGenericWebService(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookGenericWebServiceOauthConfig",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "token_endpoint": "tokenEndpoint",
        "client_secret": "clientSecret",
        "scopes": "scopes",
        "secret_version_for_client_secret": "secretVersionForClientSecret",
    },
)
class GoogleDialogflowCxWebhookGenericWebServiceOauthConfig:
    def __init__(
        self,
        *,
        client_id: builtins.str,
        token_endpoint: builtins.str,
        client_secret: typing.Optional[builtins.str] = None,
        scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        secret_version_for_client_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_id: The client ID provided by the 3rd party platform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_id GoogleDialogflowCxWebhook#client_id}
        :param token_endpoint: The token endpoint provided by the 3rd party platform to exchange an access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#token_endpoint GoogleDialogflowCxWebhook#token_endpoint}
        :param client_secret: The client secret provided by the 3rd party platform. If the 'secret_version_for_client_secret' field is set, this field will be ignored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_secret GoogleDialogflowCxWebhook#client_secret}
        :param scopes: The OAuth scopes to grant. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#scopes GoogleDialogflowCxWebhook#scopes}
        :param secret_version_for_client_secret: The name of the SecretManager secret version resource storing the client secret. If this field is set, the 'client_secret' field will be ignored. Format: 'projects/{project}/secrets/{secret}/versions/{version}' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_client_secret GoogleDialogflowCxWebhook#secret_version_for_client_secret}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95d2edce5f684d55df12319800ef86e1f726056d35467b8d66178cae78c9d0d5)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument token_endpoint", value=token_endpoint, expected_type=type_hints["token_endpoint"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument scopes", value=scopes, expected_type=type_hints["scopes"])
            check_type(argname="argument secret_version_for_client_secret", value=secret_version_for_client_secret, expected_type=type_hints["secret_version_for_client_secret"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client_id": client_id,
            "token_endpoint": token_endpoint,
        }
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if scopes is not None:
            self._values["scopes"] = scopes
        if secret_version_for_client_secret is not None:
            self._values["secret_version_for_client_secret"] = secret_version_for_client_secret

    @builtins.property
    def client_id(self) -> builtins.str:
        '''The client ID provided by the 3rd party platform.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_id GoogleDialogflowCxWebhook#client_id}
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def token_endpoint(self) -> builtins.str:
        '''The token endpoint provided by the 3rd party platform to exchange an access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#token_endpoint GoogleDialogflowCxWebhook#token_endpoint}
        '''
        result = self._values.get("token_endpoint")
        assert result is not None, "Required property 'token_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_secret(self) -> typing.Optional[builtins.str]:
        '''The client secret provided by the 3rd party platform.  If the 'secret_version_for_client_secret' field is set, this field will be ignored.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_secret GoogleDialogflowCxWebhook#client_secret}
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The OAuth scopes to grant.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#scopes GoogleDialogflowCxWebhook#scopes}
        '''
        result = self._values.get("scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secret_version_for_client_secret(self) -> typing.Optional[builtins.str]:
        '''The name of the SecretManager secret version resource storing the client secret.

        If this field is set, the 'client_secret' field will be
        ignored.
        Format: 'projects/{project}/secrets/{secret}/versions/{version}'

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_client_secret GoogleDialogflowCxWebhook#secret_version_for_client_secret}
        '''
        result = self._values.get("secret_version_for_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxWebhookGenericWebServiceOauthConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxWebhookGenericWebServiceOauthConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookGenericWebServiceOauthConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3c0487606d9cf3298a08550ac7265509af6e85738248188ad15554c92d1f10e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetClientSecret")
    def reset_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientSecret", []))

    @jsii.member(jsii_name="resetScopes")
    def reset_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScopes", []))

    @jsii.member(jsii_name="resetSecretVersionForClientSecret")
    def reset_secret_version_for_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretVersionForClientSecret", []))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="scopesInput")
    def scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "scopesInput"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionForClientSecretInput")
    def secret_version_for_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretVersionForClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenEndpointInput")
    def token_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__580e126362b7bd88df94f393070434b298ad566845848b0e2f0a688a2fbdb728)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93f89eae03960d284e96bcfb0af9c883b97b45431b3fe9e446687cd6b61fac8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scopes")
    def scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "scopes"))

    @scopes.setter
    def scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e98523370a27c2ec684a07aaba2a9d2d425d6282d4275db6aca07dd88c5194d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scopes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretVersionForClientSecret")
    def secret_version_for_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretVersionForClientSecret"))

    @secret_version_for_client_secret.setter
    def secret_version_for_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6e549d69d7f911c76d9fb08043598ccc8c64c5675e539f30e4eed7f99926e85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretVersionForClientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenEndpoint")
    def token_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenEndpoint"))

    @token_endpoint.setter
    def token_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__096cf9b6d2473560f74fb8d7145e4718c87f1ba8b10894388d01c6bb718ba3a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxWebhookGenericWebServiceOauthConfig]:
        return typing.cast(typing.Optional[GoogleDialogflowCxWebhookGenericWebServiceOauthConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxWebhookGenericWebServiceOauthConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c1bf77b6c8317e702277e1d363a32471c13b628eeb38070f0771f4a87762ebb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GoogleDialogflowCxWebhookGenericWebServiceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookGenericWebServiceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a1f0ac1f0ec0283ff2f958fc324ef171a3a0bdd949959f659b4b6a1de278ee1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOauthConfig")
    def put_oauth_config(
        self,
        *,
        client_id: builtins.str,
        token_endpoint: builtins.str,
        client_secret: typing.Optional[builtins.str] = None,
        scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        secret_version_for_client_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_id: The client ID provided by the 3rd party platform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_id GoogleDialogflowCxWebhook#client_id}
        :param token_endpoint: The token endpoint provided by the 3rd party platform to exchange an access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#token_endpoint GoogleDialogflowCxWebhook#token_endpoint}
        :param client_secret: The client secret provided by the 3rd party platform. If the 'secret_version_for_client_secret' field is set, this field will be ignored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_secret GoogleDialogflowCxWebhook#client_secret}
        :param scopes: The OAuth scopes to grant. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#scopes GoogleDialogflowCxWebhook#scopes}
        :param secret_version_for_client_secret: The name of the SecretManager secret version resource storing the client secret. If this field is set, the 'client_secret' field will be ignored. Format: 'projects/{project}/secrets/{secret}/versions/{version}' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_client_secret GoogleDialogflowCxWebhook#secret_version_for_client_secret}
        '''
        value = GoogleDialogflowCxWebhookGenericWebServiceOauthConfig(
            client_id=client_id,
            token_endpoint=token_endpoint,
            client_secret=client_secret,
            scopes=scopes,
            secret_version_for_client_secret=secret_version_for_client_secret,
        )

        return typing.cast(None, jsii.invoke(self, "putOauthConfig", [value]))

    @jsii.member(jsii_name="putSecretVersionsForRequestHeaders")
    def put_secret_versions_for_request_headers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e7c2afb557234bf3d5017dd79476b08faf91aec6efb6e83264d3867ddd9381d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSecretVersionsForRequestHeaders", [value]))

    @jsii.member(jsii_name="resetAllowedCaCerts")
    def reset_allowed_ca_certs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedCaCerts", []))

    @jsii.member(jsii_name="resetHttpMethod")
    def reset_http_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMethod", []))

    @jsii.member(jsii_name="resetOauthConfig")
    def reset_oauth_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOauthConfig", []))

    @jsii.member(jsii_name="resetParameterMapping")
    def reset_parameter_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterMapping", []))

    @jsii.member(jsii_name="resetRequestBody")
    def reset_request_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestBody", []))

    @jsii.member(jsii_name="resetRequestHeaders")
    def reset_request_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestHeaders", []))

    @jsii.member(jsii_name="resetSecretVersionForUsernamePassword")
    def reset_secret_version_for_username_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretVersionForUsernamePassword", []))

    @jsii.member(jsii_name="resetSecretVersionsForRequestHeaders")
    def reset_secret_versions_for_request_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretVersionsForRequestHeaders", []))

    @jsii.member(jsii_name="resetServiceAgentAuth")
    def reset_service_agent_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAgentAuth", []))

    @jsii.member(jsii_name="resetWebhookType")
    def reset_webhook_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebhookType", []))

    @builtins.property
    @jsii.member(jsii_name="oauthConfig")
    def oauth_config(
        self,
    ) -> GoogleDialogflowCxWebhookGenericWebServiceOauthConfigOutputReference:
        return typing.cast(GoogleDialogflowCxWebhookGenericWebServiceOauthConfigOutputReference, jsii.get(self, "oauthConfig"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionsForRequestHeaders")
    def secret_versions_for_request_headers(
        self,
    ) -> "GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersList":
        return typing.cast("GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersList", jsii.get(self, "secretVersionsForRequestHeaders"))

    @builtins.property
    @jsii.member(jsii_name="allowedCaCertsInput")
    def allowed_ca_certs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedCaCertsInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMethodInput")
    def http_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="oauthConfigInput")
    def oauth_config_input(
        self,
    ) -> typing.Optional[GoogleDialogflowCxWebhookGenericWebServiceOauthConfig]:
        return typing.cast(typing.Optional[GoogleDialogflowCxWebhookGenericWebServiceOauthConfig], jsii.get(self, "oauthConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterMappingInput")
    def parameter_mapping_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parameterMappingInput"))

    @builtins.property
    @jsii.member(jsii_name="requestBodyInput")
    def request_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestBodyInput"))

    @builtins.property
    @jsii.member(jsii_name="requestHeadersInput")
    def request_headers_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "requestHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionForUsernamePasswordInput")
    def secret_version_for_username_password_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretVersionForUsernamePasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionsForRequestHeadersInput")
    def secret_versions_for_request_headers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders"]]], jsii.get(self, "secretVersionsForRequestHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAgentAuthInput")
    def service_agent_auth_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAgentAuthInput"))

    @builtins.property
    @jsii.member(jsii_name="uriInput")
    def uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uriInput"))

    @builtins.property
    @jsii.member(jsii_name="webhookTypeInput")
    def webhook_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webhookTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedCaCerts")
    def allowed_ca_certs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedCaCerts"))

    @allowed_ca_certs.setter
    def allowed_ca_certs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6822965fad90a166781d318ba06eb9648d4cc32e9d1865ce849222c2c233443)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedCaCerts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpMethod")
    def http_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpMethod"))

    @http_method.setter
    def http_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19f4e03a8613270268a216c382125ff7efc6054eeba8e7114c311c8edd207a47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterMapping")
    def parameter_mapping(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "parameterMapping"))

    @parameter_mapping.setter
    def parameter_mapping(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07ac4ac98a9f8bb84fa94d020fc3a70c3a2278edc56e0b431e15c30783e05be8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterMapping", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestBody")
    def request_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestBody"))

    @request_body.setter
    def request_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29b9f92871c1e8b58d0aba8b858376a88df1b0010bc18ef158f2aedf452b6a1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestBody", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestHeaders")
    def request_headers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "requestHeaders"))

    @request_headers.setter
    def request_headers(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ae33de3e4579dc3d53a88b40986a304815500553820a7a16a06c457afdc74a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretVersionForUsernamePassword")
    def secret_version_for_username_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretVersionForUsernamePassword"))

    @secret_version_for_username_password.setter
    def secret_version_for_username_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c24253aec12b1485f4b48bafddfa2e525398590cca41ce0d53b61ad1914892)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretVersionForUsernamePassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAgentAuth")
    def service_agent_auth(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAgentAuth"))

    @service_agent_auth.setter
    def service_agent_auth(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d298b6eb905f5e17467b55773bda8ae811bec9dd927c6531933e141b1e8cb0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAgentAuth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @uri.setter
    def uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb001615a7dd398afadb6bc645d8a1dca638d02cb0219a349097fd439208f3c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="webhookType")
    def webhook_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhookType"))

    @webhook_type.setter
    def webhook_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80de606a07b378aa2ec27e10ac609b379cc83b37804e5b097b08e5faa16782d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhookType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxWebhookGenericWebService]:
        return typing.cast(typing.Optional[GoogleDialogflowCxWebhookGenericWebService], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxWebhookGenericWebService],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac5fff4d28d67df44331ec98262be9adf9d155ad26bd8584f10ce1a28c73c9e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "secret_version": "secretVersion"},
)
class GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders:
    def __init__(self, *, key: builtins.str, secret_version: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#key GoogleDialogflowCxWebhook#key}.
        :param secret_version: The SecretManager secret version resource storing the header value. Format: 'projects/{project}/secrets/{secret}/versions/{version}'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version GoogleDialogflowCxWebhook#secret_version}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38b86b9c4a9abed44f621f44c4db2eb01690504af6eab90fa80bf44874972138)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument secret_version", value=secret_version, expected_type=type_hints["secret_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "secret_version": secret_version,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#key GoogleDialogflowCxWebhook#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_version(self) -> builtins.str:
        '''The SecretManager secret version resource storing the header value. Format: 'projects/{project}/secrets/{secret}/versions/{version}'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version GoogleDialogflowCxWebhook#secret_version}
        '''
        result = self._values.get("secret_version")
        assert result is not None, "Required property 'secret_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba34265d7292e863451e3b52645e972925592583b179864f10e98acafda5c50c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e539fcafad45342366e2b5aa5f431734aaf74338461a37f21ef474b2281360a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33bf529d839725020a09f9503d2e4ef713bcb160b6f9eab08076624ad205cfa2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__18ade9eda3780f2835d4fa45eb33b7abb5b7c713d47eb20aaf7f7ca03a921b76)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7742ee9e3b01bfd9fff46c0c583e1d4c58c133ac4e73447f3c18ad1b5e283057)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4aa14dd17568351a43a7753cb81952212e3fbe89cde4277cb6e2a34a870a42e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f7813dde15e894b87aa4adf5864e3fe8bd64ee0c250c5674d2464521139e09e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionInput")
    def secret_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dfb8470f3fd53c05955d9ff1a3fb85e003876f2987be392336b1ea335d7981e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretVersion")
    def secret_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretVersion"))

    @secret_version.setter
    def secret_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a976d5b4a0fb416f1dbcc3f3ee9c854e116cdac80545272598ae6d737748e4c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b282d5a5e08303c6b307cdb95443dcdccc6863513dd1b38f88d4347ffeabe33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookServiceDirectory",
    jsii_struct_bases=[],
    name_mapping={"service": "service", "generic_web_service": "genericWebService"},
)
class GoogleDialogflowCxWebhookServiceDirectory:
    def __init__(
        self,
        *,
        service: builtins.str,
        generic_web_service: typing.Optional[typing.Union["GoogleDialogflowCxWebhookServiceDirectoryGenericWebService", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param service: The name of Service Directory service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service GoogleDialogflowCxWebhook#service}
        :param generic_web_service: generic_web_service block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#generic_web_service GoogleDialogflowCxWebhook#generic_web_service}
        '''
        if isinstance(generic_web_service, dict):
            generic_web_service = GoogleDialogflowCxWebhookServiceDirectoryGenericWebService(**generic_web_service)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcb22ef256d963bcde3c55ce3d30a6480b8621171f06886a793fef462614bf3c)
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument generic_web_service", value=generic_web_service, expected_type=type_hints["generic_web_service"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service": service,
        }
        if generic_web_service is not None:
            self._values["generic_web_service"] = generic_web_service

    @builtins.property
    def service(self) -> builtins.str:
        '''The name of Service Directory service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service GoogleDialogflowCxWebhook#service}
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def generic_web_service(
        self,
    ) -> typing.Optional["GoogleDialogflowCxWebhookServiceDirectoryGenericWebService"]:
        '''generic_web_service block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#generic_web_service GoogleDialogflowCxWebhook#generic_web_service}
        '''
        result = self._values.get("generic_web_service")
        return typing.cast(typing.Optional["GoogleDialogflowCxWebhookServiceDirectoryGenericWebService"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxWebhookServiceDirectory(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookServiceDirectoryGenericWebService",
    jsii_struct_bases=[],
    name_mapping={
        "uri": "uri",
        "allowed_ca_certs": "allowedCaCerts",
        "http_method": "httpMethod",
        "oauth_config": "oauthConfig",
        "parameter_mapping": "parameterMapping",
        "request_body": "requestBody",
        "request_headers": "requestHeaders",
        "secret_version_for_username_password": "secretVersionForUsernamePassword",
        "secret_versions_for_request_headers": "secretVersionsForRequestHeaders",
        "service_agent_auth": "serviceAgentAuth",
        "webhook_type": "webhookType",
    },
)
class GoogleDialogflowCxWebhookServiceDirectoryGenericWebService:
    def __init__(
        self,
        *,
        uri: builtins.str,
        allowed_ca_certs: typing.Optional[typing.Sequence[builtins.str]] = None,
        http_method: typing.Optional[builtins.str] = None,
        oauth_config: typing.Optional[typing.Union["GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        parameter_mapping: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        request_body: typing.Optional[builtins.str] = None,
        request_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        secret_version_for_username_password: typing.Optional[builtins.str] = None,
        secret_versions_for_request_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_agent_auth: typing.Optional[builtins.str] = None,
        webhook_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param uri: The webhook URI for receiving POST requests. It must use https protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#uri GoogleDialogflowCxWebhook#uri}
        :param allowed_ca_certs: Specifies a list of allowed custom CA certificates (in DER format) for HTTPS verification. This overrides the default SSL trust store. If this is empty or unspecified, Dialogflow will use Google's default trust store to verify certificates. N.B. Make sure the HTTPS server certificates are signed with "subject alt name". For instance a certificate can be self-signed using the following command, openssl x509 -req -days 200 -in example.com.csr -signkey example.com.key -out example.com.crt -extfile <(printf "\\nsubjectAltName='DNS:www.example.com'") Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#allowed_ca_certs GoogleDialogflowCxWebhook#allowed_ca_certs}
        :param http_method: HTTP method for the flexible webhook calls. Standard webhook always uses POST. Possible values: ["POST", "GET", "HEAD", "PUT", "DELETE", "PATCH", "OPTIONS"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#http_method GoogleDialogflowCxWebhook#http_method}
        :param oauth_config: oauth_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#oauth_config GoogleDialogflowCxWebhook#oauth_config}
        :param parameter_mapping: Maps the values extracted from specific fields of the flexible webhook response into session parameters. - Key: session parameter name - Value: field path in the webhook response Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#parameter_mapping GoogleDialogflowCxWebhook#parameter_mapping}
        :param request_body: Defines a custom JSON object as request body to send to flexible webhook. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_body GoogleDialogflowCxWebhook#request_body}
        :param request_headers: The HTTP request headers to send together with webhook requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_headers GoogleDialogflowCxWebhook#request_headers}
        :param secret_version_for_username_password: The SecretManager secret version resource storing the username:password pair for HTTP Basic authentication. Format: 'projects/{project}/secrets/{secret}/versions/{version}'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_username_password GoogleDialogflowCxWebhook#secret_version_for_username_password}
        :param secret_versions_for_request_headers: secret_versions_for_request_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_versions_for_request_headers GoogleDialogflowCxWebhook#secret_versions_for_request_headers}
        :param service_agent_auth: Indicate the auth token type generated from the `Diglogflow service agent <https://cloud.google.com/iam/docs/service-agents#dialogflow-service-agent>`_. The generated token is sent in the Authorization header. Possible values: ["NONE", "ID_TOKEN", "ACCESS_TOKEN"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service_agent_auth GoogleDialogflowCxWebhook#service_agent_auth}
        :param webhook_type: Type of the webhook. Possible values: ["STANDARD", "FLEXIBLE"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#webhook_type GoogleDialogflowCxWebhook#webhook_type}
        '''
        if isinstance(oauth_config, dict):
            oauth_config = GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig(**oauth_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6a19ec7026934de48fe2d290472f6ce99709968888b0166f01be172fbc47e3f)
            check_type(argname="argument uri", value=uri, expected_type=type_hints["uri"])
            check_type(argname="argument allowed_ca_certs", value=allowed_ca_certs, expected_type=type_hints["allowed_ca_certs"])
            check_type(argname="argument http_method", value=http_method, expected_type=type_hints["http_method"])
            check_type(argname="argument oauth_config", value=oauth_config, expected_type=type_hints["oauth_config"])
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
            check_type(argname="argument request_body", value=request_body, expected_type=type_hints["request_body"])
            check_type(argname="argument request_headers", value=request_headers, expected_type=type_hints["request_headers"])
            check_type(argname="argument secret_version_for_username_password", value=secret_version_for_username_password, expected_type=type_hints["secret_version_for_username_password"])
            check_type(argname="argument secret_versions_for_request_headers", value=secret_versions_for_request_headers, expected_type=type_hints["secret_versions_for_request_headers"])
            check_type(argname="argument service_agent_auth", value=service_agent_auth, expected_type=type_hints["service_agent_auth"])
            check_type(argname="argument webhook_type", value=webhook_type, expected_type=type_hints["webhook_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "uri": uri,
        }
        if allowed_ca_certs is not None:
            self._values["allowed_ca_certs"] = allowed_ca_certs
        if http_method is not None:
            self._values["http_method"] = http_method
        if oauth_config is not None:
            self._values["oauth_config"] = oauth_config
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if request_body is not None:
            self._values["request_body"] = request_body
        if request_headers is not None:
            self._values["request_headers"] = request_headers
        if secret_version_for_username_password is not None:
            self._values["secret_version_for_username_password"] = secret_version_for_username_password
        if secret_versions_for_request_headers is not None:
            self._values["secret_versions_for_request_headers"] = secret_versions_for_request_headers
        if service_agent_auth is not None:
            self._values["service_agent_auth"] = service_agent_auth
        if webhook_type is not None:
            self._values["webhook_type"] = webhook_type

    @builtins.property
    def uri(self) -> builtins.str:
        '''The webhook URI for receiving POST requests. It must use https protocol.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#uri GoogleDialogflowCxWebhook#uri}
        '''
        result = self._values.get("uri")
        assert result is not None, "Required property 'uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_ca_certs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies a list of allowed custom CA certificates (in DER format) for HTTPS verification.

        This overrides the default SSL trust store. If this
        is empty or unspecified, Dialogflow will use Google's default trust store
        to verify certificates.
        N.B. Make sure the HTTPS server certificates are signed with "subject alt
        name". For instance a certificate can be self-signed using the following
        command,
        openssl x509 -req -days 200 -in example.com.csr
        -signkey example.com.key
        -out example.com.crt
        -extfile <(printf "\\nsubjectAltName='DNS:www.example.com'")

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#allowed_ca_certs GoogleDialogflowCxWebhook#allowed_ca_certs}
        '''
        result = self._values.get("allowed_ca_certs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def http_method(self) -> typing.Optional[builtins.str]:
        '''HTTP method for the flexible webhook calls.

        Standard webhook always uses
        POST. Possible values: ["POST", "GET", "HEAD", "PUT", "DELETE", "PATCH", "OPTIONS"]

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#http_method GoogleDialogflowCxWebhook#http_method}
        '''
        result = self._values.get("http_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oauth_config(
        self,
    ) -> typing.Optional["GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig"]:
        '''oauth_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#oauth_config GoogleDialogflowCxWebhook#oauth_config}
        '''
        result = self._values.get("oauth_config")
        return typing.cast(typing.Optional["GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig"], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Maps the values extracted from specific fields of the flexible webhook response into session parameters.

        - Key: session parameter name
        - Value: field path in the webhook response

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#parameter_mapping GoogleDialogflowCxWebhook#parameter_mapping}
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def request_body(self) -> typing.Optional[builtins.str]:
        '''Defines a custom JSON object as request body to send to flexible webhook.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_body GoogleDialogflowCxWebhook#request_body}
        '''
        result = self._values.get("request_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_headers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The HTTP request headers to send together with webhook requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_headers GoogleDialogflowCxWebhook#request_headers}
        '''
        result = self._values.get("request_headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def secret_version_for_username_password(self) -> typing.Optional[builtins.str]:
        '''The SecretManager secret version resource storing the username:password pair for HTTP Basic authentication. Format: 'projects/{project}/secrets/{secret}/versions/{version}'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_username_password GoogleDialogflowCxWebhook#secret_version_for_username_password}
        '''
        result = self._values.get("secret_version_for_username_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_versions_for_request_headers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders"]]]:
        '''secret_versions_for_request_headers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_versions_for_request_headers GoogleDialogflowCxWebhook#secret_versions_for_request_headers}
        '''
        result = self._values.get("secret_versions_for_request_headers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders"]]], result)

    @builtins.property
    def service_agent_auth(self) -> typing.Optional[builtins.str]:
        '''Indicate the auth token type generated from the `Diglogflow service agent <https://cloud.google.com/iam/docs/service-agents#dialogflow-service-agent>`_. The generated token is sent in the Authorization header. Possible values: ["NONE", "ID_TOKEN", "ACCESS_TOKEN"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service_agent_auth GoogleDialogflowCxWebhook#service_agent_auth}
        '''
        result = self._values.get("service_agent_auth")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook_type(self) -> typing.Optional[builtins.str]:
        '''Type of the webhook. Possible values: ["STANDARD", "FLEXIBLE"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#webhook_type GoogleDialogflowCxWebhook#webhook_type}
        '''
        result = self._values.get("webhook_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxWebhookServiceDirectoryGenericWebService(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "token_endpoint": "tokenEndpoint",
        "client_secret": "clientSecret",
        "scopes": "scopes",
        "secret_version_for_client_secret": "secretVersionForClientSecret",
    },
)
class GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig:
    def __init__(
        self,
        *,
        client_id: builtins.str,
        token_endpoint: builtins.str,
        client_secret: typing.Optional[builtins.str] = None,
        scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        secret_version_for_client_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_id: The client ID provided by the 3rd party platform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_id GoogleDialogflowCxWebhook#client_id}
        :param token_endpoint: The token endpoint provided by the 3rd party platform to exchange an access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#token_endpoint GoogleDialogflowCxWebhook#token_endpoint}
        :param client_secret: The client secret provided by the 3rd party platform. If the 'secret_version_for_client_secret' field is set, this field will be ignored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_secret GoogleDialogflowCxWebhook#client_secret}
        :param scopes: The OAuth scopes to grant. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#scopes GoogleDialogflowCxWebhook#scopes}
        :param secret_version_for_client_secret: The name of the SecretManager secret version resource storing the client secret. If this field is set, the 'client_secret' field will be ignored. Format: 'projects/{project}/secrets/{secret}/versions/{version}' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_client_secret GoogleDialogflowCxWebhook#secret_version_for_client_secret}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__def2a79eb75512c13d65bb4633b49fe97fb4851875cbe28db356fa0a8d01e6e2)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument token_endpoint", value=token_endpoint, expected_type=type_hints["token_endpoint"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument scopes", value=scopes, expected_type=type_hints["scopes"])
            check_type(argname="argument secret_version_for_client_secret", value=secret_version_for_client_secret, expected_type=type_hints["secret_version_for_client_secret"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client_id": client_id,
            "token_endpoint": token_endpoint,
        }
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if scopes is not None:
            self._values["scopes"] = scopes
        if secret_version_for_client_secret is not None:
            self._values["secret_version_for_client_secret"] = secret_version_for_client_secret

    @builtins.property
    def client_id(self) -> builtins.str:
        '''The client ID provided by the 3rd party platform.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_id GoogleDialogflowCxWebhook#client_id}
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def token_endpoint(self) -> builtins.str:
        '''The token endpoint provided by the 3rd party platform to exchange an access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#token_endpoint GoogleDialogflowCxWebhook#token_endpoint}
        '''
        result = self._values.get("token_endpoint")
        assert result is not None, "Required property 'token_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_secret(self) -> typing.Optional[builtins.str]:
        '''The client secret provided by the 3rd party platform.  If the 'secret_version_for_client_secret' field is set, this field will be ignored.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_secret GoogleDialogflowCxWebhook#client_secret}
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The OAuth scopes to grant.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#scopes GoogleDialogflowCxWebhook#scopes}
        '''
        result = self._values.get("scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secret_version_for_client_secret(self) -> typing.Optional[builtins.str]:
        '''The name of the SecretManager secret version resource storing the client secret.

        If this field is set, the 'client_secret' field will be
        ignored.
        Format: 'projects/{project}/secrets/{secret}/versions/{version}'

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_client_secret GoogleDialogflowCxWebhook#secret_version_for_client_secret}
        '''
        result = self._values.get("secret_version_for_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf16d4b63aabdfe733d1551214f24b9b974889198c6b8f1ed691d7ae65b89573)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetClientSecret")
    def reset_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientSecret", []))

    @jsii.member(jsii_name="resetScopes")
    def reset_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScopes", []))

    @jsii.member(jsii_name="resetSecretVersionForClientSecret")
    def reset_secret_version_for_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretVersionForClientSecret", []))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="scopesInput")
    def scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "scopesInput"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionForClientSecretInput")
    def secret_version_for_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretVersionForClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenEndpointInput")
    def token_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57b2634b2ee556fbba4589b67121ea4f8fdad39ebaa349f37d43e9b164924523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9f16688c06726cb0e5b55f1d728e0fe67207d256bfcabb0c9da560aa8ce01ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scopes")
    def scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "scopes"))

    @scopes.setter
    def scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11ebf315f0cd19fcdbcb9c678b1bb6b85dc5555a3150a85420b23e3f99914852)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scopes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretVersionForClientSecret")
    def secret_version_for_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretVersionForClientSecret"))

    @secret_version_for_client_secret.setter
    def secret_version_for_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bd1f76e5a9bee73e7f1b997f0fabb8c7de68dd73ef3a22d038d3771e0a35eb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretVersionForClientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenEndpoint")
    def token_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenEndpoint"))

    @token_endpoint.setter
    def token_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8da8c87193baa2f642ee2995be10d992052cbebfca66601e4373cc8c24c43902)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig]:
        return typing.cast(typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c13d2ec36e931102935eb42d611981c7cbe5eb2c6be51fc72e43a5b199846184)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e5a8262579e945b37bd5eadab932d8a78e87d87b15d6d7e007b893bb13bac46)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOauthConfig")
    def put_oauth_config(
        self,
        *,
        client_id: builtins.str,
        token_endpoint: builtins.str,
        client_secret: typing.Optional[builtins.str] = None,
        scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        secret_version_for_client_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_id: The client ID provided by the 3rd party platform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_id GoogleDialogflowCxWebhook#client_id}
        :param token_endpoint: The token endpoint provided by the 3rd party platform to exchange an access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#token_endpoint GoogleDialogflowCxWebhook#token_endpoint}
        :param client_secret: The client secret provided by the 3rd party platform. If the 'secret_version_for_client_secret' field is set, this field will be ignored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#client_secret GoogleDialogflowCxWebhook#client_secret}
        :param scopes: The OAuth scopes to grant. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#scopes GoogleDialogflowCxWebhook#scopes}
        :param secret_version_for_client_secret: The name of the SecretManager secret version resource storing the client secret. If this field is set, the 'client_secret' field will be ignored. Format: 'projects/{project}/secrets/{secret}/versions/{version}' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_client_secret GoogleDialogflowCxWebhook#secret_version_for_client_secret}
        '''
        value = GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig(
            client_id=client_id,
            token_endpoint=token_endpoint,
            client_secret=client_secret,
            scopes=scopes,
            secret_version_for_client_secret=secret_version_for_client_secret,
        )

        return typing.cast(None, jsii.invoke(self, "putOauthConfig", [value]))

    @jsii.member(jsii_name="putSecretVersionsForRequestHeaders")
    def put_secret_versions_for_request_headers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__029c7dac94852010d224e1b28cb8758e0075ba40d60fcf9c7248b73db38570fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSecretVersionsForRequestHeaders", [value]))

    @jsii.member(jsii_name="resetAllowedCaCerts")
    def reset_allowed_ca_certs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedCaCerts", []))

    @jsii.member(jsii_name="resetHttpMethod")
    def reset_http_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMethod", []))

    @jsii.member(jsii_name="resetOauthConfig")
    def reset_oauth_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOauthConfig", []))

    @jsii.member(jsii_name="resetParameterMapping")
    def reset_parameter_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterMapping", []))

    @jsii.member(jsii_name="resetRequestBody")
    def reset_request_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestBody", []))

    @jsii.member(jsii_name="resetRequestHeaders")
    def reset_request_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestHeaders", []))

    @jsii.member(jsii_name="resetSecretVersionForUsernamePassword")
    def reset_secret_version_for_username_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretVersionForUsernamePassword", []))

    @jsii.member(jsii_name="resetSecretVersionsForRequestHeaders")
    def reset_secret_versions_for_request_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretVersionsForRequestHeaders", []))

    @jsii.member(jsii_name="resetServiceAgentAuth")
    def reset_service_agent_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAgentAuth", []))

    @jsii.member(jsii_name="resetWebhookType")
    def reset_webhook_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebhookType", []))

    @builtins.property
    @jsii.member(jsii_name="oauthConfig")
    def oauth_config(
        self,
    ) -> GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfigOutputReference:
        return typing.cast(GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfigOutputReference, jsii.get(self, "oauthConfig"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionsForRequestHeaders")
    def secret_versions_for_request_headers(
        self,
    ) -> "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersList":
        return typing.cast("GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersList", jsii.get(self, "secretVersionsForRequestHeaders"))

    @builtins.property
    @jsii.member(jsii_name="allowedCaCertsInput")
    def allowed_ca_certs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedCaCertsInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMethodInput")
    def http_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="oauthConfigInput")
    def oauth_config_input(
        self,
    ) -> typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig]:
        return typing.cast(typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig], jsii.get(self, "oauthConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterMappingInput")
    def parameter_mapping_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parameterMappingInput"))

    @builtins.property
    @jsii.member(jsii_name="requestBodyInput")
    def request_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestBodyInput"))

    @builtins.property
    @jsii.member(jsii_name="requestHeadersInput")
    def request_headers_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "requestHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionForUsernamePasswordInput")
    def secret_version_for_username_password_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretVersionForUsernamePasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionsForRequestHeadersInput")
    def secret_versions_for_request_headers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders"]]], jsii.get(self, "secretVersionsForRequestHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAgentAuthInput")
    def service_agent_auth_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAgentAuthInput"))

    @builtins.property
    @jsii.member(jsii_name="uriInput")
    def uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uriInput"))

    @builtins.property
    @jsii.member(jsii_name="webhookTypeInput")
    def webhook_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webhookTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedCaCerts")
    def allowed_ca_certs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedCaCerts"))

    @allowed_ca_certs.setter
    def allowed_ca_certs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de91067f80bd0f42854d7f100708a6d5bdbb7e7151cb943be86a70645b525c57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedCaCerts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpMethod")
    def http_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpMethod"))

    @http_method.setter
    def http_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e4fd6cf0bbb640daf0f8c3c6be5a6730d31b968fc99d53bf90b70abe467c798)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterMapping")
    def parameter_mapping(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "parameterMapping"))

    @parameter_mapping.setter
    def parameter_mapping(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__483aa5ce84f044f6f954ad6df7684e5914d10f3b0e5b4084ad4e6aa039598b93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterMapping", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestBody")
    def request_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestBody"))

    @request_body.setter
    def request_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d10fa0c523b7b40f0d88931ea78142d162c24ca8404aa5aeba8a02e669d30d2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestBody", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestHeaders")
    def request_headers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "requestHeaders"))

    @request_headers.setter
    def request_headers(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f9de012f03fe2a09e930a94d87a33736b27469734609c73e89620c8ca9bbd3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretVersionForUsernamePassword")
    def secret_version_for_username_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretVersionForUsernamePassword"))

    @secret_version_for_username_password.setter
    def secret_version_for_username_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5966c14305f43685ab85759cadf2ee96a45ab58ccb140ca74cf0908e947a18f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretVersionForUsernamePassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAgentAuth")
    def service_agent_auth(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAgentAuth"))

    @service_agent_auth.setter
    def service_agent_auth(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e229bbe2c6973b78b7fbfce46d552829588ea9f1e6541170fe3487a4bc8bedff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAgentAuth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @uri.setter
    def uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad63a5d8fa6f745c0b2ea2276f4de02e5b79a67477582de23ea37ab1fa83540e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="webhookType")
    def webhook_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhookType"))

    @webhook_type.setter
    def webhook_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ea5ace35265edf57387272aeb60140654ef7f6519f1dfbd57ddc8c813f736ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhookType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebService]:
        return typing.cast(typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebService], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebService],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4509454b62e40826c3fce50f39e8bc242ea1b7c8019ff214002017159aea7068)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "secret_version": "secretVersion"},
)
class GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders:
    def __init__(self, *, key: builtins.str, secret_version: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#key GoogleDialogflowCxWebhook#key}.
        :param secret_version: The SecretManager secret version resource storing the header value. Format: 'projects/{project}/secrets/{secret}/versions/{version}'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version GoogleDialogflowCxWebhook#secret_version}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb700c7734342b87dd486c5661f5daf3d9284cb3016743bd2ef99795b9d27931)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument secret_version", value=secret_version, expected_type=type_hints["secret_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "secret_version": secret_version,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#key GoogleDialogflowCxWebhook#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_version(self) -> builtins.str:
        '''The SecretManager secret version resource storing the header value. Format: 'projects/{project}/secrets/{secret}/versions/{version}'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version GoogleDialogflowCxWebhook#secret_version}
        '''
        result = self._values.get("secret_version")
        assert result is not None, "Required property 'secret_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e6e8be4a1909ab23225bc295f984d8498c6f14f39a859040dcf8e37432619c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86db5f87b36373d850835d40ac846762ba01b8acfa91da0804b5927377d5bbd2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f13df1a52b80e73943c4bb1ede9d380260f51f81c5f96a5f524305c7ea4811a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a0e12515e52bd2d2246bda380da3b8c3106425947c880bded1ef047356bc1e1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__870348090e08619f854d48509ddad94e46f1fdb61828f8e224ab27dc01d19682)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a965a1af6bdc75129d44ed7192521e188fc7ca2ff019532725f1474031e51177)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c6ac4253513ef23b8569a2b7d734ac9ac867793189c94598f30b7be7ef40e4c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="secretVersionInput")
    def secret_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf3a8feb38012e693f5e4684b9626d4c679fd75dbdf9ee93f402b6598d914f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretVersion")
    def secret_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretVersion"))

    @secret_version.setter
    def secret_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f239cc1acd11cdc6ee309f243d95e67e1c2fab1d33add51eff07c9b37482dbde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27ceac7bb30ee8c7550e2173f812e90df2ff9a65a954093d893442ee26f8a846)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GoogleDialogflowCxWebhookServiceDirectoryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookServiceDirectoryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a178f90c72bad9f8870714c4c9f339d1f9621a1c936c96f96b311081e79af5d4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putGenericWebService")
    def put_generic_web_service(
        self,
        *,
        uri: builtins.str,
        allowed_ca_certs: typing.Optional[typing.Sequence[builtins.str]] = None,
        http_method: typing.Optional[builtins.str] = None,
        oauth_config: typing.Optional[typing.Union[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        parameter_mapping: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        request_body: typing.Optional[builtins.str] = None,
        request_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        secret_version_for_username_password: typing.Optional[builtins.str] = None,
        secret_versions_for_request_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_agent_auth: typing.Optional[builtins.str] = None,
        webhook_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param uri: The webhook URI for receiving POST requests. It must use https protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#uri GoogleDialogflowCxWebhook#uri}
        :param allowed_ca_certs: Specifies a list of allowed custom CA certificates (in DER format) for HTTPS verification. This overrides the default SSL trust store. If this is empty or unspecified, Dialogflow will use Google's default trust store to verify certificates. N.B. Make sure the HTTPS server certificates are signed with "subject alt name". For instance a certificate can be self-signed using the following command, openssl x509 -req -days 200 -in example.com.csr -signkey example.com.key -out example.com.crt -extfile <(printf "\\nsubjectAltName='DNS:www.example.com'") Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#allowed_ca_certs GoogleDialogflowCxWebhook#allowed_ca_certs}
        :param http_method: HTTP method for the flexible webhook calls. Standard webhook always uses POST. Possible values: ["POST", "GET", "HEAD", "PUT", "DELETE", "PATCH", "OPTIONS"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#http_method GoogleDialogflowCxWebhook#http_method}
        :param oauth_config: oauth_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#oauth_config GoogleDialogflowCxWebhook#oauth_config}
        :param parameter_mapping: Maps the values extracted from specific fields of the flexible webhook response into session parameters. - Key: session parameter name - Value: field path in the webhook response Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#parameter_mapping GoogleDialogflowCxWebhook#parameter_mapping}
        :param request_body: Defines a custom JSON object as request body to send to flexible webhook. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_body GoogleDialogflowCxWebhook#request_body}
        :param request_headers: The HTTP request headers to send together with webhook requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#request_headers GoogleDialogflowCxWebhook#request_headers}
        :param secret_version_for_username_password: The SecretManager secret version resource storing the username:password pair for HTTP Basic authentication. Format: 'projects/{project}/secrets/{secret}/versions/{version}'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_version_for_username_password GoogleDialogflowCxWebhook#secret_version_for_username_password}
        :param secret_versions_for_request_headers: secret_versions_for_request_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#secret_versions_for_request_headers GoogleDialogflowCxWebhook#secret_versions_for_request_headers}
        :param service_agent_auth: Indicate the auth token type generated from the `Diglogflow service agent <https://cloud.google.com/iam/docs/service-agents#dialogflow-service-agent>`_. The generated token is sent in the Authorization header. Possible values: ["NONE", "ID_TOKEN", "ACCESS_TOKEN"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#service_agent_auth GoogleDialogflowCxWebhook#service_agent_auth}
        :param webhook_type: Type of the webhook. Possible values: ["STANDARD", "FLEXIBLE"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#webhook_type GoogleDialogflowCxWebhook#webhook_type}
        '''
        value = GoogleDialogflowCxWebhookServiceDirectoryGenericWebService(
            uri=uri,
            allowed_ca_certs=allowed_ca_certs,
            http_method=http_method,
            oauth_config=oauth_config,
            parameter_mapping=parameter_mapping,
            request_body=request_body,
            request_headers=request_headers,
            secret_version_for_username_password=secret_version_for_username_password,
            secret_versions_for_request_headers=secret_versions_for_request_headers,
            service_agent_auth=service_agent_auth,
            webhook_type=webhook_type,
        )

        return typing.cast(None, jsii.invoke(self, "putGenericWebService", [value]))

    @jsii.member(jsii_name="resetGenericWebService")
    def reset_generic_web_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenericWebService", []))

    @builtins.property
    @jsii.member(jsii_name="genericWebService")
    def generic_web_service(
        self,
    ) -> GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOutputReference:
        return typing.cast(GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOutputReference, jsii.get(self, "genericWebService"))

    @builtins.property
    @jsii.member(jsii_name="genericWebServiceInput")
    def generic_web_service_input(
        self,
    ) -> typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebService]:
        return typing.cast(typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebService], jsii.get(self, "genericWebServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__131a472b2977606a43864aba19fb9b72e4482cfe6f42d6d99bffa129d3281a90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxWebhookServiceDirectory]:
        return typing.cast(typing.Optional[GoogleDialogflowCxWebhookServiceDirectory], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxWebhookServiceDirectory],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__945aee672181d452535c4e2ebfc52ee88cfb5fd318c5c1355e036b3565c59cec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class GoogleDialogflowCxWebhookTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#create GoogleDialogflowCxWebhook#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#delete GoogleDialogflowCxWebhook#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#update GoogleDialogflowCxWebhook#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c520df44ea478cb15413988ce01d194a48751ec84f06043c5eea87275f1f9ee1)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#create GoogleDialogflowCxWebhook#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#delete GoogleDialogflowCxWebhook#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/6.50.0/docs/resources/google_dialogflow_cx_webhook#update GoogleDialogflowCxWebhook#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxWebhookTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxWebhookTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxWebhook.GoogleDialogflowCxWebhookTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e135ef8c466fc12c3a2ab59941f5d74d1bf032aab4e56693e19cea0ba60b7a31)
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
            type_hints = typing.get_type_hints(_typecheckingstub__62004e465a8e941f48c053dc989a0e4bfd6885496176fa46b63b929f4bd02742)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b672edd6f9b19ef70caa6d43efe5c61c8f4216b4f6e74dd59eaddb6aada5547)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10f64f1d83eddbc88a0d44cc52da5e0c27adcd76e5069696af989e549bda86ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8acec3b77d1a12d1e32b5702d011d1bbe9fc1367ced7aefe383cb564880648b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "GoogleDialogflowCxWebhook",
    "GoogleDialogflowCxWebhookConfig",
    "GoogleDialogflowCxWebhookGenericWebService",
    "GoogleDialogflowCxWebhookGenericWebServiceOauthConfig",
    "GoogleDialogflowCxWebhookGenericWebServiceOauthConfigOutputReference",
    "GoogleDialogflowCxWebhookGenericWebServiceOutputReference",
    "GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders",
    "GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersList",
    "GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeadersOutputReference",
    "GoogleDialogflowCxWebhookServiceDirectory",
    "GoogleDialogflowCxWebhookServiceDirectoryGenericWebService",
    "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig",
    "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfigOutputReference",
    "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOutputReference",
    "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders",
    "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersList",
    "GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeadersOutputReference",
    "GoogleDialogflowCxWebhookServiceDirectoryOutputReference",
    "GoogleDialogflowCxWebhookTimeouts",
    "GoogleDialogflowCxWebhookTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__3c5806cd7ee91cb43ae92e485e436ca32d7f56effa632c11ffc1cfc41aefb67c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    display_name: builtins.str,
    disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_spell_correction: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_stackdriver_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    generic_web_service: typing.Optional[typing.Union[GoogleDialogflowCxWebhookGenericWebService, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    parent: typing.Optional[builtins.str] = None,
    security_settings: typing.Optional[builtins.str] = None,
    service_directory: typing.Optional[typing.Union[GoogleDialogflowCxWebhookServiceDirectory, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleDialogflowCxWebhookTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__0363add7e1532c6d6784456d35256c41ae9234a35afdf0b7998a65962c79555d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57671b22b640d5b96b87ccd15f9980bd31cfb367dcd322cd5925c5a94e4bfda1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__321d18ff8be8f03e0e143dd55e8e12956f3f690095769766711dfa6a7ab3bca7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__942ba817cbf27756624b37c32e0ae9d5412415c1fe9f3cefd1dfef2cd5447394(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05537eebe2014d7c56081cbf103598996d12e93ad54fd331f7dcd486de2fe76a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ce610a984435010f0e84513cad937faa230f59ba69bf1f82c68ccdb2aa8ea3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee1b282adf0b59a187fad6d85c8b797b35f6a134cc3c96ec9c75fa455e8d53bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d2ce5233268324c1c7dfe9efb83a3f880d102ad206261015a6df85e6dad7232(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e435387e7ebf3fcba26cd196bd7139c1ac14b09c742045277b05637979a91444(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05bd9ad21b40a120f3ad77aebd59e16e0566fd93fe14321ba3ac8bffdcda4bc4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    display_name: builtins.str,
    disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_spell_correction: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_stackdriver_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    generic_web_service: typing.Optional[typing.Union[GoogleDialogflowCxWebhookGenericWebService, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    parent: typing.Optional[builtins.str] = None,
    security_settings: typing.Optional[builtins.str] = None,
    service_directory: typing.Optional[typing.Union[GoogleDialogflowCxWebhookServiceDirectory, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleDialogflowCxWebhookTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aa3096505ab0805b17fab5fedb8b01817af1d2d6b0bca87e5fc88f402c40e0f(
    *,
    uri: builtins.str,
    allowed_ca_certs: typing.Optional[typing.Sequence[builtins.str]] = None,
    http_method: typing.Optional[builtins.str] = None,
    oauth_config: typing.Optional[typing.Union[GoogleDialogflowCxWebhookGenericWebServiceOauthConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    parameter_mapping: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    request_body: typing.Optional[builtins.str] = None,
    request_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    secret_version_for_username_password: typing.Optional[builtins.str] = None,
    secret_versions_for_request_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
    service_agent_auth: typing.Optional[builtins.str] = None,
    webhook_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95d2edce5f684d55df12319800ef86e1f726056d35467b8d66178cae78c9d0d5(
    *,
    client_id: builtins.str,
    token_endpoint: builtins.str,
    client_secret: typing.Optional[builtins.str] = None,
    scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    secret_version_for_client_secret: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3c0487606d9cf3298a08550ac7265509af6e85738248188ad15554c92d1f10e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__580e126362b7bd88df94f393070434b298ad566845848b0e2f0a688a2fbdb728(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93f89eae03960d284e96bcfb0af9c883b97b45431b3fe9e446687cd6b61fac8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e98523370a27c2ec684a07aaba2a9d2d425d6282d4275db6aca07dd88c5194d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6e549d69d7f911c76d9fb08043598ccc8c64c5675e539f30e4eed7f99926e85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__096cf9b6d2473560f74fb8d7145e4718c87f1ba8b10894388d01c6bb718ba3a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c1bf77b6c8317e702277e1d363a32471c13b628eeb38070f0771f4a87762ebb(
    value: typing.Optional[GoogleDialogflowCxWebhookGenericWebServiceOauthConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a1f0ac1f0ec0283ff2f958fc324ef171a3a0bdd949959f659b4b6a1de278ee1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e7c2afb557234bf3d5017dd79476b08faf91aec6efb6e83264d3867ddd9381d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6822965fad90a166781d318ba06eb9648d4cc32e9d1865ce849222c2c233443(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19f4e03a8613270268a216c382125ff7efc6054eeba8e7114c311c8edd207a47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07ac4ac98a9f8bb84fa94d020fc3a70c3a2278edc56e0b431e15c30783e05be8(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29b9f92871c1e8b58d0aba8b858376a88df1b0010bc18ef158f2aedf452b6a1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ae33de3e4579dc3d53a88b40986a304815500553820a7a16a06c457afdc74a7(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c24253aec12b1485f4b48bafddfa2e525398590cca41ce0d53b61ad1914892(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d298b6eb905f5e17467b55773bda8ae811bec9dd927c6531933e141b1e8cb0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb001615a7dd398afadb6bc645d8a1dca638d02cb0219a349097fd439208f3c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80de606a07b378aa2ec27e10ac609b379cc83b37804e5b097b08e5faa16782d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac5fff4d28d67df44331ec98262be9adf9d155ad26bd8584f10ce1a28c73c9e7(
    value: typing.Optional[GoogleDialogflowCxWebhookGenericWebService],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38b86b9c4a9abed44f621f44c4db2eb01690504af6eab90fa80bf44874972138(
    *,
    key: builtins.str,
    secret_version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba34265d7292e863451e3b52645e972925592583b179864f10e98acafda5c50c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e539fcafad45342366e2b5aa5f431734aaf74338461a37f21ef474b2281360a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33bf529d839725020a09f9503d2e4ef713bcb160b6f9eab08076624ad205cfa2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18ade9eda3780f2835d4fa45eb33b7abb5b7c713d47eb20aaf7f7ca03a921b76(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7742ee9e3b01bfd9fff46c0c583e1d4c58c133ac4e73447f3c18ad1b5e283057(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4aa14dd17568351a43a7753cb81952212e3fbe89cde4277cb6e2a34a870a42e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f7813dde15e894b87aa4adf5864e3fe8bd64ee0c250c5674d2464521139e09e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dfb8470f3fd53c05955d9ff1a3fb85e003876f2987be392336b1ea335d7981e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a976d5b4a0fb416f1dbcc3f3ee9c854e116cdac80545272598ae6d737748e4c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b282d5a5e08303c6b307cdb95443dcdccc6863513dd1b38f88d4347ffeabe33(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookGenericWebServiceSecretVersionsForRequestHeaders]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcb22ef256d963bcde3c55ce3d30a6480b8621171f06886a793fef462614bf3c(
    *,
    service: builtins.str,
    generic_web_service: typing.Optional[typing.Union[GoogleDialogflowCxWebhookServiceDirectoryGenericWebService, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6a19ec7026934de48fe2d290472f6ce99709968888b0166f01be172fbc47e3f(
    *,
    uri: builtins.str,
    allowed_ca_certs: typing.Optional[typing.Sequence[builtins.str]] = None,
    http_method: typing.Optional[builtins.str] = None,
    oauth_config: typing.Optional[typing.Union[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    parameter_mapping: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    request_body: typing.Optional[builtins.str] = None,
    request_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    secret_version_for_username_password: typing.Optional[builtins.str] = None,
    secret_versions_for_request_headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
    service_agent_auth: typing.Optional[builtins.str] = None,
    webhook_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__def2a79eb75512c13d65bb4633b49fe97fb4851875cbe28db356fa0a8d01e6e2(
    *,
    client_id: builtins.str,
    token_endpoint: builtins.str,
    client_secret: typing.Optional[builtins.str] = None,
    scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    secret_version_for_client_secret: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf16d4b63aabdfe733d1551214f24b9b974889198c6b8f1ed691d7ae65b89573(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57b2634b2ee556fbba4589b67121ea4f8fdad39ebaa349f37d43e9b164924523(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9f16688c06726cb0e5b55f1d728e0fe67207d256bfcabb0c9da560aa8ce01ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11ebf315f0cd19fcdbcb9c678b1bb6b85dc5555a3150a85420b23e3f99914852(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bd1f76e5a9bee73e7f1b997f0fabb8c7de68dd73ef3a22d038d3771e0a35eb3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8da8c87193baa2f642ee2995be10d992052cbebfca66601e4373cc8c24c43902(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c13d2ec36e931102935eb42d611981c7cbe5eb2c6be51fc72e43a5b199846184(
    value: typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceOauthConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e5a8262579e945b37bd5eadab932d8a78e87d87b15d6d7e007b893bb13bac46(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__029c7dac94852010d224e1b28cb8758e0075ba40d60fcf9c7248b73db38570fa(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de91067f80bd0f42854d7f100708a6d5bdbb7e7151cb943be86a70645b525c57(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e4fd6cf0bbb640daf0f8c3c6be5a6730d31b968fc99d53bf90b70abe467c798(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__483aa5ce84f044f6f954ad6df7684e5914d10f3b0e5b4084ad4e6aa039598b93(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d10fa0c523b7b40f0d88931ea78142d162c24ca8404aa5aeba8a02e669d30d2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f9de012f03fe2a09e930a94d87a33736b27469734609c73e89620c8ca9bbd3d(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5966c14305f43685ab85759cadf2ee96a45ab58ccb140ca74cf0908e947a18f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e229bbe2c6973b78b7fbfce46d552829588ea9f1e6541170fe3487a4bc8bedff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad63a5d8fa6f745c0b2ea2276f4de02e5b79a67477582de23ea37ab1fa83540e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ea5ace35265edf57387272aeb60140654ef7f6519f1dfbd57ddc8c813f736ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4509454b62e40826c3fce50f39e8bc242ea1b7c8019ff214002017159aea7068(
    value: typing.Optional[GoogleDialogflowCxWebhookServiceDirectoryGenericWebService],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb700c7734342b87dd486c5661f5daf3d9284cb3016743bd2ef99795b9d27931(
    *,
    key: builtins.str,
    secret_version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e6e8be4a1909ab23225bc295f984d8498c6f14f39a859040dcf8e37432619c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86db5f87b36373d850835d40ac846762ba01b8acfa91da0804b5927377d5bbd2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f13df1a52b80e73943c4bb1ede9d380260f51f81c5f96a5f524305c7ea4811a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a0e12515e52bd2d2246bda380da3b8c3106425947c880bded1ef047356bc1e1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__870348090e08619f854d48509ddad94e46f1fdb61828f8e224ab27dc01d19682(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a965a1af6bdc75129d44ed7192521e188fc7ca2ff019532725f1474031e51177(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c6ac4253513ef23b8569a2b7d734ac9ac867793189c94598f30b7be7ef40e4c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf3a8feb38012e693f5e4684b9626d4c679fd75dbdf9ee93f402b6598d914f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f239cc1acd11cdc6ee309f243d95e67e1c2fab1d33add51eff07c9b37482dbde(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27ceac7bb30ee8c7550e2173f812e90df2ff9a65a954093d893442ee26f8a846(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookServiceDirectoryGenericWebServiceSecretVersionsForRequestHeaders]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a178f90c72bad9f8870714c4c9f339d1f9621a1c936c96f96b311081e79af5d4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__131a472b2977606a43864aba19fb9b72e4482cfe6f42d6d99bffa129d3281a90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__945aee672181d452535c4e2ebfc52ee88cfb5fd318c5c1355e036b3565c59cec(
    value: typing.Optional[GoogleDialogflowCxWebhookServiceDirectory],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c520df44ea478cb15413988ce01d194a48751ec84f06043c5eea87275f1f9ee1(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e135ef8c466fc12c3a2ab59941f5d74d1bf032aab4e56693e19cea0ba60b7a31(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62004e465a8e941f48c053dc989a0e4bfd6885496176fa46b63b929f4bd02742(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b672edd6f9b19ef70caa6d43efe5c61c8f4216b4f6e74dd59eaddb6aada5547(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10f64f1d83eddbc88a0d44cc52da5e0c27adcd76e5069696af989e549bda86ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8acec3b77d1a12d1e32b5702d011d1bbe9fc1367ced7aefe383cb564880648b0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GoogleDialogflowCxWebhookTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
