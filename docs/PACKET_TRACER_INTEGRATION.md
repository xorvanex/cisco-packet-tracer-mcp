# 🔌 Integración con Cisco Packet Tracer

Este documento describe las técnicas utilizadas para interactuar con **Cisco Packet Tracer (v8.x y v9.x)** desde un entorno externo como este servidor MCP.

---

## 1. Métodos de Integración Soportados

Cisco Packet Tracer ofrece diferentes mecanismos para trabajar con configuraciones y topologías:

### Método A: Carga Directa de Configuraciones IOS (Recomendado y más confiable)
1. El servidor MCP genera archivos `.ios` individuales para cada dispositivo (ej. `R1.ios`, `SW1.ios`).
2. En Packet Tracer, el usuario o un script puede:
   - Abrir la pestaña **CLI** de cualquier dispositivo.
   - Copiar y pegar el bloque de comandos generado.
   - Alternativamente, configurar un servidor TFTP en la simulación y cargar la configuración mediante `copy tftp: running-config`.

### Método B: Scripting Interno de Packet Tracer (PT Script Engine / `.ptst`)
Packet Tracer incluye un motor de scripts basado en **QtScript / JavaScript** con una API de objetos:
- `ipc`: Módulo de comunicación entre procesos.
- `app.getNetwork()`: Retorna el grafo de red actual.
- `network.addDevice(type, model, x, y)`: Crea un dispositivo en el espacio de trabajo lógico.
- `network.addLink(dev1, port1, dev2, port2, cableType)`: Conecta dos interfaces.
- `device.getCommandLine()`: Permite enviar comandos IOS directamente al dispositivo.

El servidor MCP genera plantillas de scripts compatibles con este motor para que puedan ejecutarse desde el menú **Extensions -> Scripting Module** o mediante plantillas `.ptst`.

### Método C: Packet Tracer IPC API (TCP Port 39000)
Packet Tracer puede actuar como servidor IPC abriendo un socket TCP local (generalmente en el puerto `39000`).
- Activación en Packet Tracer: `Options -> Preferences -> IPC -> Enable IPC`.
- El servidor MCP incluye un puente en `src/packet_tracer/bridge.py` preparado para enviar tramas de automatización a través de dicho socket cuando está habilitado.

---

## 2. Modelos de Dispositivos Soportados

| Dispositivo | Modelo en Packet Tracer | Puertos Predeterminados | Rol Típico |
|---|---|---|---|
| Router | `2911` | 3x GigabitEthernet (0/0, 0/1, 0/2) | Gateway, Inter-VLAN, OSPF |
| Router | `1941` | 2x GigabitEthernet (0/0, 0/1) | Conexiones de sucursal |
| Switch L2 | `2960-24TT` | 24x FastEthernet, 2x GigabitEthernet | Conmutación de acceso, VLANs |
| Switch L3 | `3560-24PS` | 24x FastEthernet, 2x GigabitEthernet | Routing Inter-VLAN, SVI, DHCP |
| PC | `PC-PT` | 1x FastEthernet | Host final |
| Servidor | `Server-PT` | 1x FastEthernet | DNS, DHCP, Web, TFTP |

---

## 3. Convenciones de Puertos y Cables
- **Cables Directos (`copper_straight`):**
  - PC / Servidor a Switch.
  - Router a Switch.
- **Cables Cruzados (`copper_cross`):**
  - Switch a Switch (si MDIX no estuviera activo).
  - Router a Router (mediante interfaces Ethernet directas).
  - PC a PC.
- **Cables Seriales (`serial_dce` / `serial_dte`):**
  - Routers equipados con tarjetas HWIC-2T para enlaces WAN punto a punto tradicionales.
