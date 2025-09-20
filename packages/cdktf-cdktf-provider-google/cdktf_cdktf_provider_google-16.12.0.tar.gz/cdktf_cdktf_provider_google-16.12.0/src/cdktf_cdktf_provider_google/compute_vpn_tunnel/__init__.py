r'''
# `google_compute_vpn_tunnel`

Refer to the Terraform Registry for docs: [`google_compute_vpn_tunnel`](https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel).
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


class ComputeVpnTunnel(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeVpnTunnel.ComputeVpnTunnel",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel google_compute_vpn_tunnel}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        shared_secret: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ike_version: typing.Optional[jsii.Number] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        local_traffic_selector: typing.Optional[typing.Sequence[builtins.str]] = None,
        peer_external_gateway: typing.Optional[builtins.str] = None,
        peer_external_gateway_interface: typing.Optional[jsii.Number] = None,
        peer_gcp_gateway: typing.Optional[builtins.str] = None,
        peer_ip: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        remote_traffic_selector: typing.Optional[typing.Sequence[builtins.str]] = None,
        router: typing.Optional[builtins.str] = None,
        target_vpn_gateway: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["ComputeVpnTunnelTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        vpn_gateway: typing.Optional[builtins.str] = None,
        vpn_gateway_interface: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel google_compute_vpn_tunnel} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the resource. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression '`a-z <%5B-a-z0-9%5D*%5Ba-z0-9%5D>`_?' which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#name ComputeVpnTunnel#name}
        :param shared_secret: Shared secret used to set the secure session between the Cloud VPN gateway and the peer VPN gateway. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#shared_secret ComputeVpnTunnel#shared_secret}
        :param description: An optional description of this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#description ComputeVpnTunnel#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#id ComputeVpnTunnel#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ike_version: IKE protocol version to use when establishing the VPN tunnel with peer VPN gateway. Acceptable IKE versions are 1 or 2. Default version is 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#ike_version ComputeVpnTunnel#ike_version}
        :param labels: Labels to apply to this VpnTunnel. **Note**: This field is non-authoritative, and will only manage the labels present in your configuration. Please refer to the field 'effective_labels' for all of the labels present on the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#labels ComputeVpnTunnel#labels}
        :param local_traffic_selector: Local traffic selector to use when establishing the VPN tunnel with peer VPN gateway. The value should be a CIDR formatted string, for example '192.168.0.0/16'. The ranges should be disjoint. Only IPv4 is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#local_traffic_selector ComputeVpnTunnel#local_traffic_selector}
        :param peer_external_gateway: URL of the peer side external VPN gateway to which this VPN tunnel is connected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_external_gateway ComputeVpnTunnel#peer_external_gateway}
        :param peer_external_gateway_interface: The interface ID of the external VPN gateway to which this VPN tunnel is connected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_external_gateway_interface ComputeVpnTunnel#peer_external_gateway_interface}
        :param peer_gcp_gateway: URL of the peer side HA GCP VPN gateway to which this VPN tunnel is connected. If provided, the VPN tunnel will automatically use the same vpn_gateway_interface ID in the peer GCP VPN gateway. This field must reference a 'google_compute_ha_vpn_gateway' resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_gcp_gateway ComputeVpnTunnel#peer_gcp_gateway}
        :param peer_ip: IP address of the peer VPN gateway. Only IPv4 is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_ip ComputeVpnTunnel#peer_ip}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#project ComputeVpnTunnel#project}.
        :param region: The region where the tunnel is located. If unset, is set to the region of 'target_vpn_gateway'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#region ComputeVpnTunnel#region}
        :param remote_traffic_selector: Remote traffic selector to use when establishing the VPN tunnel with peer VPN gateway. The value should be a CIDR formatted string, for example '192.168.0.0/16'. The ranges should be disjoint. Only IPv4 is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#remote_traffic_selector ComputeVpnTunnel#remote_traffic_selector}
        :param router: URL of router resource to be used for dynamic routing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#router ComputeVpnTunnel#router}
        :param target_vpn_gateway: URL of the Target VPN gateway with which this VPN tunnel is associated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#target_vpn_gateway ComputeVpnTunnel#target_vpn_gateway}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#timeouts ComputeVpnTunnel#timeouts}
        :param vpn_gateway: URL of the VPN gateway with which this VPN tunnel is associated. This must be used if a High Availability VPN gateway resource is created. This field must reference a 'google_compute_ha_vpn_gateway' resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#vpn_gateway ComputeVpnTunnel#vpn_gateway}
        :param vpn_gateway_interface: The interface ID of the VPN gateway with which this VPN tunnel is associated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#vpn_gateway_interface ComputeVpnTunnel#vpn_gateway_interface}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1185742b903a8d9c5bd3a581f2e4a2fb1d77511ebbe797efebc92ce27625ed5e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ComputeVpnTunnelConfig(
            name=name,
            shared_secret=shared_secret,
            description=description,
            id=id,
            ike_version=ike_version,
            labels=labels,
            local_traffic_selector=local_traffic_selector,
            peer_external_gateway=peer_external_gateway,
            peer_external_gateway_interface=peer_external_gateway_interface,
            peer_gcp_gateway=peer_gcp_gateway,
            peer_ip=peer_ip,
            project=project,
            region=region,
            remote_traffic_selector=remote_traffic_selector,
            router=router,
            target_vpn_gateway=target_vpn_gateway,
            timeouts=timeouts,
            vpn_gateway=vpn_gateway,
            vpn_gateway_interface=vpn_gateway_interface,
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
        '''Generates CDKTF code for importing a ComputeVpnTunnel resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ComputeVpnTunnel to import.
        :param import_from_id: The id of the existing ComputeVpnTunnel that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ComputeVpnTunnel to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29af8963d6e011714f7182d855387e6279bf713d376a63a30e5b4b8e5c1ebab2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#create ComputeVpnTunnel#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#delete ComputeVpnTunnel#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#update ComputeVpnTunnel#update}.
        '''
        value = ComputeVpnTunnelTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIkeVersion")
    def reset_ike_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIkeVersion", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetLocalTrafficSelector")
    def reset_local_traffic_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalTrafficSelector", []))

    @jsii.member(jsii_name="resetPeerExternalGateway")
    def reset_peer_external_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeerExternalGateway", []))

    @jsii.member(jsii_name="resetPeerExternalGatewayInterface")
    def reset_peer_external_gateway_interface(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeerExternalGatewayInterface", []))

    @jsii.member(jsii_name="resetPeerGcpGateway")
    def reset_peer_gcp_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeerGcpGateway", []))

    @jsii.member(jsii_name="resetPeerIp")
    def reset_peer_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeerIp", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetRemoteTrafficSelector")
    def reset_remote_traffic_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteTrafficSelector", []))

    @jsii.member(jsii_name="resetRouter")
    def reset_router(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouter", []))

    @jsii.member(jsii_name="resetTargetVpnGateway")
    def reset_target_vpn_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetVpnGateway", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVpnGateway")
    def reset_vpn_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpnGateway", []))

    @jsii.member(jsii_name="resetVpnGatewayInterface")
    def reset_vpn_gateway_interface(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpnGatewayInterface", []))

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
    @jsii.member(jsii_name="creationTimestamp")
    def creation_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="detailedStatus")
    def detailed_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detailedStatus"))

    @builtins.property
    @jsii.member(jsii_name="effectiveLabels")
    def effective_labels(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "effectiveLabels"))

    @builtins.property
    @jsii.member(jsii_name="labelFingerprint")
    def label_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "labelFingerprint"))

    @builtins.property
    @jsii.member(jsii_name="selfLink")
    def self_link(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "selfLink"))

    @builtins.property
    @jsii.member(jsii_name="sharedSecretHash")
    def shared_secret_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sharedSecretHash"))

    @builtins.property
    @jsii.member(jsii_name="terraformLabels")
    def terraform_labels(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "terraformLabels"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ComputeVpnTunnelTimeoutsOutputReference":
        return typing.cast("ComputeVpnTunnelTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="tunnelId")
    def tunnel_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tunnelId"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ikeVersionInput")
    def ike_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ikeVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="localTrafficSelectorInput")
    def local_traffic_selector_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "localTrafficSelectorInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="peerExternalGatewayInput")
    def peer_external_gateway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "peerExternalGatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="peerExternalGatewayInterfaceInput")
    def peer_external_gateway_interface_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "peerExternalGatewayInterfaceInput"))

    @builtins.property
    @jsii.member(jsii_name="peerGcpGatewayInput")
    def peer_gcp_gateway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "peerGcpGatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="peerIpInput")
    def peer_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "peerIpInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteTrafficSelectorInput")
    def remote_traffic_selector_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "remoteTrafficSelectorInput"))

    @builtins.property
    @jsii.member(jsii_name="routerInput")
    def router_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routerInput"))

    @builtins.property
    @jsii.member(jsii_name="sharedSecretInput")
    def shared_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sharedSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="targetVpnGatewayInput")
    def target_vpn_gateway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetVpnGatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ComputeVpnTunnelTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ComputeVpnTunnelTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="vpnGatewayInput")
    def vpn_gateway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpnGatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="vpnGatewayInterfaceInput")
    def vpn_gateway_interface_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vpnGatewayInterfaceInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43ca21f8e1d9cac77ee4bf5c20a1552f9fde97d8a17c8c72e0ca3bd39603c496)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c3b2ad155d6d9401eab9a68a05fbb959be47edd683e20050af51aed125d4379)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ikeVersion")
    def ike_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ikeVersion"))

    @ike_version.setter
    def ike_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2c6203629b0c81c31ab5e75c4e5b36b25275383788deae74b8bb60fd8455659)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ikeVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9f90adb53be304855f0acb0c1ddc182ed7ce8278b3307f7e793e0bc7dfa5ce5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localTrafficSelector")
    def local_traffic_selector(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "localTrafficSelector"))

    @local_traffic_selector.setter
    def local_traffic_selector(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03e9bb4b99d2f6f5c8d68b7fd9bac318fbadb048754f588888e47eb7d8f9d28c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localTrafficSelector", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76bf61c9bda6e78c038557210cdd566e498504abc97ebabc8abe5f022c880491)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peerExternalGateway")
    def peer_external_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peerExternalGateway"))

    @peer_external_gateway.setter
    def peer_external_gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f1e65a009c6d86574e4ba1dbea95b7d25945e8a3681aef4f0187d34c70b9d86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peerExternalGateway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peerExternalGatewayInterface")
    def peer_external_gateway_interface(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "peerExternalGatewayInterface"))

    @peer_external_gateway_interface.setter
    def peer_external_gateway_interface(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d81f2b518d7ee4e07660d6286919fc34508d05cb6c898202b10f50193df1834)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peerExternalGatewayInterface", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peerGcpGateway")
    def peer_gcp_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peerGcpGateway"))

    @peer_gcp_gateway.setter
    def peer_gcp_gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9559f4f26bc43d089d9c05091a8101d64f0f8649e98282222c0d33ccecfc37b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peerGcpGateway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peerIp")
    def peer_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peerIp"))

    @peer_ip.setter
    def peer_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__884d905931895a1a1cbfc523059ded7b012b461bb2845512a85ab196017af44b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peerIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9150e05a5725fea011d39995a0706c177875eccaee319cbf5336d7f8f66b6039)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c327f555e6bcfaa729aa453d186ac98e1780361b7695fac57f96e95d54c6cab6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remoteTrafficSelector")
    def remote_traffic_selector(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "remoteTrafficSelector"))

    @remote_traffic_selector.setter
    def remote_traffic_selector(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f21bd2ce74cbc7be164fc19c5b8bd73929f2c58440c98d43e177eb118c0b950)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remoteTrafficSelector", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="router")
    def router(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "router"))

    @router.setter
    def router(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9378c7ca56dcc5e305239245a4a54803270ebe87bc4fcbe8a18ba9ee342ed1c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "router", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sharedSecret")
    def shared_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sharedSecret"))

    @shared_secret.setter
    def shared_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6819510ad038c19c16e248a00066d635dcbb1a1a3014386d1bf3779a31db60f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sharedSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetVpnGateway")
    def target_vpn_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetVpnGateway"))

    @target_vpn_gateway.setter
    def target_vpn_gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8330f9e25d1e4fd5ae73bdb39ec809e1e02c24f15945b727e75ae7288606ff56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetVpnGateway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpnGateway")
    def vpn_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpnGateway"))

    @vpn_gateway.setter
    def vpn_gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54d3686922209b4a37b77cfb0c4c0ff34d2d931016232e6b54c1ad48f59b1905)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpnGateway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpnGatewayInterface")
    def vpn_gateway_interface(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vpnGatewayInterface"))

    @vpn_gateway_interface.setter
    def vpn_gateway_interface(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2835a5e590b3a09858c6e8802dd69623a03b7960d654187d76c5a29ef3973dee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpnGatewayInterface", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeVpnTunnel.ComputeVpnTunnelConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "shared_secret": "sharedSecret",
        "description": "description",
        "id": "id",
        "ike_version": "ikeVersion",
        "labels": "labels",
        "local_traffic_selector": "localTrafficSelector",
        "peer_external_gateway": "peerExternalGateway",
        "peer_external_gateway_interface": "peerExternalGatewayInterface",
        "peer_gcp_gateway": "peerGcpGateway",
        "peer_ip": "peerIp",
        "project": "project",
        "region": "region",
        "remote_traffic_selector": "remoteTrafficSelector",
        "router": "router",
        "target_vpn_gateway": "targetVpnGateway",
        "timeouts": "timeouts",
        "vpn_gateway": "vpnGateway",
        "vpn_gateway_interface": "vpnGatewayInterface",
    },
)
class ComputeVpnTunnelConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        shared_secret: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ike_version: typing.Optional[jsii.Number] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        local_traffic_selector: typing.Optional[typing.Sequence[builtins.str]] = None,
        peer_external_gateway: typing.Optional[builtins.str] = None,
        peer_external_gateway_interface: typing.Optional[jsii.Number] = None,
        peer_gcp_gateway: typing.Optional[builtins.str] = None,
        peer_ip: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        remote_traffic_selector: typing.Optional[typing.Sequence[builtins.str]] = None,
        router: typing.Optional[builtins.str] = None,
        target_vpn_gateway: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["ComputeVpnTunnelTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        vpn_gateway: typing.Optional[builtins.str] = None,
        vpn_gateway_interface: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Name of the resource. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression '`a-z <%5B-a-z0-9%5D*%5Ba-z0-9%5D>`_?' which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#name ComputeVpnTunnel#name}
        :param shared_secret: Shared secret used to set the secure session between the Cloud VPN gateway and the peer VPN gateway. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#shared_secret ComputeVpnTunnel#shared_secret}
        :param description: An optional description of this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#description ComputeVpnTunnel#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#id ComputeVpnTunnel#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ike_version: IKE protocol version to use when establishing the VPN tunnel with peer VPN gateway. Acceptable IKE versions are 1 or 2. Default version is 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#ike_version ComputeVpnTunnel#ike_version}
        :param labels: Labels to apply to this VpnTunnel. **Note**: This field is non-authoritative, and will only manage the labels present in your configuration. Please refer to the field 'effective_labels' for all of the labels present on the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#labels ComputeVpnTunnel#labels}
        :param local_traffic_selector: Local traffic selector to use when establishing the VPN tunnel with peer VPN gateway. The value should be a CIDR formatted string, for example '192.168.0.0/16'. The ranges should be disjoint. Only IPv4 is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#local_traffic_selector ComputeVpnTunnel#local_traffic_selector}
        :param peer_external_gateway: URL of the peer side external VPN gateway to which this VPN tunnel is connected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_external_gateway ComputeVpnTunnel#peer_external_gateway}
        :param peer_external_gateway_interface: The interface ID of the external VPN gateway to which this VPN tunnel is connected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_external_gateway_interface ComputeVpnTunnel#peer_external_gateway_interface}
        :param peer_gcp_gateway: URL of the peer side HA GCP VPN gateway to which this VPN tunnel is connected. If provided, the VPN tunnel will automatically use the same vpn_gateway_interface ID in the peer GCP VPN gateway. This field must reference a 'google_compute_ha_vpn_gateway' resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_gcp_gateway ComputeVpnTunnel#peer_gcp_gateway}
        :param peer_ip: IP address of the peer VPN gateway. Only IPv4 is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_ip ComputeVpnTunnel#peer_ip}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#project ComputeVpnTunnel#project}.
        :param region: The region where the tunnel is located. If unset, is set to the region of 'target_vpn_gateway'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#region ComputeVpnTunnel#region}
        :param remote_traffic_selector: Remote traffic selector to use when establishing the VPN tunnel with peer VPN gateway. The value should be a CIDR formatted string, for example '192.168.0.0/16'. The ranges should be disjoint. Only IPv4 is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#remote_traffic_selector ComputeVpnTunnel#remote_traffic_selector}
        :param router: URL of router resource to be used for dynamic routing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#router ComputeVpnTunnel#router}
        :param target_vpn_gateway: URL of the Target VPN gateway with which this VPN tunnel is associated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#target_vpn_gateway ComputeVpnTunnel#target_vpn_gateway}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#timeouts ComputeVpnTunnel#timeouts}
        :param vpn_gateway: URL of the VPN gateway with which this VPN tunnel is associated. This must be used if a High Availability VPN gateway resource is created. This field must reference a 'google_compute_ha_vpn_gateway' resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#vpn_gateway ComputeVpnTunnel#vpn_gateway}
        :param vpn_gateway_interface: The interface ID of the VPN gateway with which this VPN tunnel is associated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#vpn_gateway_interface ComputeVpnTunnel#vpn_gateway_interface}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = ComputeVpnTunnelTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22388026feebe978c090ddaf071f729ab978aa4cbdcce8182faf44de1504f4de)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument shared_secret", value=shared_secret, expected_type=type_hints["shared_secret"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ike_version", value=ike_version, expected_type=type_hints["ike_version"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument local_traffic_selector", value=local_traffic_selector, expected_type=type_hints["local_traffic_selector"])
            check_type(argname="argument peer_external_gateway", value=peer_external_gateway, expected_type=type_hints["peer_external_gateway"])
            check_type(argname="argument peer_external_gateway_interface", value=peer_external_gateway_interface, expected_type=type_hints["peer_external_gateway_interface"])
            check_type(argname="argument peer_gcp_gateway", value=peer_gcp_gateway, expected_type=type_hints["peer_gcp_gateway"])
            check_type(argname="argument peer_ip", value=peer_ip, expected_type=type_hints["peer_ip"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument remote_traffic_selector", value=remote_traffic_selector, expected_type=type_hints["remote_traffic_selector"])
            check_type(argname="argument router", value=router, expected_type=type_hints["router"])
            check_type(argname="argument target_vpn_gateway", value=target_vpn_gateway, expected_type=type_hints["target_vpn_gateway"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument vpn_gateway", value=vpn_gateway, expected_type=type_hints["vpn_gateway"])
            check_type(argname="argument vpn_gateway_interface", value=vpn_gateway_interface, expected_type=type_hints["vpn_gateway_interface"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "shared_secret": shared_secret,
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
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if ike_version is not None:
            self._values["ike_version"] = ike_version
        if labels is not None:
            self._values["labels"] = labels
        if local_traffic_selector is not None:
            self._values["local_traffic_selector"] = local_traffic_selector
        if peer_external_gateway is not None:
            self._values["peer_external_gateway"] = peer_external_gateway
        if peer_external_gateway_interface is not None:
            self._values["peer_external_gateway_interface"] = peer_external_gateway_interface
        if peer_gcp_gateway is not None:
            self._values["peer_gcp_gateway"] = peer_gcp_gateway
        if peer_ip is not None:
            self._values["peer_ip"] = peer_ip
        if project is not None:
            self._values["project"] = project
        if region is not None:
            self._values["region"] = region
        if remote_traffic_selector is not None:
            self._values["remote_traffic_selector"] = remote_traffic_selector
        if router is not None:
            self._values["router"] = router
        if target_vpn_gateway is not None:
            self._values["target_vpn_gateway"] = target_vpn_gateway
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if vpn_gateway is not None:
            self._values["vpn_gateway"] = vpn_gateway
        if vpn_gateway_interface is not None:
            self._values["vpn_gateway_interface"] = vpn_gateway_interface

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
    def name(self) -> builtins.str:
        '''Name of the resource.

        The name must be 1-63 characters long, and
        comply with RFC1035. Specifically, the name must be 1-63
        characters long and match the regular expression
        '`a-z <%5B-a-z0-9%5D*%5Ba-z0-9%5D>`_?' which means the first character
        must be a lowercase letter, and all following characters must
        be a dash, lowercase letter, or digit,
        except the last character, which cannot be a dash.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#name ComputeVpnTunnel#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def shared_secret(self) -> builtins.str:
        '''Shared secret used to set the secure session between the Cloud VPN gateway and the peer VPN gateway.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#shared_secret ComputeVpnTunnel#shared_secret}
        '''
        result = self._values.get("shared_secret")
        assert result is not None, "Required property 'shared_secret' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''An optional description of this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#description ComputeVpnTunnel#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#id ComputeVpnTunnel#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ike_version(self) -> typing.Optional[jsii.Number]:
        '''IKE protocol version to use when establishing the VPN tunnel with peer VPN gateway.

        Acceptable IKE versions are 1 or 2. Default version is 2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#ike_version ComputeVpnTunnel#ike_version}
        '''
        result = self._values.get("ike_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Labels to apply to this VpnTunnel.

        **Note**: This field is non-authoritative, and will only manage the labels present in your configuration.
        Please refer to the field 'effective_labels' for all of the labels present on the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#labels ComputeVpnTunnel#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def local_traffic_selector(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Local traffic selector to use when establishing the VPN tunnel with peer VPN gateway.

        The value should be a CIDR formatted string,
        for example '192.168.0.0/16'. The ranges should be disjoint.
        Only IPv4 is supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#local_traffic_selector ComputeVpnTunnel#local_traffic_selector}
        '''
        result = self._values.get("local_traffic_selector")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def peer_external_gateway(self) -> typing.Optional[builtins.str]:
        '''URL of the peer side external VPN gateway to which this VPN tunnel is connected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_external_gateway ComputeVpnTunnel#peer_external_gateway}
        '''
        result = self._values.get("peer_external_gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer_external_gateway_interface(self) -> typing.Optional[jsii.Number]:
        '''The interface ID of the external VPN gateway to which this VPN tunnel is connected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_external_gateway_interface ComputeVpnTunnel#peer_external_gateway_interface}
        '''
        result = self._values.get("peer_external_gateway_interface")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def peer_gcp_gateway(self) -> typing.Optional[builtins.str]:
        '''URL of the peer side HA GCP VPN gateway to which this VPN tunnel is connected.

        If provided, the VPN tunnel will automatically use the same vpn_gateway_interface
        ID in the peer GCP VPN gateway.
        This field must reference a 'google_compute_ha_vpn_gateway' resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_gcp_gateway ComputeVpnTunnel#peer_gcp_gateway}
        '''
        result = self._values.get("peer_gcp_gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer_ip(self) -> typing.Optional[builtins.str]:
        '''IP address of the peer VPN gateway. Only IPv4 is supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#peer_ip ComputeVpnTunnel#peer_ip}
        '''
        result = self._values.get("peer_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#project ComputeVpnTunnel#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The region where the tunnel is located. If unset, is set to the region of 'target_vpn_gateway'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#region ComputeVpnTunnel#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_traffic_selector(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Remote traffic selector to use when establishing the VPN tunnel with peer VPN gateway.

        The value should be a CIDR formatted string,
        for example '192.168.0.0/16'. The ranges should be disjoint.
        Only IPv4 is supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#remote_traffic_selector ComputeVpnTunnel#remote_traffic_selector}
        '''
        result = self._values.get("remote_traffic_selector")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def router(self) -> typing.Optional[builtins.str]:
        '''URL of router resource to be used for dynamic routing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#router ComputeVpnTunnel#router}
        '''
        result = self._values.get("router")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_vpn_gateway(self) -> typing.Optional[builtins.str]:
        '''URL of the Target VPN gateway with which this VPN tunnel is associated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#target_vpn_gateway ComputeVpnTunnel#target_vpn_gateway}
        '''
        result = self._values.get("target_vpn_gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ComputeVpnTunnelTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#timeouts ComputeVpnTunnel#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ComputeVpnTunnelTimeouts"], result)

    @builtins.property
    def vpn_gateway(self) -> typing.Optional[builtins.str]:
        '''URL of the VPN gateway with which this VPN tunnel is associated.

        This must be used if a High Availability VPN gateway resource is created.
        This field must reference a 'google_compute_ha_vpn_gateway' resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#vpn_gateway ComputeVpnTunnel#vpn_gateway}
        '''
        result = self._values.get("vpn_gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpn_gateway_interface(self) -> typing.Optional[jsii.Number]:
        '''The interface ID of the VPN gateway with which this VPN tunnel is associated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#vpn_gateway_interface ComputeVpnTunnel#vpn_gateway_interface}
        '''
        result = self._values.get("vpn_gateway_interface")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeVpnTunnelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google.computeVpnTunnel.ComputeVpnTunnelTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class ComputeVpnTunnelTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#create ComputeVpnTunnel#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#delete ComputeVpnTunnel#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#update ComputeVpnTunnel#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51c9dc7ac596f143c18b9e35a5fc884e14cbc88f62e4764304cbb545c17af364)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#create ComputeVpnTunnel#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#delete ComputeVpnTunnel#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google/6.50.0/docs/resources/compute_vpn_tunnel#update ComputeVpnTunnel#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeVpnTunnelTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ComputeVpnTunnelTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google.computeVpnTunnel.ComputeVpnTunnelTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__03502576291a4cd097444dd9d5892f621df4c96be30b3aeab14daff3af2d244a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e6c8b517531d29a9a9eba8101fde5c54dc3ead59a838ceaf3e1a52f32f5efaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61afeb3711d5af703f700e57753d4e43eb3bc2e23a4d774bc3c4ab2c5016ce6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b26894a8adbd9ea3227af05289a841d61f19b1bb06dc195a6a727af63ac7f183)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeVpnTunnelTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeVpnTunnelTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeVpnTunnelTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__517753c967e56e119f53be8eaaa3f7cf546390aa6c5bedbbab4b12c61fba2b8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ComputeVpnTunnel",
    "ComputeVpnTunnelConfig",
    "ComputeVpnTunnelTimeouts",
    "ComputeVpnTunnelTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__1185742b903a8d9c5bd3a581f2e4a2fb1d77511ebbe797efebc92ce27625ed5e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    shared_secret: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ike_version: typing.Optional[jsii.Number] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    local_traffic_selector: typing.Optional[typing.Sequence[builtins.str]] = None,
    peer_external_gateway: typing.Optional[builtins.str] = None,
    peer_external_gateway_interface: typing.Optional[jsii.Number] = None,
    peer_gcp_gateway: typing.Optional[builtins.str] = None,
    peer_ip: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    remote_traffic_selector: typing.Optional[typing.Sequence[builtins.str]] = None,
    router: typing.Optional[builtins.str] = None,
    target_vpn_gateway: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[ComputeVpnTunnelTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    vpn_gateway: typing.Optional[builtins.str] = None,
    vpn_gateway_interface: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__29af8963d6e011714f7182d855387e6279bf713d376a63a30e5b4b8e5c1ebab2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43ca21f8e1d9cac77ee4bf5c20a1552f9fde97d8a17c8c72e0ca3bd39603c496(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c3b2ad155d6d9401eab9a68a05fbb959be47edd683e20050af51aed125d4379(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2c6203629b0c81c31ab5e75c4e5b36b25275383788deae74b8bb60fd8455659(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9f90adb53be304855f0acb0c1ddc182ed7ce8278b3307f7e793e0bc7dfa5ce5(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03e9bb4b99d2f6f5c8d68b7fd9bac318fbadb048754f588888e47eb7d8f9d28c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76bf61c9bda6e78c038557210cdd566e498504abc97ebabc8abe5f022c880491(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f1e65a009c6d86574e4ba1dbea95b7d25945e8a3681aef4f0187d34c70b9d86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d81f2b518d7ee4e07660d6286919fc34508d05cb6c898202b10f50193df1834(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9559f4f26bc43d089d9c05091a8101d64f0f8649e98282222c0d33ccecfc37b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__884d905931895a1a1cbfc523059ded7b012b461bb2845512a85ab196017af44b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9150e05a5725fea011d39995a0706c177875eccaee319cbf5336d7f8f66b6039(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c327f555e6bcfaa729aa453d186ac98e1780361b7695fac57f96e95d54c6cab6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f21bd2ce74cbc7be164fc19c5b8bd73929f2c58440c98d43e177eb118c0b950(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9378c7ca56dcc5e305239245a4a54803270ebe87bc4fcbe8a18ba9ee342ed1c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6819510ad038c19c16e248a00066d635dcbb1a1a3014386d1bf3779a31db60f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8330f9e25d1e4fd5ae73bdb39ec809e1e02c24f15945b727e75ae7288606ff56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54d3686922209b4a37b77cfb0c4c0ff34d2d931016232e6b54c1ad48f59b1905(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2835a5e590b3a09858c6e8802dd69623a03b7960d654187d76c5a29ef3973dee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22388026feebe978c090ddaf071f729ab978aa4cbdcce8182faf44de1504f4de(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    shared_secret: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ike_version: typing.Optional[jsii.Number] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    local_traffic_selector: typing.Optional[typing.Sequence[builtins.str]] = None,
    peer_external_gateway: typing.Optional[builtins.str] = None,
    peer_external_gateway_interface: typing.Optional[jsii.Number] = None,
    peer_gcp_gateway: typing.Optional[builtins.str] = None,
    peer_ip: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    remote_traffic_selector: typing.Optional[typing.Sequence[builtins.str]] = None,
    router: typing.Optional[builtins.str] = None,
    target_vpn_gateway: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[ComputeVpnTunnelTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    vpn_gateway: typing.Optional[builtins.str] = None,
    vpn_gateway_interface: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51c9dc7ac596f143c18b9e35a5fc884e14cbc88f62e4764304cbb545c17af364(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03502576291a4cd097444dd9d5892f621df4c96be30b3aeab14daff3af2d244a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e6c8b517531d29a9a9eba8101fde5c54dc3ead59a838ceaf3e1a52f32f5efaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61afeb3711d5af703f700e57753d4e43eb3bc2e23a4d774bc3c4ab2c5016ce6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b26894a8adbd9ea3227af05289a841d61f19b1bb06dc195a6a727af63ac7f183(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__517753c967e56e119f53be8eaaa3f7cf546390aa6c5bedbbab4b12c61fba2b8e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ComputeVpnTunnelTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
