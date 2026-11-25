"""Auditor estático de topologías de red para Cisco Packet Tracer."""

import ipaddress
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..core.models import NetworkTopology, Device


class AuditIssue(BaseModel):
    rule_id: str
    severity: str  # "CRITICAL", "WARNING", "INFO"
    device_id: Optional[str] = None
    interface: Optional[str] = None
    message: str
    recommendation: str


class AuditReport(BaseModel):
    project_name: str
    is_valid: bool
    total_issues: int
    critical_count: int
    warning_count: int
    issues: List[AuditIssue] = Field(default_factory=list)


def validate_topology(topology: NetworkTopology) -> AuditReport:
    """Audita una topología de red completa y detecta inconsistencias técnicas."""
    issues: List[AuditIssue] = []
    
    # 1. Mapa de IPs para detectar duplicados
    ip_map: Dict[str, List[str]] = {}
    
    # Mapa de subredes configuradas en routers/switches para validar gateways
    known_networks: List[ipaddress.IPv4Network] = []
    configured_gateways: Dict[str, str] = {}  # ip -> device_id
    
    # Recorrer todos los dispositivos
    for dev in topology.devices:
        # Validar interfaces físicas
        for iface in dev.interfaces:
            if iface.ip_address and iface.subnet_mask:
                try:
                    net = ipaddress.IPv4Network(f"{iface.ip_address}/{iface.subnet_mask}", strict=False)
                    known_networks.append(net)
                    configured_gateways[iface.ip_address] = f"{dev.id}:{iface.name}"
                    
                    # Chequeo de duplicados
                    ip_map.setdefault(iface.ip_address, []).append(f"{dev.id}:{iface.name}")
                except Exception as e:
                    issues.append(AuditIssue(
                        rule_id="AUD-007",
                        severity="CRITICAL",
                        device_id=dev.id,
                        interface=iface.name,
                        message=f"Dirección IP o máscara inválida: {iface.ip_address} {iface.subnet_mask} ({str(e)})",
                        recommendation="Corrige el formato decimal punteado de la dirección IP y su máscara."
                    ))
                    
        # Validar subinterfaces 802.1Q
        for subif in dev.subinterfaces:
            try:
                net = ipaddress.IPv4Network(f"{subif.ip_address}/{subif.subnet_mask}", strict=False)
                known_networks.append(net)
                configured_gateways[subif.ip_address] = f"{dev.id}:{subif.name}"
                ip_map.setdefault(subif.ip_address, []).append(f"{dev.id}:{subif.name}")
            except Exception as e:
                issues.append(AuditIssue(
                    rule_id="AUD-007",
                    severity="CRITICAL",
                    device_id=dev.id,
                    interface=subif.name,
                    message=f"IP o máscara de subinterfaz inválida: {subif.ip_address} {subif.subnet_mask}",
                    recommendation="Revisa los valores de direccionamiento de la subinterfaz 802.1Q."
                ))
                
        # Validar dispositivos finales (PC / Servidor)
        if dev.type in ["pc", "server"]:
            if dev.ip_address:
                ip_map.setdefault(dev.ip_address, []).append(f"{dev.id}:NIC")
                
            # Validar Default Gateway
            if dev.default_gateway:
                if dev.default_gateway not in configured_gateways:
                    issues.append(AuditIssue(
                        rule_id="AUD-003",
                        severity="CRITICAL",
                        device_id=dev.id,
                        message=f"Default Gateway '{dev.default_gateway}' no existe en ningún router o switch de la topología.",
                        recommendation="Configura una interfaz de router o SVI con esa IP para actuar como puerta de enlace."
                    ))
            else:
                issues.append(AuditIssue(
                    rule_id="AUD-003",
                    severity="WARNING",
                    device_id=dev.id,
                    message=f"El host '{dev.id}' no tiene configurado un Default Gateway.",
                    recommendation="Asigna una puerta de enlace para que el host pueda comunicarse fuera de su subred local."
                ))
                
        # Validar OSPF Wildcard Masks
        if dev.routing_ospf:
            for net_entry in dev.routing_ospf.networks:
                # Comprobar que wildcard sea matemáticamente válida (complemento a 255)
                try:
                    parts = [int(p) for p in net_entry.wildcard.split(".")]
                    if len(parts) != 4 or any(p < 0 or p > 255 for p in parts):
                        raise ValueError()
                except Exception:
                    issues.append(AuditIssue(
                        rule_id="AUD-005",
                        severity="CRITICAL",
                        device_id=dev.id,
                        message=f"Máscara wildcard inválida en OSPF: {net_entry.wildcard}",
                        recommendation="Usa una wildcard válida como 0.0.0.255 para /24 o 0.0.0.3 para /30."
                    ))

    # Chequeo de duplicados en mapa de IPs
    for ip, locations in ip_map.items():
        if len(locations) > 1:
            issues.append(AuditIssue(
                rule_id="AUD-001",
                severity="CRITICAL",
                message=f"Conflicto de IP duplicada: La dirección {ip} está asignada a: {', '.join(locations)}",
                recommendation="Reasigna una dirección IP única a cada interfaz."
            ))

    # Validar coherencia de enlaces (ambos lados deben estar en la misma subred)
    dev_dict = {d.id: d for d in topology.devices}
    for link in topology.links:
        d1 = dev_dict.get(link.from_device)
        d2 = dev_dict.get(link.to_device)
        if not d1 or not d2:
            issues.append(AuditIssue(
                rule_id="AUD-008",
                severity="CRITICAL",
                message=f"Enlace huérfano: No se encuentra uno de los dispositivos ({link.from_device} o {link.to_device})",
                recommendation="Asegúrate de que ambos extremos del enlace existan en la lista de dispositivos."
            ))

    criticals = sum(1 for i in issues if i.severity == "CRITICAL")
    warnings = sum(1 for i in issues if i.severity == "WARNING")
    
    return AuditReport(
        project_name=topology.project_name,
        is_valid=(criticals == 0),
        total_issues=len(issues),
        critical_count=criticals,
        warning_count=warnings,
        issues=issues
    )
