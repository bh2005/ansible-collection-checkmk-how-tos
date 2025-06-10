# Cómo configurar los tiempos de caída en checkmk con la colección Ansible

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


Esto cómo describe cómo `downtimes.yml` del repositorio [Checkmk/ansible-colection-checkmk. General](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/downtimes.yml) se utiliza para planificar el tiempo de inactividad (tiempos de inactividad) para hosts y servicios en checkmk. El libro de jugadas usa el `checkmk.general` colección Ansible para establecer tiempos para individuos o varios anfitriones, así como servicios específicos.

## Requisitos previos
- **Ansible**: Instalado y configurado (compatible con la colección).
- **Colección de checkmk.general**: Instalado a través de `ansible-galaxy collection install checkmk.general`.
- **Servidor checkmk**: Acceso a una instancia de checkmk con API web activada.
- **Datos de acceso a la API**: Nombre de usuario (`automation_user`) y contraseña/secreto (`automation_secret`) para la API de automatización.
- **Bóveda (recomendado)**: Para el almacenamiento seguro del `automation_secret`.
- **Acceso a la red**: El controlador Ansible debe poder comunicarse con el servidor CheckMK a través de HTTP/HTTPS.
- **Anfitriones/servicios**: Los anfitriones dados en el libro de jugadas (p. Ej.`example.com`) y servicios (por ejemplo, B.`Filesystem /`,`Ping`) debe existir en la instancia de checkmk.

## Pasos

### 1. Descargar Playbook
Clonar el repositorio o copiar el libro de jugadas `downtimes.yml` en su controlador Ansible:

```bash
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
cd ansible-collection-checkmk.general/playbooks/demo
```

El libro de jugadas se ve así (extracto para una descripción general):
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "http://localhost" 
    site: "mysite" 
    automation_user: "automation" 
    automation_secret: "mysecret" 
    comment: "Ansible Downtime" 
    duration: 60
  tasks:
    - name: Set a downtime for a single host
      checkmk.general.downtime:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        hostname: "example.com" 
        comment: "{{ comment }}" 
        duration: "{{ duration }}" 
        state: present
    - name: Set a downtime for multiple hosts
      checkmk.general.downtime:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        hostname: "{{ item }}" 
        comment: "{{ comment }}" 
        duration: "{{ duration }}" 
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}" 
    - name: Set a downtime for a service
      checkmk.general.downtime:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        hostname: "example.com" 
        service: "Filesystem /" 
        comment: "{{ comment }}" 
        duration: "{{ duration }}" 
        state: present
    - name: Set a downtime for a service on multiple hosts
      checkmk.general.downtime:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        hostname: "{{ item }}" 
        service: "Ping" 
        comment: "{{ comment }}" 
        duration: "{{ duration }}" 
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}" 
```

### 2. Ajuste las variables
Ajuste las variables en el libro de jugadas a su entorno:
- **servidor_url**: Reemplazar `http://localhost` A través de la URL de su servidor checkmk (p. Ej.`https://monitoring.example.com`).
- **sitio**: Reemplazar `mysite` por el nombre de su sitio de chechmk.
- **Automatización_user**: Use el nombre de usuario para la API de automatización (p. Ej.`automation`).
- **Automatización_secret**: Reemplazar `mysecret` a través de la contraseña o token de la API.
- **nombre de host**: Asegúrese de que el host (p. Ej.`example.com`) existe en su instancia de checkmk.
- **servicio**: Verifique que los servicios (p. Ej.`Filesystem /`,`Ping`) se definen en checkmk.
- **consulta**: Ajuste la consulta en el complemento de búsqueda para filtrar los hosts deseados (p.`{"host_tags": {"os": "linux"}}` para hosts de Linux).

 **Recomendación**: Guarda eso `automation_secret` en un archivo de bóveda ansible para aumentar la seguridad.

#### Crear el archivo de bóveda
```bash
ansible-vault create vault.yml
```

Contenido del `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

Edite el libro de jugadas para usar la variable de bóveda:
```yaml
automation_secret: "{{ vault_automation_secret }}" 
```

### 3. Run Playbook
Realice el libro de jugadas para configurar los tiempos:

```bash
ansible-playbook downtimes.yml --vault-id vault.yml
```

### 4. Tareas del libro de jugadas
El libro de jugadas realiza cuatro tareas:
1. **Tiempo de inactividad para un solo anfitrión**:
   - Setzt eine 60-minütige Ausfallzeit für den Host `example.com` con el comentario `Ansible Downtime`.
2. **Tiempo de inactividad para varios anfitriones**:
   - Ruft alle Hosts mit dem Tag `os: linux` sobre el complemento de búsqueda `checkmk.general.host` y establece un tiempo de inactividad de 60 minutos para todos.
3. **Tiempo de inactividad para un servicio**:
   - Setzt eine 60-minütige Ausfallzeit für den Service `Filesystem /` en el anfitrión `example.com`.
4. **Tiempo de inactividad para un servicio en varios anfitriones**:
   - Setzt eine 60-minütige Ausfallzeit für den Service `Ping` en todos los anfitriones con el día `os: linux`.

### 5. Verifique el tiempo de inactividad
Después de ejecutar el libro de jugadas:
1. Regístrese en el área web de Checkmk y navegue **Monitor> todos los hosts** o **Monitor> todos los servicios**.
2. Revise el tiempo de inactividad bajo **Tiempos de inactividad**(por ejemplo, en el menú de host o servicio).
3. Alternativamente, consulte los tiempos de inactividad a través de la API CHECKMK:
```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/downtime/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json" 
   ```

### 6. Tratamiento de errores
- **Host/servicio no encontrado**: Si el host (p.`example.com`) o el servicio (p.`Filesystem /`) no existe, la tarea falla. Verifique la ortografía y la existencia en checkmk.
- **Datos de acceso no válidos**: Asegúrate de que `automation_user` y `automation_secret` son correctos.
- **Problemas de red**: Verifique la accesibilidad del servidor checkmk (`server_url`) y el puerto compartido correcto (http/https).
- **Certificados TLS**: En https, asegúrese de que el certificado sea válido o establecido `validate_certs: false` en el libro de jugadas (solo para entornos de prueba).
- **Error de complemento de búsqueda**: Si la consulta en el complemento de búsqueda no devuelve los hosts, verifique eso `query`-Attribut (z. B. `{"host_tags": {"os": "linux"}}`).

### 7. Ajustes y extensiones
- **Listas de host dinámicos**: Ajuste la consulta en el complemento de búsqueda para usar otros criterios (p.`{"host_labels": {"env": "prod"}}`).
- - **Otros parámetros de tiempo de inactividad**: Agregar otros parámetros, cómo `start_time` o `end_time` para definir el tiempo de inactividad con mayor precisión (ver [Documentación de checkmk](https://docs.checkmk.com/latest/en/rest_api.html)).
- **Eliminar los tiempos de inactividad**: Colocar `state: absent` en las tareas para eliminar el tiempo de inactividad existente.
- **automatización**: Planifique el libro de jugadas con un programador (por ejemplo, Ansible Tower/Awx o Cron) para establecer el tiempo de inactividad regular.

## Referencias
- **Seguridad**: Siempre use un archivo de bóveda para eso `automation_secret` para proteger los datos confidenciales.
- **Versión checkmk**: Asegúrate de que `checkmk.general` la colección es compatible con su versión checkmk (ver `SUPPORT.md` en el repositorio).
- - **documentación**: Se pueden encontrar más detalles sobre módulos y complementos de búsqueda en el [Documentación de Github](https://github.com/Checkmk/ansible-collection-checkmk.general) O en Ansible Galaxy.
- **Entorno de prueba**: Pruebe el libro de jugadas en un entorno no productivo para evitar efectos inesperados.
- **Valores de muestra**: El libro de jugadas usa un marcador de posición (`example.com`,`http://localhost`). Adaptarlo a su entorno real.

## Conclusión
El libro de jugadas `downtimes.yml` ofrece una forma flexible de establecer el tiempo de inactividad en checkmk para hosts y servicios, tanto para individuos como para varios objetos. Con el `checkmk.general` la recolección puede automatizar eficientemente las ventanas de mantenimiento, que es particularmente útil para fallas planificadas o trabajos de mantenimiento regulares. Al adaptar las variables y las consultas, puede adaptar el libro de jugadas a sus requisitos específicos.