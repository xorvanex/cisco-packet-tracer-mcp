# 🛡️ Política y Reglas de Auditoría de Red

Este documento define las comprobaciones automáticas ejecutadas por el módulo `src/validators/topology_validator.py` antes de autorizar la generación de configuraciones y despliegues en Cisco Packet Tracer.

---

## 1. Niveles de Severidad

- **CRITICAL (Error Crítico):** Impide el despliegue. Causa fallas directas de comunicación en la red (ej. IP duplicada o máscara inconsistente en un enlace).
- **WARNING (Advertencia):** La red podría funcionar, pero viola buenas prácticas de ingeniería o estándares de diseño (ej. falta de descripción en interfaces, VLANs sin nombre).
- **INFO (Informativo):** Sugerencias de optimización o recordatorios de configuración (ej. puertos sin apagar, MTU por defecto).

---

## 2. Catálogo de Reglas de Auditoría

### Regla AUD-001: No Duplicación de Direcciones IP
- **Severidad:** `CRITICAL`
- **Descripción:** Cada dirección IPv4/IPv6 asignada a una interfaz activa debe ser única en todo el dominio de enrutamiento.
- **Acción:** El validador detecta colisiones y señala los dos dispositivos en conflicto.

### Regla AUD-002: Coherencia de Subred en Enlaces Punto a Punto
- **Severidad:** `CRITICAL`
- **Descripción:** Las dos interfaces conectadas por un cable deben pertenecer exactamente a la misma subred y compartir la misma máscara.
- **Ejemplo:** Si el puerto `R1:Gi0/0` tiene `10.0.0.1/30`, el puerto `R2:Gi0/0` debe tener `10.0.0.2/30`. Asignar `10.0.0.5/30` o `10.0.0.2/24` provocará un error crítico.

### Regla AUD-003: Validación de Gateway para Hosts Finales
- **Severidad:** `CRITICAL`
- **Descripción:** Si una PC o Servidor tiene un Default Gateway configurado, esa dirección IP debe existir en alguna interfaz de router o switch L3 conectado al mismo segmento.

### Regla AUD-004: Consistencia de Troncales 802.1Q
- **Severidad:** `WARNING`
- **Descripción:** Si dos switches están interconectados y uno de ellos tiene el puerto en modo `trunk`, el extremo opuesto también debe estar en modo `trunk` y con la misma VLAN nativa (por defecto VLAN 1).

### Regla AUD-005: Coherencia de Máscara Wildcard en Protocolos de Enrutamiento
- **Severidad:** `CRITICAL`
- **Descripción:** En configuraciones de OSPF (`network X.X.X.X Y.Y.Y.Y area Z`), la máscara wildcard `Y.Y.Y.Y` debe coincidir exactamente con el complemento a uno de la máscara de subred (`255.255.255.255 - SubnetMask`).

### Regla AUD-006: Seguridad Mínima de Dispositivo
- **Severidad:** `WARNING`
- **Descripción:** Todo router y switch debe contar con `enable secret` y `service password-encryption` habilitados.
