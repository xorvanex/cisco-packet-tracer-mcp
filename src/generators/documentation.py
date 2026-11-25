"""Documentation generator (Addressing tables, diagrams, and summary sheets)."""

from typing import List, Dict, Any
from ..core.models import NetworkTopology


def generate_addressing_table(topology: NetworkTopology) -> str:
    """Genera una tabla de direccionamiento completa en formato Markdown."""
    lines: List[str] = []
    lines.append("# 📊 Tabla de Direccionamiento de Red")
    lines.append(f"**Proyecto:** {topology.project_name}  ")
    lines.append(f"**Descripción:** {topology.description or 'No provista'}  \n")
    lines.append("| Dispositivo | Interfaz | Dirección IP | Máscara de Subred | Default Gateway | Propósito / Descripción |")
    lines.append("|---|---|---|---|---|---|")
    
    for dev in topology.devices:
        # Interfaces físicas
        for iface in dev.interfaces:
            ip = iface.ip_address or "N/A (L2 / Sin IP)"
            mask = iface.subnet_mask or "N/A"
            gw = "N/A"
            desc = iface.description or ("Troncal" if iface.mode == "trunk" else f"VLAN {iface.vlan_id}" if iface.vlan_id else "-")
            lines.append(f"| **{dev.id}** | {iface.name} | `{ip}` | `{mask}` | `{gw}` | {desc} |")
            
        # Subinterfaces
        for subif in dev.subinterfaces:
            lines.append(
                f"| **{dev.id}** | {subif.name} | `{subif.ip_address}` | `{subif.subnet_mask}` | "
                f"`N/A (Es Gateway)` | {subif.description or f'VLAN {subif.vlan_id}'} |"
            )
            
        # Hosts finales (PC / Servidor)
        if dev.type in ["pc", "server"]:
            ip = dev.ip_address or "DHCP"
            mask = dev.subnet_mask or "DHCP"
            gw = dev.default_gateway or "DHCP"
            lines.append(f"| **{dev.id}** | FastEthernet0 | `{ip}` | `{mask}` | `{gw}` | Host de Usuario / Servidor |")
            
    return "\n".join(lines)


def generate_mermaid_diagram(topology: NetworkTopology) -> str:
    """Genera un diagrama Mermaid visual representando el mapa de la red."""
    lines: List[str] = []
    lines.append("```mermaid")
    lines.append("graph TD")
    lines.append("    %% Estilos de Nodos")
    lines.append("    classDef router fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#fff;")
    lines.append("    classDef switch fill:#16a34a,stroke:#15803d,stroke-width:2px,color:#fff;")
    lines.append("    classDef endpoint fill:#64748b,stroke:#475569,stroke-width:2px,color:#fff;")
    lines.append("")
    
    # Declaración de nodos con iconos/etiquetas
    for dev in topology.devices:
        label = f"{dev.id}<br/>({dev.model})"
        if dev.type == "router":
            lines.append(f'    {dev.id}["🌐 {label}"]:::router')
        elif dev.type == "switch":
            lines.append(f'    {dev.id}["🔀 {label}"]:::switch')
        else:
            lines.append(f'    {dev.id}["💻 {label}"]:::endpoint')
            
    lines.append("")
    lines.append("    %% Enlaces Físicos")
    for link in topology.links:
        link_label = f"{link.from_port} ↔ {link.to_port}"
        lines.append(f'    {link.from_device} ---|"{link_label}"| {link.to_device}')
        
    lines.append("```")
    return "\n".join(lines)
