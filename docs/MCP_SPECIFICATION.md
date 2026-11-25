# 📋 Especificación de Herramientas MCP - Cisco Packet Tracer

Este documento define el catálogo de herramientas (**tools**) que el servidor MCP expone para cualquier modelo de lenguaje o cliente MCP.

---

## 1. `calculate_vlsm_subnets`
Calcula la partición de un bloque de red IPv4 en múltiples subredes de tamaño variable (VLSM) según la cantidad de hosts requerida para cada segmento.

### Argumentos:
```json
{
  "network_block": "192.168.1.0/24",
  "subnets": [
    {"name": "VLAN10_VENTAS", "hosts_needed": 50},
    {"name": "VLAN20_TI", "hosts_needed": 20},
    {"name": "ENLACE_WAN_R1_R2", "hosts_needed": 2}
  ]
}
```

### Respuesta:
Retorna para cada subred:
- Dirección de red (`Network`) y prefijo CIDR (`CIDR`).
- Máscara de subred en formato decimal punteado (`Subnet Mask`) y wildcard (`Wildcard Mask`).
- Rango de IPs utilizables (`First Usable`, `Last Usable`).
- Dirección de broadcast (`Broadcast`).
- Gateway sugerido (por convención, la primera o última IP utilizable).

---

## 2. `create_network_topology`
Crea una topología de red completa en memoria a partir de una descripción estructurada de dispositivos, enlaces, VLANs y configuraciones de enrutamiento.

### Argumentos:
```json
{
  "project_name": "lab_red_universidad",
  "description": "Laboratorio con 2 routers OSPF, 2 switches Catalyst y 4 PCs",
  "devices": [
    {
      "id": "R1",
      "model": "2911",
      "type": "router",
      "interfaces": [
        {"name": "GigabitEthernet0/0", "ip_address": "192.168.10.1", "subnet_mask": "255.255.255.0", "description": "LAN Facultad"},
        {"name": "GigabitEthernet0/1", "ip_address": "10.0.0.1", "subnet_mask": "255.255.255.252", "description": "WAN a R2"}
      ],
      "routing": {
        "protocol": "ospf",
        "process_id": 1,
        "networks": [
          {"network": "192.168.10.0", "wildcard": "0.0.0.255", "area": 0},
          {"network": "10.0.0.0", "wildcard": "0.0.0.3", "area": 0}
        ]
      }
    }
  ],
  "links": [
    {
      "from_device": "R1",
      "from_port": "GigabitEthernet0/1",
      "to_device": "R2",
      "to_port": "GigabitEthernet0/1",
      "cable_type": "copper_straight"
    }
  ]
}
```

---

## 3. `audit_network_topology`
Realiza una auditoría exhaustiva de la topología antes de su implementación física o lógica en Packet Tracer.

### Validaciones realizadas:
1. **Detección de IPs duplicadas:** Ninguna dirección IP debe repetirse en distintas interfaces.
2. **Consistencia de enlaces:** Ambos extremos de un cable deben compartir la misma red IP y máscara.
3. **Consistencia de Gateways:** Los dispositivos finales (PCs/Laptops/Servidores) deben apuntar a una IP existente en su mismo dominio de broadcast.
4. **VLANs y Troncales:** Si un puerto de acceso está en una VLAN, dicha VLAN debe estar definida en el switch. Los enlaces entre switches deben ser `trunk`.
5. **Wildcard Masks en OSPF:** Verificación estricta de que la máscara wildcard corresponda matemáticamente a la máscara de subred.

---

## 4. `generate_cisco_ios_configs`
Transforma la topología en scripts de configuración Cisco IOS (`running-config`) para cada router y switch.

### Incluye:
- Hostname del equipo.
- Contraseñas cifradas (`service password-encryption`, `enable secret`).
- Banners de advertencia (`banner motd`).
- Configuración de interfaces (IPs, descripciones, `no shutdown`).
- Subinterfaces con encapsulación 802.1Q para Router-on-a-Stick.
- Servidores DHCP locales (`ip dhcp pool`, `excluded-address`).
- Protocolos de enrutamiento dinámico (OSPF, RIP) o rutas estáticas (`ip route`).
- Líneas de consola y VTY con autenticación local y timeout.

---

## 5. `export_topology_package`
Guarda el proyecto completo en el directorio de salida del usuario con la siguiente estructura de entrega:
- `README.md` del laboratorio con explicación detallada.
- `addressing_table.md` y `addressing_table.csv` con la tabla de direccionamiento.
- `topology_diagram.md` con el diagrama visual en Mermaid.
- Carpeta `configs/` con los archivos `.ios` individuales para cada dispositivo.
- `automation_script.ptst` o script de aprovisionamiento de Packet Tracer.
- `audit_report.json` con el resultado de la auditoría.
