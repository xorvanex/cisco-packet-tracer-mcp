"""Packet Tracer Script Engine automation script generator."""

from typing import List
from ..core.models import NetworkTopology


def generate_pt_automation_script(topology: NetworkTopology) -> str:
    """Genera un script de automatización para el motor interno de Packet Tracer (QtScript)."""
    lines: List[str] = []
    lines.append("// ==============================================================")
    lines.append(f"// Script de Despliegue Automatizado para Cisco Packet Tracer")
    lines.append(f"// Proyecto: {topology.project_name}")
    lines.append("// ==============================================================")
    lines.append("var app = ipc.getApp();")
    lines.append("var network = app.getNetwork();")
    lines.append("")
    lines.append("// 1. Creacion de Dispositivos en el Workspace Logico")
    
    # Coordenadas simples en cuadrícula
    x, y = 100, 100
    for i, dev in enumerate(topology.devices):
        lines.append(f"// Dispositivo {dev.id}")
        lines.append(f"var dev_{dev.id} = network.addDevice('{dev.model}', '{dev.id}', {x}, {y});")
        x += 180
        if (i + 1) % 4 == 0:
            x = 100
            y += 150
            
    lines.append("")
    lines.append("// 2. Creacion de Enlaces Fisicos")
    for link in topology.links:
        lines.append(
            f"network.addLink('{link.from_device}', '{link.from_port}', "
            f"'{link.to_device}', '{link.to_port}', '{link.cable_type}');"
        )
        
    lines.append("")
    lines.append("// Fin del Script de Inicializacion")
    return "\n".join(lines)
