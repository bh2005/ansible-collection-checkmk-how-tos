# Colección Ansible para checkmk: Cómo para usuarios de habla alemana

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


¡Bienvenido a este repositorio! Aquí ofrezco a los usuarios alemanes una forma integral de usar el `checkmk.general` colección Ansible para checkmk. El objetivo es simplificar la automatización de las tareas de checkmk, como la gestión de hosts, servicios, reglas, tiempos de inactividad y más.

## Sobre este repositorio
En este repositorio ([BH2005/Ansible-Things/Ansible Collection](https://github.com/bh2005/ansible-things/tree/main/ansible-collection)) Encuentre instrucciones, ejemplos y consejos sobre cómo usar la colección checkmk ansible de manera efectiva. El contenido está especialmente preparado para que los usuarios de lo que hablan alemán minimicen los obstáculos de entrada.

## La colección checkmk ansible
El `checkmk.general` la colección es desarrollada y mantenida por Checkmk. Permite la automatización de las tareas de monitoreo en checkmk a través de Ansible, que incluye:
- Crear y administrar carpetas, hosts, reglas y usuarios.
- Planificación de tiempo de inactividad (tiempos de inactividad).
- Gestionar agentes y grupos de anfitriones.
- Inventario dinámico basado en datos de checkmk.

Puede encontrar el repositorio oficial de la colección aquí:
 [https://github.com/checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general) 

## Libros de jugadas de demostración
La colección oficial contiene una serie de libros de jugadas de demostración que demuestran varias aplicaciones. Puedes encontrar esto en el directorio:
 [https://github.com/checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo](https://github.com/Checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo) 

Los ejemplos incluyen:
- **tiempos de caída.yml**: Planificación de tiempo de inactividad para anfitriones y servicios.
- Otros libros de jugadas para la gestión de anfitriones, agentes y reglas.

Estos libros de jugadas de demostración sirven como punto de partida para comprender las funcionalidades de la colección y crear sus propios libros de jugadas.

## Cómo empiezas
1. **Instalar la colección**:
```bash
   ansible-galaxy collection install checkmk.general
   ```
2. **Requisitos previos**:
   - Ansible (kompatible Version).
   - Zugang zu einem Checkmk-Server mit aktivierter Web-API.
   - API-Zugangsdaten (`automation_user` y `automation_secret`).
   - Optional: Ansible Vault für sichere Speicherung von Zugangsdaten.
3. **Use ejemplos**:
   - Klone das Repository der Collection oder dieses Repository, um die Demo-Playbooks zu testen.
   - Passe die Variablen (z. B. `server_url`,`site`,`automation_user`) a tu entorno.
4. **Leer documentación**:
   - Die offizielle Dokumentation der Collection findest du im [Repositorio de Github](https://github.com/Checkmk/ansible-collection-checkmk.general).
   - Weitere Details zu Checkmk und seiner API sind in der [Documentación de checkmk](https://docs.checkmk.com) disponible.

## Contribuciones
¡Este repositorio debería crecer! Si desea contribuir con sus propias instrucciones, libros de jugadas o consejos para usuarios que hablan alemanes, cree una solicitud de extracción o contácteme [Bh2005/ansible-things](https://github.com/bh2005/ansible-things).

## Licencia
El contenido de este repositorio está sujeto a la misma licencia que la `checkmk.general` colección (ver [Licencia](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/LICENSE) en el repositorio oficial).

¡Diviértete automatizando con checkmk y ansible!