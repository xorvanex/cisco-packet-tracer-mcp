"""VLSM (Variable Length Subnet Masking) calculator engine."""

import ipaddress
import math
from typing import List, Dict, Any


def calculate_vlsm(network_block: str, subnets_request: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calcula la partición de un bloque de red IPv4 mediante VLSM.
    
    Args:
        network_block: Bloque base en notación CIDR, ej. "192.168.1.0/24"
        subnets_request: Lista de diccionarios con 'name' y 'hosts_needed',
                         ej. [{'name': 'LAN1', 'hosts_needed': 50}, ...]
                         
    Returns:
        Lista de diccionarios con la información completa de cada subred asignada.
    """
    base_net = ipaddress.IPv4Network(network_block, strict=True)
    
    # Ordenar los requerimientos de mayor a menor (regla fundamental de VLSM)
    sorted_requests = sorted(subnets_request, key=lambda x: x.get("hosts_needed", 0), reverse=True)
    
    current_ip_int = int(base_net.network_address)
    base_end_int = int(base_net.broadcast_address)
    
    results = []
    
    for req in sorted_requests:
        name = req.get("name", "Subred")
        hosts_needed = req.get("hosts_needed", 2)
        
        # Calcular los bits necesarios para host: 2^h - 2 >= hosts_needed
        # Excepción especial: enlaces punto a punto /31 según RFC 3021 o /30 estándar de Packet Tracer
        # En Packet Tracer comúnmente se usa /30 para 2 hosts (red + 2 utilizables + broadcast = 4 IPs)
        needed_total = hosts_needed + 2
        host_bits = max(2, math.ceil(math.log2(needed_total)))
        prefix_len = 32 - host_bits
        
        subnet_size = 2 ** host_bits
        
        # Verificar alineación de subred con su tamaño
        if current_ip_int % subnet_size != 0:
            current_ip_int += subnet_size - (current_ip_int % subnet_size)
            
        subnet_end_int = current_ip_int + subnet_size - 1
        
        if subnet_end_int > base_end_int:
            raise ValueError(
                f"Capacidad excedida: El bloque base '{network_block}' no tiene suficiente espacio "
                f"para alojar la subred '{name}' ({hosts_needed} hosts requeridos)."
            )
            
        sub_net = ipaddress.IPv4Network((current_ip_int, prefix_len))
        
        first_usable = str(sub_net.network_address + 1)
        last_usable = str(sub_net.broadcast_address - 1)
        gateway = first_usable
        
        # Wildcard mask = 255.255.255.255 - netmask
        netmask_parts = [int(p) for p in str(sub_net.netmask).split('.')]
        wildcard_parts = [255 - p for p in netmask_parts]
        wildcard_str = ".".join(map(str, wildcard_parts))
        
        results.append({
            "name": name,
            "hosts_requested": hosts_needed,
            "hosts_allocated": (2 ** host_bits) - 2,
            "network_address": str(sub_net.network_address),
            "cidr": f"/{prefix_len}",
            "full_cidr": f"{sub_net.network_address}/{prefix_len}",
            "netmask": str(sub_net.netmask),
            "wildcard": wildcard_str,
            "first_usable": first_usable,
            "last_usable": last_usable,
            "broadcast": str(sub_net.broadcast_address),
            "default_gateway": gateway
        })
        
        current_ip_int = subnet_end_int + 1
        
    return results


def calculate_flsm(network_block: str, subnets_request: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calcula la partición de un bloque de red IPv4 mediante FLSM (Fixed Length Subnet Mask)
    aplicando el criterio de host (determinando la máscara a partir de la mayor demanda de hosts).
    """
    base_net = ipaddress.IPv4Network(network_block, strict=True)
    if not subnets_request:
        return []

    # Criterio de host: determinar bits de host segun la mayor demanda critica
    max_hosts = max(req.get("hosts_needed", 2) for req in subnets_request)
    needed_total = max_hosts + 2
    host_bits = max(2, math.ceil(math.log2(needed_total)))
    prefix_len = 32 - host_bits
    subnet_size = 2 ** host_bits

    current_ip_int = int(base_net.network_address)
    base_end_int = int(base_net.broadcast_address)
    results = []

    for req in subnets_request:
        name = req.get("name", "Subred")
        hosts_needed = req.get("hosts_needed", 2)
        subnet_end_int = current_ip_int + subnet_size - 1

        if subnet_end_int > base_end_int:
            raise ValueError(
                f"Capacidad excedida: El bloque base '{network_block}' no tiene suficiente espacio "
                f"para alojar la subred '{name}' con mascara /{prefix_len}."
            )

        sub_net = ipaddress.IPv4Network((current_ip_int, prefix_len))
        first_usable = str(sub_net.network_address + 1)
        last_usable = str(sub_net.broadcast_address - 1)
        gateway = first_usable

        netmask_parts = [int(p) for p in str(sub_net.netmask).split('.')]
        wildcard_parts = [255 - p for p in netmask_parts]
        wildcard_str = ".".join(map(str, wildcard_parts))

        results.append({
            "name": name,
            "hosts_requested": hosts_needed,
            "hosts_allocated": (2 ** host_bits) - 2,
            "network_address": str(sub_net.network_address),
            "cidr": f"/{prefix_len}",
            "full_cidr": f"{sub_net.network_address}/{prefix_len}",
            "netmask": str(sub_net.netmask),
            "wildcard": wildcard_str,
            "first_usable": first_usable,
            "last_usable": last_usable,
            "broadcast": str(sub_net.broadcast_address),
            "default_gateway": gateway
        })

        current_ip_int = subnet_end_int + 1

    return results
