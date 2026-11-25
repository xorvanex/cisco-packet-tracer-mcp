#!/usr/bin/env python3
"""
Cisco Packet Tracer MCP Server
Protocolo: Model Context Protocol (MCP) sobre stdio
Permite a asistentes de IA (Claude Code, OpenCode, Antigravity, Cursor, etc.)
diseñar, calcular VLSM, auditar, generar configuraciones Cisco IOS y exportar
proyectos completos para Cisco Packet Tracer.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Asegurar que el directorio raíz del proyecto esté en el sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.models import NetworkTopology, Device, Link
from src.core.subnetting import calculate_vlsm
from src.validators.topology_validator import validate_topology
from src.generators.ios_config import generate_all_ios_configs, generate_device_ios_config
from src.generators.documentation import generate_addressing_table, generate_mermaid_diagram
from src.packet_tracer.bridge import export_topology_package

DEFAULT_OUTPUT_DIR = os.environ.get(
    "PACKET_TRACER_OUTPUT_DIR",
    str(PROJECT_ROOT / "topologies_output")
)
TEMPLATES_DIR = PROJECT_ROOT / "templates" / "topologies"

# ==============================================================================
# DEFINICIÓN DE HERRAMIENTAS MCP (TOOLS)
# ==============================================================================

TOOLS_MANIFEST = [
    {
        "name": "calculate_vlsm_subnets",
        "description": "Calcula el direccionamiento IP de subredes de longitud variable (VLSM) a partir de un bloque base y requerimientos de hosts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "network_block": {
                    "type": "string",
                    "description": "Bloque IPv4 base en formato CIDR, ej: '192.168.1.0/24' o '10.0.0.0/16'"
                },
                "subnets": {
                    "type": "array",
                    "description": "Lista de requerimientos por subred",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Nombre de la subred o VLAN"},
                            "hosts_needed": {"type": "integer", "description": "Cantidad de hosts requeridos"}
                        },
                        "required": ["name", "hosts_needed"]
                    }
                }
            },
            "required": ["network_block", "subnets"]
        }
    },
    {
        "name": "audit_network_topology",
        "description": "Audita una topología de red detectando IPs duplicadas, inconsistencias de máscara, problemas de gateway y parámetros de seguridad.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {
                    "type": "object",
                    "description": "Objeto completo de topología según el esquema NetworkTopology"
                }
            },
            "required": ["topology"]
        }
    },
    {
        "name": "generate_cisco_ios_configs",
        "description": "Genera los archivos de configuración Cisco IOS (running-config) para cada router y switch de la topología.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {
                    "type": "object",
                    "description": "Objeto de topología con dispositivos, interfaces, VLANs y protocolos"
                }
            },
            "required": ["topology"]
        }
    },
    {
        "name": "export_topology_package",
        "description": "Empaqueta y guarda la topología completa en disco: configuraciones .ios, tablas de direccionamiento, diagramas Mermaid, scripts de Packet Tracer y reporte de auditoría.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topology": {
                    "type": "object",
                    "description": "Objeto NetworkTopology completo a persistir"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directorio de destino (opcional, por defecto topologies_output/)"
                }
            },
            "required": ["topology"]
        }
    },
    {
        "name": "list_topology_templates",
        "description": "Lista las plantillas de red predefinidas disponibles en el repositorio (ej. Router-on-a-stick, OSPF multi-sitio).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_topology_template",
        "description": "Obtiene una plantilla de topología completa en JSON para usarla como base de diseño.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_name": {
                    "type": "string",
                    "description": "Nombre de la plantilla, ej: 'router_on_a_stick'"
                }
            },
            "required": ["template_name"]
        }
    }
]

# ==============================================================================
# DISPATCHER DE HERRAMIENTAS
# ==============================================================================

def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    """Ejecuta la lógica de la herramienta solicitada."""
    if name == "calculate_vlsm_subnets":
        net_block = arguments["network_block"]
        subnets_req = arguments["subnets"]
        result = calculate_vlsm(net_block, subnets_req)
        return {"network_block": net_block, "allocated_subnets": result}

    elif name == "audit_network_topology":
        topo_data = arguments["topology"]
        topo = NetworkTopology(**topo_data)
        audit = validate_topology(topo)
        return audit.model_dump()

    elif name == "generate_cisco_ios_configs":
        topo_data = arguments["topology"]
        topo = NetworkTopology(**topo_data)
        configs = generate_all_ios_configs(topo)
        return {"device_configs": configs}

    elif name == "export_topology_package":
        topo_data = arguments["topology"]
        out_dir = arguments.get("output_dir") or DEFAULT_OUTPUT_DIR
        topo = NetworkTopology(**topo_data)
        result = export_topology_package(topo, out_dir)
        return result

    elif name == "list_topology_templates":
        templates = []
        if TEMPLATES_DIR.exists():
            for f in TEMPLATES_DIR.glob("*.json"):
                templates.append({
                    "name": f.stem,
                    "file": f.name
                })
        return {"available_templates": templates}

    elif name == "get_topology_template":
        tname = arguments["template_name"]
        if not tname.endswith(".json"):
            tname += ".json"
        target_file = TEMPLATES_DIR / tname
        if not target_file.exists():
            raise FileNotFoundError(f"Plantilla '{tname}' no encontrada en {TEMPLATES_DIR}")
        with open(target_file, "r", encoding="utf-8") as f:
            return json.load(f)

    else:
        raise ValueError(f"Herramienta desconocida: {name}")


# ==============================================================================
# MOTOR JSON-RPC 2.0 SOBRE STDIO (COMPATIBLE MCP)
# ==============================================================================

def run_stdio_server():
    """Bucle principal de servidor MCP sobre stdio."""
    # Desactivar buffering para salida inmediata
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip().lstrip('\ufeff')
            if not line:
                continue
                
            request = json.loads(line)
            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            # 1. Initialize
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "cisco-packet-tracer-mcp",
                            "version": "0.1.0"
                        }
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            # 2. Notificaciones (Initialized)
            elif method in ["notifications/initialized", "initialized"]:
                pass  # Confirmación de inicialización

            # 3. Ping
            elif method == "ping":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {}
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            # 4. Listar herramientas (tools/list)
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS_MANIFEST
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            # 5. Ejecutar herramienta (tools/call)
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                try:
                    result_data = handle_tool_call(tool_name, tool_args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result_data, indent=2, ensure_ascii=False)
                                }
                            ]
                        }
                    }
                except Exception as err:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "isError": True,
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error al ejecutar {tool_name}: {str(err)}"
                                }
                            ]
                        }
                    }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            else:
                # Método no soportado
                if req_id is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()

        except Exception as e:
            sys.stderr.write(f"[cisco-pt-mcp] Error en ciclo principal: {e}\n")
            sys.stderr.flush()


def main():
    run_stdio_server()


if __name__ == "__main__":
    main()
