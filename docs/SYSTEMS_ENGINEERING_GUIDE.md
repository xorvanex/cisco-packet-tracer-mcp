# 🎓 Guía de Ingeniería de Sistemas: Redes y Automatización (NetDevOps)

Esta guía complementa el proyecto con los fundamentos teóricos y metodológicos esenciales para estudiantes y futuros ingenieros de sistemas.

---

## 1. El Concepto de "Redes como Código" (Infrastructure as Code - IaC)

En la ingeniería de sistemas moderna, las redes ya no se configuran manualmente dispositivo por dispositivo a través de comandos lentos y propensos a error humano.
El enfoque de este proyecto aplica los principios de **NetDevOps**:
1. **Definición Declarativa:** Describimos el estado deseado de la red (dispositivos, subredes, VLANs) en un formato estructurado (JSON o YAML).
2. **Validación Automática:** Antes de tocar el hardware o simulador, auditamos la coherencia matemática y de seguridad del diseño.
3. **Generación Automatizada:** Los comandos y configuraciones se compilan de forma determinista a partir de plantillas estandarizadas.

---

## 2. Metodología de Subnetting y VLSM

El direccionamiento con **Máscaras de Subred de Longitud Variable (VLSM)** optimiza el espacio de direcciones IP evitando el desperdicio de direcciones:

### Pasos de cálculo VLSM:
1. **Ordenar los requerimientos de mayor a menor número de hosts necesarios.**
2. **Calcular la cantidad de bits de host requeridos:**
   $$\text{Hosts utilizables} = 2^h - 2 \ge \text{Requerimiento}$$
   *(Se restan 2 direcciones: la dirección de red y la de broadcast).*
3. **Calcular la nueva máscara de subred (prefijo CIDR):**
   $$\text{CIDR} = 32 - h$$
4. **Asignar la primera subred disponible en el bloque base.**
5. **Calcular el salto de red:**
   $$\text{Salto} = 2^h$$
6. **Repetir el proceso para el siguiente segmento.**

---

## 3. Arquitectura Jerárquica de Red de Cisco

Al diseñar topologías en este MCP, seguimos el modelo clásico de 3 capas de Cisco:
- **Capa de Núcleo (Core):** Enrutamiento de alta velocidad entre centros de datos o sitios principales (routers con OSPF/BGP).
- **Capa de Distribución:** Enrutamiento Inter-VLAN, políticas de acceso (ACLs), filtrado y agregación de enlaces.
- **Capa de Acceso:** Conexión directa a los usuarios finales (switches L2 con seguridad de puertos `port-security` y VLANs).

---

## 4. Estándares de Seguridad Base para Dispositivos Cisco IOS

Cualquier configuración generada por este MCP debe cumplir con el siguiente estándar de endurecimiento (*hardening*):
- Cifrado de todas las contraseñas en texto claro (`service password-encryption`).
- Contraseña secreta robusta para modo EXEC privilegiado (`enable secret`).
- Autenticación en la línea de consola (`line console 0`) con timeout de inactividad (`exec-timeout 5 0`).
- Configuración de líneas VTY para acceso SSH o Telnet controlado.
- Mensaje legal de advertencia contra accesos no autorizados (`banner motd`).
- Desactivación de interfaces no utilizadas (`shutdown`).
