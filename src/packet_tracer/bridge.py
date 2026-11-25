"""Project packager and Packet Tracer file export."""

import os
import json
from pathlib import Path
from typing import Dict, Any

from ..core.models import NetworkTopology
from ..generators.ios_config import generate_all_ios_configs
from ..generators.documentation import generate_addressing_table, generate_mermaid_diagram
from ..generators.pt_script import generate_pt_automation_script
from ..validators.topology_validator import validate_topology


def export_topology_package(topology: NetworkTopology, output_base_dir: str) -> Dict[str, Any]:
    """Empaqueta y guarda la topología completa en disco.
    
    Crea la carpeta del proyecto conteniendo:
    - configs/*.ios (configuraciones por dispositivo)
    - addressing_table.md (tabla de direccionamiento)
    - topology_diagram.md (diagrama Mermaid)
    - automation_script.js (script de despliegue PT)
    - audit_report.json (informe de validación)
    - topology.json (definición estructurada)
    - README.md (guía de uso del laboratorio)
    """
    proj_dir = Path(output_base_dir) / topology.project_name
    configs_dir = proj_dir / "configs"
    
    os.makedirs(configs_dir, exist_ok=True)
    
    # 1. Auditoría
    audit = validate_topology(topology)
    with open(proj_dir / "audit_report.json", "w", encoding="utf-8") as f:
        json.dump(audit.model_dump(), f, indent=2, ensure_ascii=False)
        
    # 2. Configuraciones Cisco IOS
    ios_configs = generate_all_ios_configs(topology)
    for dev_id, cfg_text in ios_configs.items():
        with open(configs_dir / f"{dev_id}.ios", "w", encoding="utf-8") as f:
            f.write(cfg_text)
            
    # 3. Documentación
    addr_table = generate_addressing_table(topology)
    with open(proj_dir / "addressing_table.md", "w", encoding="utf-8") as f:
        f.write(addr_table)
        
    diagram = generate_mermaid_diagram(topology)
    with open(proj_dir / "topology_diagram.md", "w", encoding="utf-8") as f:
        f.write(f"# 🗺️ Diagrama de Red - {topology.project_name}\n\n{diagram}\n")
        
    # 4. Script de Packet Tracer
    pt_script = generate_pt_automation_script(topology)
    with open(proj_dir / "automation_script.js", "w", encoding="utf-8") as f:
        f.write(pt_script)
        
    # 5. Definición JSON de la topología
    with open(proj_dir / "topology.json", "w", encoding="utf-8") as f:
        json.dump(topology.model_dump(), f, indent=2, ensure_ascii=False)
        
    # 6. Generación nativa del archivo binario .pkt (Cisco Packet Tracer)
    pkt_file = proj_dir / f"{topology.project_name}.pkt"
    has_pkt = False
    try:
        from pkt_core.builder.lab import Lab
        lab = Lab()
        lab.drop_seed_devices()
        
        x_start, y_start = 120, 100
        x, y = x_start, y_start
        
        dev_sid_map = {}
        for i, dev in enumerate(topology.devices):
            cfg_lines = ios_configs.get(dev.id, "").splitlines() if dev.id in ios_configs else None
            pc_ip_tuple = (dev.ip_address, dev.subnet_mask, dev.default_gateway) if dev.ip_address and dev.subnet_mask and dev.default_gateway else None
            # Detectar si el router requiere tarjeta serial (HWIC-2T)
            needs_serial = False
            if dev.type.lower() == "router":
                for iface in dev.interfaces:
                    if iface.name.lower().startswith("serial") or iface.name.lower().startswith("se"):
                        needs_serial = True
                        break
                if not needs_serial:
                    for lk in topology.links:
                        if (lk.from_device == dev.id and (lk.from_port.lower().startswith("serial") or lk.from_port.lower().startswith("se"))) or \
                           (lk.to_device == dev.id and (lk.to_port.lower().startswith("serial") or lk.to_port.lower().startswith("se"))) or \
                           (lk.cable_type == "serial" and (lk.from_device == dev.id or lk.to_device == dev.id)):
                            needs_serial = True
                            break

            sid = lab.add_device(
                model=dev.model,
                name=dev.id,
                x=x,
                y=y,
                power=True,
                ios_config=cfg_lines,
                pc_ip=pc_ip_tuple,
                install="HWIC-2T" if needs_serial else None
            )
            dev_sid_map[dev.id] = sid
            x += 220
            if (i + 1) % 4 == 0:
                x = x_start
                y += 180

        for link in topology.links:
            cable_kind = "serial" if link.cable_type == "serial" else "copper"
            from_sid = dev_sid_map.get(link.from_device, link.from_device)
            to_sid = dev_sid_map.get(link.to_device, link.to_device)
            
            # Normalizar puertos en terminales/PCs (FastEthernet0)
            from_port = link.from_port
            to_port = link.to_port
            from_dev_obj = next((d for d in topology.devices if d.id == link.from_device), None)
            to_dev_obj = next((d for d in topology.devices if d.id == link.to_device), None)
            if from_dev_obj and from_dev_obj.type.lower() in ["pc", "host", "endpoint"] and from_port == "FastEthernet0/1":
                from_port = "FastEthernet0"
            if to_dev_obj and to_dev_obj.type.lower() in ["pc", "host", "endpoint"] and to_port == "FastEthernet0/1":
                to_port = "FastEthernet0"

            lab.link(from_sid, from_port, to_sid, to_port, kind=cable_kind)

        # Ajuste de version de Packet Tracer (9.0.1.0858 nativo)
        ver_elem = lab.base.find("VERSION")
        if ver_elem is not None:
            ver_elem.text = "9.0.1.0858"

        lab.save(str(pkt_file))
        has_pkt = True
        
        # También guardar copia en el directorio base si es distinto
        root_pkt = Path(output_base_dir) / f"{topology.project_name}.pkt"
        if root_pkt != pkt_file:
            lab.save(str(root_pkt))
    except Exception as exc:
        print(f"[bridge] Nota al compilar .pkt nativo: {exc}")

    # 7. README del Laboratorio
    readme_content = f"""# 🧪 Laboratorio de Red: {topology.project_name}

**Descripción:** {topology.description or 'Topología generada mediante Cisco Packet Tracer MCP'}  
**Estado de Auditoría:** {'✅ APROBADO' if audit.is_valid else '⚠️ CON ADVERTENCIAS/ERRORES'}  
**Total de Dispositivos:** {len(topology.devices)}  
**Total de Enlaces:** {len(topology.links)}  

---

## 📁 Contenido del Paquete
- `{topology.project_name}.pkt`: Archivo nativo de Cisco Packet Tracer listo para abrir con doble clic.
- `configs/`: Archivos de configuración Cisco IOS (`.ios`) listos para cada router y switch.
- `addressing_table.md`: Tabla completa de direccionamiento IPv4 y asignación de puertos.
- `topology_diagram.md`: Diagrama topológico en formato Mermaid.
- `automation_script.js`: Script de aprovisionamiento para el módulo de scripting de Packet Tracer.
- `audit_report.json`: Reporte de validación técnica y cumplimiento de normas.
- `topology.json`: Esquema declarativo de la topología.

---

## 🚀 Instrucciones de Despliegue en Cisco Packet Tracer

### Opción 1: Apertura Directa (.pkt)
Simplemente haz doble clic en `{topology.project_name}.pkt` o ábrelo desde Packet Tracer (`File -> Open`). La topología, el cableado y las configuraciones de red ya están cargados.

### Opción 2: Configuración Manual guiada por CLI
1. Abre **Cisco Packet Tracer**.
2. Añade los dispositivos según se especifica en `topology_diagram.md` e interconéctalos con los cables indicados.
3. Abre la consola CLI de cada router y switch.
4. Abre el archivo correspondiente en la carpeta `configs/` (ej. `configs/R1.ios`), copia todo el texto y pégalo directamente en la consola CLI.
5. Para las PCs, abre la pestaña **Desktop -> IP Configuration** y asigna los valores listados en `addressing_table.md`.
6. ¡Prueba la conectividad con comandos `ping` entre los extremos!
"""
    with open(proj_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
        
    generated_files = [
        str(proj_dir / "README.md"),
        str(proj_dir / "addressing_table.md"),
        str(proj_dir / "topology_diagram.md"),
        str(proj_dir / "automation_script.js"),
        str(proj_dir / "audit_report.json"),
        str(proj_dir / "topology.json"),
        *[str(configs_dir / f"{d}.ios") for d in ios_configs.keys()]
    ]
    if has_pkt:
        generated_files.insert(1, str(pkt_file))

    return {
        "status": "success",
        "project_directory": str(proj_dir),
        "audit_passed": audit.is_valid,
        "files_generated": generated_files
    }
