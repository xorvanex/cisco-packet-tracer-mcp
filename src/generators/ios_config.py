"""Cisco IOS configuration generator."""

from typing import Dict, List
from ..core.models import Device, NetworkTopology


def generate_device_ios_config(device: Device) -> str:
    """Genera el bloque de configuración Cisco IOS (running-config) para un equipo."""
    lines: List[str] = []
    
    # Encabezado
    lines.append("! ==================================================")
    lines.append(f"! Configuracion Cisco IOS para: {device.id} ({device.model})")
    lines.append("! Generado automaticamente por cisco-packet-tracer-mcp")
    lines.append("! ==================================================")
    lines.append("enable")
    lines.append("configure terminal")
    lines.append("")
    
    # Hostname y seguridad base
    hostname = device.hostname or device.id
    lines.append(f"hostname {hostname}")
    lines.append("no ip domain-lookup")
    lines.append("service password-encryption")
    lines.append("enable secret class123")
    lines.append("")
    
    # Banner
    lines.append("banner motd #")
    lines.append(f"*** ACCESO AUTORIZADO UNICAMENTE - DISPOSITIVO: {hostname} ***")
    lines.append("#")
    lines.append("")
    
    # Si es switch, crear base de datos de VLANs
    if device.type == "switch" and device.vlans:
        lines.append("! --- Creacion de VLANs ---")
        for vlan in device.vlans:
            lines.append(f"vlan {vlan.id}")
            lines.append(f" name {vlan.name}")
            lines.append(" exit")
        lines.append("")
        
    # Interfaces físicas
    if device.interfaces:
        lines.append("! --- Configuracion de Interfaces ---")
        for iface in device.interfaces:
            lines.append(f"interface {iface.name}")
            if iface.description:
                lines.append(f" description {iface.description}")
                
            if device.type == "switch":
                if iface.mode == "trunk":
                    lines.append(" switchport mode trunk")
                    if iface.native_vlan and iface.native_vlan != 1:
                        lines.append(f" switchport trunk native vlan {iface.native_vlan}")
                elif iface.mode == "access":
                    lines.append(" switchport mode access")
                    if iface.vlan_id:
                        lines.append(f" switchport access vlan {iface.vlan_id}")
                    lines.append(" spanning-tree portfast")
            else:
                # Router
                if iface.ip_address and iface.subnet_mask:
                    lines.append(f" ip address {iface.ip_address} {iface.subnet_mask}")
                    
            if iface.enabled:
                lines.append(" no shutdown")
            else:
                lines.append(" shutdown")
            lines.append(" exit")
        lines.append("")

    # Subinterfaces 802.1Q (Router on a stick)
    if device.subinterfaces:
        lines.append("! --- Subinterfaces 802.1Q (Inter-VLAN) ---")
        for subif in device.subinterfaces:
            lines.append(f"interface {subif.name}")
            if subif.description:
                lines.append(f" description {subif.description}")
            lines.append(f" encapsulation dot1Q {subif.vlan_id}")
            lines.append(f" ip address {subif.ip_address} {subif.subnet_mask}")
            lines.append(" exit")
        lines.append("")

    # Pools DHCP
    if device.dhcp_pools:
        lines.append("! --- Servidor DHCP ---")
        for pool in device.dhcp_pools:
            for exc in pool.excluded_addresses:
                lines.append(f"ip dhcp excluded-address {exc}")
            lines.append(f"ip dhcp pool {pool.name}")
            lines.append(f" network {pool.network} {pool.mask}")
            lines.append(f" default-router {pool.default_router}")
            if pool.dns_server:
                lines.append(f" dns-server {pool.dns_server}")
            lines.append(" exit")
        lines.append("")

    # Enrutamiento OSPF
    if device.routing_ospf:
        ospf = device.routing_ospf
        lines.append(f"! --- Protocolo de Enrutamiento OSPF (Proceso {ospf.process_id}) ---")
        lines.append(f"router ospf {ospf.process_id}")
        if ospf.router_id:
            lines.append(f" router-id {ospf.router_id}")
        for net in ospf.networks:
            lines.append(f" network {net.network} {net.wildcard} area {net.area}")
        for p_iface in getattr(ospf, "passive_interfaces", []):
            lines.append(f" passive-interface {p_iface}")
        lines.append(" exit")
        lines.append("")

    # Enrutamiento RIP
    if device.routing_rip:
        rip = device.routing_rip
        lines.append(f"! --- Protocolo de Enrutamiento RIP (Version {rip.version}) ---")
        lines.append("router rip")
        lines.append(f" version {rip.version}")
        if rip.no_auto_summary:
            lines.append(" no auto-summary")
        for net in rip.networks:
            lines.append(f" network {net}")
        for p_iface in rip.passive_interfaces:
            lines.append(f" passive-interface {p_iface}")
        if rip.redistribute_static:
            if rip.metric_static:
                lines.append(f" redistribute static metric {rip.metric_static}")
            else:
                lines.append(" redistribute static")
        if rip.default_information_originate:
            lines.append(" default-information originate")
        lines.append(" exit")
        lines.append("")

    # Rutas estáticas
    if device.static_routes:
        lines.append("! --- Rutas Estaticas ---")
        for route in device.static_routes:
            lines.append(f"ip route {route.network} {route.mask} {route.next_hop}")
        lines.append("")

    # Lineas de consola y VTY
    lines.append("! --- Seguridad de Lineas ---")
    lines.append("line console 0")
    lines.append(" password cisco123")
    lines.append(" login")
    lines.append(" exec-timeout 5 0")
    lines.append(" logging synchronous")
    lines.append(" exit")
    lines.append("")
    
    vty_max = 15 if device.type == "switch" else 4
    lines.append(f"line vty 0 {vty_max}")
    lines.append(" password cisco123")
    lines.append(" login")
    lines.append(" exec-timeout 5 0")
    lines.append(" transport input ssh telnet")
    lines.append(" exit")
    lines.append("")
    
    # Cierre y guardado
    lines.append("end")
    lines.append("write memory")
    lines.append("")
    
    return "\n".join(lines)


def generate_all_ios_configs(topology: NetworkTopology) -> Dict[str, str]:
    """Genera las configuraciones IOS para todos los routers y switches de la red."""
    configs: Dict[str, str] = {}
    for dev in topology.devices:
        if dev.type in ["router", "switch"]:
            configs[dev.id] = generate_device_ios_config(dev)
    return configs
