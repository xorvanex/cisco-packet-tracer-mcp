"""Data models for Cisco Packet Tracer network topologies."""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class Interface(BaseModel):
    name: str = Field(..., description="Nombre del puerto, ej. GigabitEthernet0/0 o FastEthernet0/1")
    ip_address: Optional[str] = Field(None, description="Dirección IPv4, ej. 192.168.1.1")
    subnet_mask: Optional[str] = Field(None, description="Máscara de subred, ej. 255.255.255.0")
    description: Optional[str] = Field(None, description="Descripción del enlace o propósito del puerto")
    mode: Optional[Literal["access", "trunk", "routed"]] = Field("access", description="Modo del puerto en switch")
    vlan_id: Optional[int] = Field(None, description="ID de VLAN asignada en modo acceso")
    native_vlan: Optional[int] = Field(1, description="VLAN nativa para puertos troncales")
    enabled: bool = Field(True, description="Estado administrativo (no shutdown)")


class SubInterface(BaseModel):
    name: str = Field(..., description="Nombre de subinterfaz, ej. GigabitEthernet0/0.10")
    vlan_id: int = Field(..., description="ID de VLAN para encapsulación 802.1Q")
    ip_address: str = Field(..., description="Dirección IP de la subinterfaz (Gateway de la VLAN)")
    subnet_mask: str = Field(..., description="Máscara de subred")
    description: Optional[str] = Field(None, description="Descripción de la subinterfaz")


class VLAN(BaseModel):
    id: int = Field(..., ge=1, le=4094, description="ID numérico de la VLAN (1-4094)")
    name: str = Field(..., description="Nombre descriptivo de la VLAN, ej. VENTAS, DOCENTES")


class OSPFNetwork(BaseModel):
    network: str = Field(..., description="Dirección de red, ej. 192.168.10.0")
    wildcard: str = Field(..., description="Máscara wildcard, ej. 0.0.0.255")
    area: int = Field(0, description="Número de área OSPF, típicamente 0 (backbone)")


class RoutingOSPF(BaseModel):
    protocol: Literal["ospf"] = "ospf"
    process_id: int = Field(1, ge=1, le=65535, description="ID de proceso OSPF")
    router_id: Optional[str] = Field(None, description="ID de router OSPF, ej. 1.1.1.1")
    networks: List[OSPFNetwork] = Field(default_factory=list, description="Redes anunciadas")
    passive_interfaces: List[str] = Field(default_factory=list, description="Interfaces pasivas para evitar envios innecesarios de Hello packets")


class RoutingRIP(BaseModel):
    protocol: Literal["rip"] = "rip"
    version: int = Field(2, ge=1, le=2, description="Versión de RIP (1 o 2)")
    no_auto_summary: bool = Field(True, description="Desactivar auto-resumen")
    networks: List[str] = Field(default_factory=list, description="Redes principales o con clase anunciadas")
    passive_interfaces: List[str] = Field(default_factory=list, description="Interfaces pasivas para no enviar updates")
    redistribute_static: bool = Field(False, description="Redistribuir rutas estáticas en RIP")
    metric_static: Optional[int] = Field(1, description="Métrica de redistribución estática")
    default_information_originate: bool = Field(False, description="Propagar ruta por defecto en RIP")


class StaticRoute(BaseModel):
    network: str = Field(..., description="Red destino")
    mask: str = Field(..., description="Máscara de la red destino")
    next_hop: str = Field(..., description="Dirección IP del siguiente salto o interfaz de salida")


class DHCPPool(BaseModel):
    name: str = Field(..., description="Nombre del pool DHCP")
    network: str = Field(..., description="Red del pool")
    mask: str = Field(..., description="Máscara de la red")
    default_router: str = Field(..., description="Default gateway entregado por DHCP")
    dns_server: Optional[str] = Field("8.8.8.8", description="Servidor DNS")
    excluded_addresses: List[str] = Field(default_factory=list, description="Direcciones excluidas del pool")


class Device(BaseModel):
    id: str = Field(..., description="Identificador único del equipo (ej. R1, SW1, PC_1)")
    model: str = Field("2911", description="Modelo en Packet Tracer (ej. 2911, 1941, 2960-24TT, PC-PT, Server-PT)")
    type: Literal["router", "switch", "pc", "server"] = Field(..., description="Tipo de dispositivo")
    hostname: Optional[str] = Field(None, description="Hostname configurado en el equipo (por defecto id)")
    interfaces: List[Interface] = Field(default_factory=list, description="Puertos físicos del equipo")
    subinterfaces: List[SubInterface] = Field(default_factory=list, description="Subinterfaces 802.1Q")
    vlans: List[VLAN] = Field(default_factory=list, description="VLANs configuradas en el switch")
    routing_ospf: Optional[RoutingOSPF] = Field(None, description="Configuración OSPF si aplica")
    routing_rip: Optional[RoutingRIP] = Field(None, description="Configuración RIP si aplica")
    static_routes: List[StaticRoute] = Field(default_factory=list, description="Rutas estáticas")
    dhcp_pools: List[DHCPPool] = Field(default_factory=list, description="Servidores DHCP locales")
    
    # Para dispositivos finales (PC/Server)
    ip_address: Optional[str] = Field(None, description="IP del host final")
    subnet_mask: Optional[str] = Field(None, description="Máscara del host final")
    default_gateway: Optional[str] = Field(None, description="Gateway del host final")
    dns_server: Optional[str] = Field(None, description="DNS del host final")


class Link(BaseModel):
    from_device: str = Field(..., description="ID del dispositivo de origen")
    from_port: str = Field(..., description="Puerto de origen")
    to_device: str = Field(..., description="ID del dispositivo de destino")
    to_port: str = Field(..., description="Puerto de destino")
    cable_type: Literal["copper_straight", "copper_cross", "fiber", "serial"] = Field(
        "copper_straight", description="Tipo de medio de transmisión"
    )


class NetworkTopology(BaseModel):
    project_name: str = Field(..., description="Nombre identificador del proyecto o laboratorio")
    description: Optional[str] = Field(None, description="Descripción de los objetivos de la red")
    devices: List[Device] = Field(..., description="Lista de dispositivos en la topología")
    links: List[Link] = Field(default_factory=list, description="Lista de interconexiones físicas")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales del laboratorio")
