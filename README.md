<div align="center">

# 🌐 Cisco Packet Tracer MCP Server

**Servidor Model Context Protocol (MCP) para diseñar, calcular, auditar y empaquetar topologías de red Cisco Packet Tracer directamente desde asistentes de IA.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/Protocol-MCP%20(stdio%20%2F%20JSON--RPC%202.0)-0EA5E9)](https://modelcontextprotocol.io/)
[![Pydantic](https://img.shields.io/badge/Validation-Pydantic%20v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Packet Tracer](https://img.shields.io/badge/Cisco%20Packet%20Tracer-8.x%20%2F%209.x%20(.pkt)-1BA0D7?logo=cisco&logoColor=white)](https://www.netacad.com/courses/packet-tracer)
[![License: MIT](https://img.shields.io/badge/License-MIT-8B5CF6.svg)](LICENSE)

</div>

---

## 📌 ¿Qué es y cómo funciona?

**`cisco-packet-tracer-mcp`** conecta asistentes de IA compatibles con MCP (**Claude Code**, **Claude Desktop**, **Cursor**, **Antigravity**, **OpenCode**) con un motor determinista de ingeniería de redes en Python.

En lugar de que la IA escriba comandos Cisco IOS "de memoria" con errores de subredes o IPs repetidas, el flujo trabaja en 4 etapas:

```text
Prompt en lenguaje natural
   │
   ▼
Asistente IA (razona sobre la topología y llama herramientas MCP vía stdio)
   │
   ├─► 1. calculate_vlsm_subnets    → Particiona bloques IPv4 sin solapamientos
   ├─► 2. audit_network_topology    → Valida IPs duplicadas, gateways y wildcards
   ├─► 3. generate_cisco_ios_configs→ Genera scripts Cisco IOS por dispositivo
   └─► 4. export_topology_package   → Exporta carpeta completa + archivo binario .pkt
```

---

## 🛠️ Stack Tecnológico

| Tecnología | Rol en el proyecto |
|----|-- --|
| **Python 3.10+** | Lenguaje base del servidor y lógica de red |
| **MCP (`stdio` / JSON-RPC 2.0)** | Comunicación estándar entre cliente IA y servidor |
| **Pydantic v2** | Validación de esquemas de topología (`Device`, `Link`, `VLAN`, etc.) |
| **`packet-tracer-pkt-format` (`pkt_core`)** | Compilación offline de archivos binarios `.pkt` para Packet Tracer |
| **Mermaid + Markdown** | Generación automática de diagramas y tablas de direccionamiento |

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Python 3.10** o superior.
- **Cisco Packet Tracer** (v8.x o v9.x) para abrir los archivos `.pkt` generados.
- Un cliente compatible con **MCP** (Claude Code, Claude Desktop, Cursor, Antigravity, etc.).

### 1. Crear entorno virtual e instalar desde `pyproject.toml`

En PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e .
```

> **Nota:** En Linux/macOS activa el entorno con `source .venv/bin/activate`.

### 2. Conectar el servidor en tu cliente MCP

Usa como base la plantilla [docs/mcp_config_example.json](docs/mcp_config_example.json) reemplazando `<RUTA_AL_PROYECTO>` por la ruta absoluta de este repositorio:

```json
{
  "mcpServers": {
    "cisco-packet-tracer": {
      "command": "<RUTA_AL_PROYECTO>/.venv/Scripts/python.exe",
      "args": [
        "<RUTA_AL_PROYECTO>/src/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PACKET_TRACER_OUTPUT_DIR": "<RUTA_AL_PROYECTO>/topologies_output"
      }
    }
  }
}
```

> Si instalaste el paquete con `pip install -e .`, también puedes usar el comando `cisco-pt-mcp` dentro del entorno virtual.

---

## 🧰 Herramientas MCP Expuestas

| Herramienta | Qué hace |
|-------------|------ ---|
| `calculate_vlsm_subnets` | Calcula subredes IPv4 por VLSM (red, máscara, wildcard, rango usable, broadcast y gateway) ordenando de mayor a menor demanda. |
| `audit_network_topology` | Audita un objeto `NetworkTopology` en busca de IPs duplicadas, gateways inexistentes, enlaces huérfanos y wildcards OSPF inválidas. |
| `generate_cisco_ios_configs` | Genera bloques de configuración Cisco IOS para routers y switches (interfaces, subinterfaces 802.1Q, VLANs, DHCP, OSPF, RIPv2 y rutas estáticas). |
| `export_topology_package` | Ejecuta auditoría, genera `.ios`, `addressing_table.md`, `topology_diagram.md`, `automation_script.js`, `topology.json`, `README.md` y compila el `.pkt` en `topologies_output/`. |
| `list_topology_templates` | Lista las plantillas JSON disponibles en `templates/topologies/`. |
| `get_topology_template` | Devuelve el JSON completo de una plantilla (ej. `router_on_a_stick`) como punto de partida. |

---

## 💡 Ejemplo de Uso desde la IA

Una vez conectado el MCP, puedes pedirle a tu asistente:

> *"Calcula subredes VLSM sobre `192.168.10.0/24` para Ventas (50 hosts), TI (20 hosts) y un enlace WAN (2 hosts). Luego carga la plantilla `router_on_a_stick`, adáptala y expórtala como paquete para Packet Tracer."*

El paquete generado aparecerá en `topologies_output/<project_name>/`:

```text
topologies_output/<project_name>/
├── <project_name>.pkt      # Topología compilada para abrir en Packet Tracer
├── configs/                # Archivos .ios individuales (R1.ios, SW1.ios, ...)
├── addressing_table.md     # Tabla de direccionamiento IPv4
├── topology_diagram.md     # Diagrama de red en Mermaid
├── automation_script.js    # Script de despliegue PT
├── audit_report.json       # Resultado de la auditoría
├── topology.json           # Definición estructurada de la topología
└── README.md               # Guía rápida del laboratorio
```

---

## 🗂️ Estructura del Proyecto

```text
cisco-packet-tracer-mcp/
├── pyproject.toml                  # Metadatos, dependencias y entrypoint (cisco-pt-mcp)
├── LICENSE                         # Licencia MIT
├── README.md                       # Documentación principal
├── .gitignore
├── src/
│   ├── server.py                   # Servidor MCP sobre stdio (JSON-RPC 2.0)
│   ├── core/
│   │   ├── models.py               # Esquemas Pydantic de topología y dispositivos
│   │   └── subnetting.py           # Motor de cálculo VLSM / FLSM
│   ├── validators/
│   │   └── topology_validator.py   # Auditor estático de topologías
│   ├── generators/
│   │   ├── ios_config.py           # Generador de configuraciones Cisco IOS
│   │   ├── documentation.py        # Tablas Markdown y diagramas Mermaid
│   │   └── pt_script.py            # Generador de script JS para Packet Tracer
│   └── packet_tracer/
│       └── bridge.py               # Empaquetador y compilador .pkt (vía pkt_core)
├── templates/
│   └── topologies/
│       └── router_on_a_stick.json  # Plantilla base Router-on-a-Stick
├── topologies_output/              # Carpeta de salida por defecto para proyectos
├── tests/                          # Pruebas unitarias (unittest)
└── docs/                           # Documentación técnica y ejemplo de config MCP
```

---

## 🧪 Pruebas

Para ejecutar la suite de pruebas unitarias sin generar archivos temporales:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
