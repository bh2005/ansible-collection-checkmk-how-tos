# Cómo crear grupos de host y servicios en checkmk desde un archivo CSV con la colección Ansible

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


Esto cómo describe cómo `groups.yml` del repositorio [Checkmk/ansible-colection-checkmk. General](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/groups.yml) ajustado para crear grupos de host y servicio en checkmk según un archivo CSV. Usa el `checkmk.general` colección ansible a grupos anfitriones (`checkmk.general.checkmk_hostgroup`) y grupos de servicio (`checkmk.general.checkmk_servicegroup`) para crear, así como el módulo `community.general.read_csv` para leer la información del grupo de un archivo CSV. Además, los hosts se pueden asignar a un grupo de host dinámicamente basado en etiquetas u otros criterios.

## Requisitos previos
- **Ansible**: Instalado y configurado (compatible con las colecciones).
- **Colección de checkmk.general**: Instalado a través de `ansible-galaxy collection install checkmk.general`.
- **Comunidad. Colección General**: Instalado a través de `ansible-galaxy collection install community.general`(para el `read_csv`-Modul).
- **Servidor checkmk**: Acceso a una instancia de checkmk con API web activada.
- **Datos de acceso a la API**: Nombre de usuario (`automation_user`) y contraseña/secreto (`automation_secret`) para la API de automatización.
- **Bóveda (recomendado)**: Para el almacenamiento seguro del `automation_secret`.
- **Acceso a la red**: El controlador Ansible debe poder comunicarse con el servidor CheckMK a través de HTTP/HTTPS.
- **Anfitrión**: Los anfitriones mencionados en el libro de jugadas (por ejemplo, con el día `os: linux`) debe existir en la instancia de checkmk.
- **Archivo CSV**: Un archivo CSV con la información del grupo que se lee en el libro de jugadas.

## Preparar el archivo CSV
Cree un archivo CSV (p. Ej.`groups.csv`) que define el host y los grupos de servicio. El archivo debe contener al menos las siguientes columnas:
- `type`: Tipo de grupo (`hostgroup` o `servicegroup`).
- `name`: Nombre del grupo (p. Ej.`web_servers`).
- `title`: Anuncios del grupo (p. Ej.`Web Servers`).

 **Ejemplo`groups.csv`**:
```csv
type,name,title
hostgroup,web_servers,Web Servers
hostgroup,db_servers,Database Servers
servicegroup,http_services,HTTP Services
servicegroup,database_services,Database Services
```

Guarde el archivo en el mismo directorio que el libro de jugadas o adapte la ruta en el libro de jugadas.

## Pasos

### 1. Cree o adapte el libro de jugadas
Crea un nuevo libro de jugadas (p. Ej.`create_groups_from_csv.yml`) o ajuste el original `groups.yml` para leer los grupos del archivo CSV.

 **Playbook:`create_groups_from_csv.yml`**:
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "https://monitoring.example.com" 
    site: "mysite" 
    automation_user: "automation" 
    automation_secret: "{{ vault_automation_secret }}" 
    csv_file: "groups.csv" 
  tasks:
    # CSV-Datei einlesen
    - name: Read groups from CSV file
      community.general.read_csv:
        path: "{{ csv_file }}" 
        key: name
      register: groups_data

    # Hostgruppen erstellen
    - name: Create host groups from CSV
      checkmk.general.checkmk_hostgroup:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "{{ item.name }}" 
        title: "{{ item.title }}" 
        state: present
      loop: "{{ groups_data.list | selectattr('type', 'equalto', 'hostgroup') | list }}" 

    # Servicegruppen erstellen
    - name: Create service groups from CSV
      checkmk.general.checkmk_servicegroup:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "{{ item.name }}" 
        title: "{{ item.title }}" 
        state: present
      loop: "{{ groups_data.list | selectattr('type', 'equalto', 'servicegroup') | list }}" 

    # Hosts einer Hostgruppe zuweisen (z. B. web_servers für Linux-Hosts)
    - name: Add hosts to a host group
      checkmk.general.checkmk_host:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "{{ item }}" 
        attributes:
          groups:
            host:
              - "web_servers" 
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}" 
```

#### Explicación
- **Lectura de CSV**: El módulo `community.general.read_csv` lee el archivo `groups.csv` y almacena los datos en `groups_data`. La opción `key: name` asegúrese de que cada línea después del `name`-Feld indiziert wird.
- **Crear grupos anfitriones**: La tarea filtra entradas con `type: hostgroup` y crea grupos anfitriones con el especificado `name` y `title` valores.
- **Crear grupos de servicio**: La tarea filtra entradas con `type: servicegroup` y crea grupos de servicio.
- **Anfitrión**: Anfitriones con el día `os: linux` convertirse en el grupo anfitrión `web_servers` asignado. Ajuste el nombre del grupo (`web_servers`) o la consulta (`{'host_tags': {'os': 'linux'}}`) a tus necesidades.
- **Bóveda**: El `automation_secret` se guarda de forma segura en una variable de bóveda.

### 2. Ajuste las variables
Ajuste las variables en el libro de jugadas a su entorno:
- **servidor_url**: Reemplace con la URL de su servidor CHECKMK (p. Ej.`https://monitoring.example.com`).
- **sitio**: Reemplace con el nombre de su sitio Checkmk.
- **Automatización_user**: Use el nombre de usuario para la API de automatización (p. Ej.`automation`).
- **Automatización_secret**: Use la variable de bóveda (p. Ej.`{{ vault_automation_secret }}`).
- **csv_file**: Asegúrese de que la ruta al archivo CSV sea correcta (p. Ej.`groups.csv` en el mismo directorio que el libro de jugadas).
- **consulta**: Ajuste la consulta en el complemento de búsqueda para filtrar los hosts deseados (p.`{"host_labels": {"env": "prod"}}`).

#### Crear el archivo de bóveda
```bash
ansible-vault create vault.yml
```

Contenido del `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

### 3. Proporcionar archivo CSV
Crea el archivo `groups.csv` en el mismo directorio que el libro de jugadas o se ajusta a la ruta en la variable `csv_file` a. Contenido de ejemplo:
```csv
type,name,title
hostgroup,web_servers,Web Servers
hostgroup,db_servers,Database Servers
servicegroup,http_services,HTTP Services
servicegroup,database_services,Database Services
```

### 4. Run Playbook
Realice el libro de jugadas para crear los grupos y asignar hosts:

```bash
ansible-playbook create_groups_from_csv.yml --vault-id vault.yml
```

### 5. Tareas del libro de jugadas
El libro de jugadas lleva tres tareas principales:
1. **Dirigir el archivo CSV**:
   - Liest die `groups.csv` archivo y almacena los datos en `groups_data`.
2. **Creación de grupos anfitriones**:
   - Erstellt Hostgruppen (z. B. `web_servers`,`db_servers`) basado en las entradas CSV con `type: hostgroup`.
3. **Creación de grupos de servicio**:
   - Erstellt Servicegruppen (z. B. `http_services`,`database_services`) basado en las entradas CSV con `type: servicegroup`.
4. **Asignación dinámica de hosts a un grupo de host**:
   -Anfitriones con el día `os: linux` el grupo anfitrión `web_servers` también (adaptable).

### 6. Active los cambios
Después de ejecutar el libro de jugadas, los cambios en CheckMK deben activarse, ya que la asignación de hosts a un grupo de host cambia la configuración:
1. Regístrese en el área web de checkmk.
2. Ir a **Configurar> Activar cambios** Y activar los cambios pendientes.
3. Alternativamente, active los cambios a través de la API CHECKMK:
```intento
CURL -X POST "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/activation_run/actions/activate-changes/invoke"\
     -H "Authorization: Bearer automation dein_geheimes_passwort"\
     -H "Accept: application/json" 
```

### 7. Überprüfen der Ergebnisse
Nach der Ausführung des Playbooks:
1. Melde dich in der Checkmk-Weboberfläche an und navigiere zu:
   - **Setup > Hosts > Host groups**, um die erstellten Hostgruppen (z. B. `Web_Servers`, `DB_SERVERS`) zu überprüfen.
   - **Setup > Services > Service groups**, um die erstellten Servicegruppen (z. B. `http_services`, `database_services`) para verificar.
2. Verifique la asignación del host:
   -Ir a **Monitor> todos los hosts**, elija un host de la lista (por ejemplo, con el día `os: linux`) y verificar debajo **Propiedades> Grupos de host** si `web_servers` se asigna.
3. Alternativamente, consulte los grupos a través de la API CHECKMK:
```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_group_config/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json" 
   ```

### 8. Tratamiento de errores
- **Archivo CSV no encontrado**: Asegúrate de que `groups.csv` existió y el camino en `csv_file` correcto.
- **Formato CSV no válido**: Verifique si el archivo CSV las columnas requeridas (`type`,`name`,`title`) contiene y formateado correctamente.
- **Grupo anfitrión/grupo de servicio ya existe**: Si ya existe un grupo, el módulo ignora la creación (comportamiento ideMpotente). Configuración `state: absent`, para eliminar los grupos existentes.
- **Anfitriones no encontrados**: Si la consulta en el complemento de búsqueda no devuelve hosts (por ejemplo, porque no hay host el día `os: linux` ha), la tarea omitió la tarea. Revise la consulta (`query`) y las etiquetas de host en checkmk.
- **Datos de acceso no válidos**: Asegúrate de que `automation_user` y `automation_secret` son correctos.
- **Problemas de red**: Verifique la accesibilidad del servidor checkmk (`server_url`) y el puerto compartido correcto (http/https).
- **Certificados TLS**: En https, asegúrese de que el certificado sea válido o establecido `validate_certs: false` en el libro de jugadas (solo para entornos de prueba).
- **Versión checkmk**: Asegúrese de que la colección sea compatible con su versión de checkmk (ver `SUPPORT.md` en el repositorio).

### 9. Ajustes y extensiones
- **Atributos CSV extendidos**: Agregue más columnas al archivo CSV (p. Ej.`description` O atributos definidos por el usuario) si las futuras versiones de checkmk los admiten.
- **Consultas dinámicas**: Ajuste la consulta en el complemento de búsqueda para usar otros criterios (p.`{"host_labels": {"env": "prod"}}` o `{"folder": "/production"}`).
- **Asignación del grupo de servicio**: Para asignar servicios de un grupo de servicio, puede `checkmk.general.checkmk_service` use (no incluido en el libro de jugadas de demostración, pero disponible en la colección).
- **Eliminando grupos**: Colocar `state: absent` en las tareas para eliminar los grupos de host o servicios existentes.
- **automatización**: Planifique el libro de jugadas con un programador (por ejemplo, Ansible Tower/Awx o Cron) para actualizar los grupos regularmente.
- **Estructura de CSV extendida**: Puede expandir el archivo CSV para definir también las reglas de asignación (por ejemplo, una columna `host_tags` para la asignación dinámica de hosts).

## Referencias
- **Seguridad**: Siempre use un archivo de bóveda para eso `automation_secret` para proteger los datos confidenciales.
- **Versión checkmk**: Asegúrate de que `checkmk.general` la colección es compatible con su versión checkmk (ver `SUPPORT.md` en el repositorio).
- - **documentación**: Se pueden encontrar más detalles sobre módulos y complementos de búsqueda en el [Documentación de Github](https://github.com/Checkmk/ansible-collection-checkmk.general) O en Ansible Galaxy.
- **Entorno de prueba**: Pruebe el libro de jugadas en un entorno no productivo para evitar efectos inesperados.
- **Formato CSV**: Asegúrese de que el archivo CSV esté formateado correctamente (por ejemplo, no faltan columnas ni caracteres no válidos).
- **Cambiar la activación**: Después de asignar hosts a un grupo de host, los cambios en Checkmk deben activarse, ya sea manualmente o mediante la API.

## Conclusión
El libro de jugadas adaptado `create_groups_from_csv.yml` le permite crear grupos de host y servicios en Checkmk según un archivo CSV y asignar hosts a un grupo de host dinámicamente. Con el `checkmk.general` colección y el `community.general.read_csv` el módulo puede automatizar la administración del grupo de manera flexible y escalable, lo que es particularmente útil para la gestión de los objetos de monitoreo en entornos grandes. Al adaptar el archivo CSV y las consultas, puede adaptar el libro de jugadas a sus requisitos específicos.