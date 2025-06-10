# Cómo crear carpetas y hosts en checkmk desde un archivo CSV con la colección Ansible

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


Esto cómo describe cómo `hosts-and-folders.yml` del repositorio [Checkmk/ansible-colection-checkmk. General](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/hosts-and-folders.yml) ajuste para crear carpetas y hosts en checkmk según un archivo CSV. Usa el `checkmk.general` colección ansible a carpeta (`checkmk.general.folder`) y anfitriones (`checkmk.general.checkmk_host`) para crear, así como el módulo `community.general.read_csv` para leer la información de un archivo CSV. Además, los hosts se pueden crear dinámicamente en función de una consulta.

## Requisitos previos
- **Ansible**: Instalado y configurado (compatible con las colecciones).
- **Colección de checkmk.general**: Instalado a través de `ansible-galaxy collection install checkmk.general`.
- **Comunidad. Colección General**: Instalado a través de `ansible-galaxy collection install community.general`(para el `read_csv`-Modul).
- **Servidor checkmk**: Acceso a una instancia de checkmk con API web activada.
- **Datos de acceso a la API**: Nombre de usuario (`automation_user`) y contraseña/secreto (`automation_secret`) para la API de automatización.
- **Bóveda (recomendado)**: Para el almacenamiento seguro del `automation_secret`.
- **Acceso a la red**: El controlador Ansible debe poder comunicarse con el servidor CheckMK a través de HTTP/HTTPS.
- **Archivo CSV**: Un archivo CSV con la carpeta y la información del host que se lee en el libro de jugadas.

## Preparar el archivo CSV
Cree un archivo CSV (p. Ej.`hosts_and_folders.csv`) que define las carpetas y los hosts. El archivo debe contener las siguientes columnas:
- `type`: Tipo de entrada (`folder` o `host`).
- `name`: Nombre de la carpeta (p. Ej.`/my_folder`) o hosts (por ejemplo, B.`myhost1.local`).
- `title`: Anuncios de la carpeta (p. Ej.`My Folder`) o alias del huésped (p. Ej.`My Host 1`).
- `folder`(solo para hosts): ruta de carpeta en la que se crea el host (p.`/my_folder` o `/` para raíz).
- `ipaddress`(Opcional, solo para hosts): dirección IP del host (p.`192.168.1.100`).
- `tag_os`(Opcional, solo para hosts): día de host para el sistema operativo (p.`linux`).
- `labels`(Opcional, solo para hosts): formato JSON para etiquetas (p.`{"env": "prod"}`).

 **Ejemplo`hosts_and_folders.csv`**:
```csv
type,name,title,folder,ipaddress,tag_os,labels
folder,/my_folder,My Folder,,,
folder,/prod_servers,Production Servers,,,
host,myhost1.local,My Host 1,/my_folder,192.168.1.100,linux,{"env": "prod"}
host,myhost2.local,My Host 2,/,192.168.1.101,windows,{"env": "test"}
```

Guarde el archivo en el mismo directorio que el libro de jugadas o adapte la ruta en el libro de jugadas.

## Pasos

### 1. Cree o adapte el libro de jugadas
Crea un nuevo libro de jugadas (p. Ej.`create_hosts_and_folders_from_csv.yml`) o ajuste el original `hosts-and-folders.yml` para leer las carpetas y hosts del archivo CSV.

 **Playbook:`create_hosts_and_folders_from_csv.yml`**:
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "https://monitoring.example.com" 
    site: "mysite" 
    automation_user: "automation" 
    automation_secret: "{{ vault_automation_secret }}" 
    csv_file: "hosts_and_folders.csv" 
  tasks:
    # CSV-Datei einlesen
    - name: Read folders and hosts from CSV file
      community.general.read_csv:
        path: "{{ csv_file }}" 
        key: name
      register: csv_data

    # Ordner erstellen
    - name: Create folders from CSV
      checkmk.general.folder:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        path: "{{ item.name }}" 
        title: "{{ item.title }}" 
        state: present
      loop: "{{ csv_data.list | selectattr('type', 'equalto', 'folder') | list }}" 

    # Hosts erstellen
    - name: Create hosts from CSV
      checkmk.general.checkmk_host:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "{{ item.name }}" 
        folder: "{{ item.folder | default('/') }}" 
        attributes:
          alias: "{{ item.title }}" 
          ipaddress: "{{ item.ipaddress | default(omit) }}" 
          tag_os: "{{ item.tag_os | default(omit) }}" 
          labels: "{{ item.labels | default({}) | from_json }}" 
        state: present
      loop: "{{ csv_data.list | selectattr('type', 'equalto', 'host') | list }}" 

    # Dynamische Hosts erstellen (Beispiel)
    - name: Create dynamic hosts from query
      checkmk.general.checkmk_host:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "ansible-{{ item }}-{{ 1000 | random }}" 
        folder: "/my_folder" 
        attributes:
          tag_os: linux
          labels:
            source: ansible
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}" 
```

#### Explicación
- **Lectura de CSV**: El módulo `community.general.read_csv` lee el archivo `hosts_and_folders.csv` y almacena los datos en `csv_data`. La opción `key: name` indica cada línea después del `name`-Feld.
- **Crear carpeta**: La tarea filtra entradas con `type: folder` y crear carpetas con el especificado `path` y `title` valores.
- **Crear anfitriones**: La tarea filtra entradas con `type: host` y crea hosts con los atributos especificados (`alias`,`ipaddress`,`tag_os`,`labels`). El `folder`-Wert bestimmt den Zielordner, standardmäßig `/`(Raíz).
- **Creación dinámica del huésped**: La última tarea sigue siendo similar al original, pero crea hosts basados ​​en una consulta (p. Ej.`os: linux`) con un sufijo aleatorio en el nombre.
- **Bóveda**: El `automation_secret` se guarda de forma segura en una variable de bóveda.

### 2. Ajuste las variables
Ajuste las variables en el libro de jugadas a su entorno:
- **servidor_url**: Reemplace con la URL de su servidor CHECKMK (p. Ej.`https://monitoring.example.com`).
- **sitio**: Reemplace con el nombre de su sitio Checkmk.
- **Automatización_user**: Use el nombre de usuario para la API de automatización (p. Ej.`automation`).
- **Automatización_secret**: Use la variable de bóveda (p. Ej.`{{ vault_automation_secret }}`).
- **csv_file**: Asegúrese de que la ruta al archivo CSV sea correcta (p. Ej.`hosts_and_folders.csv` en el mismo directorio que el libro de jugadas).
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
Crea el archivo `hosts_and_folders.csv` en el mismo directorio que el libro de jugadas o se ajusta a la ruta en la variable `csv_file` a. Contenido de ejemplo:
```csv
type,name,title,folder,ipaddress,tag_os,labels
folder,/my_folder,My Folder,,,
folder,/prod_servers,Production Servers,,,
host,myhost1.local,My Host 1,/my_folder,192.168.1.100,linux,{"env": "prod"}
host,myhost2.local,My Host 2,/,192.168.1.101,windows,{"env": "test"}
```

### 4. Run Playbook
Realice el libro de jugadas para crear las carpetas y hosts:

```bash
ansible-playbook create_hosts_and_folders_from_csv.yml --vault-id vault.yml
```

### 5. Tareas del libro de jugadas
El libro de jugadas lleva tres tareas principales:
1. **Dirigir el archivo CSV**:
   -Lee el `hosts_and_folders.csv` archivo y almacena los datos en `csv_data`.
2. **Crear carpetas**:
   - Erstellt Ordner (z. B. `/my_folder`,`/prod_servers`) basado en las entradas CSV con `type: folder`.
3. **Creación de anfitriones**:
   - Erstellt Hosts (z. B. `myhost1.local`,`myhost2.local`) basado en las entradas CSV con `type: host`, con los atributos especificados y las asignaciones de carpetas.
4. **Creación dinámica del huésped**:
   - Erstellt Hosts basierend auf einer Abfrage (z. B. `os: linux`) Con un sufijo aleatorio y muestra la carpeta `/my_folder` a.

### 6. Active los cambios
Después de ejecutar el libro de jugadas, los cambios en CheckMK deben activarse, ya que agregar carpetas y hosts cambia la configuración:
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
   - **Setup > Hosts > Folders**, um die erstellten Ordner (z. B. `/My_folder`, `/Prod_Servers`) zu überprüfen.
   - **Monitor > All hosts**, um die erstellten Hosts (z. B. `myhost1.local`, `myhost2.local`) zu überprüfen.
2. Überprüfe die Host-Details:
   - Wähle einen Host aus und prüfe unter **Properties**, ob die Attribute (`alias`, `ipaddress`, `TAG_OS`, `etiqueta`) se configuran correctamente.
   -Revise la carpeta en **Host> Carpeta**.
3. Alternativamente, verifique las carpetas y los hosts sobre el checkmk-API:
```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/folder_config/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json" 
   ```
```intento
curl -x get "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_config/collections/all"\
     -H "Authorization: Bearer automation dein_geheimes_passwort"\
     -H "Accept: application/json" 
```

### 8. Fehlerbehandlung
- **CSV-Datei nicht gefunden**: Stelle sicher, dass `hosts_and_forders.csv` existiert und der Pfad in `csv_file` korrekt ist.
- **Ungültiges CSV-Format**: Überprüfe, ob die CSV-Datei die erforderlichen Spalten (`tipo`, `nombre`, `título`) enthält und korrekt formatiert ist. JSON-Daten in `etiqueta` müssen gültig sein.
- **Ordner/Host existiert bereits**: Wenn ein Ordner oder Host bereits existiert, ignoriert das Modul die Erstellung (idempotentes Verhalten). Setze `Estado: ausente`, para eliminar los objetos existentes.
- **Anfitriones no encontrados**: Si la consulta en el complemento de búsqueda no devuelve hosts (por ejemplo, porque no hay host el día `os: linux` ha), la tarea se saltó la creación. Revise la consulta (`query`) y las etiquetas de host en checkmk.
- **Datos de acceso no válidos**: Asegúrate de que `automation_user` y `automation_secret` son correctos.
- **Problemas de red**: Verifique la accesibilidad del servidor checkmk (`server_url`) y el puerto compartido correcto (http/https).
- **Certificados TLS**: En https, asegúrese de que el certificado sea válido o establecido `validate_certs: false` en el libro de jugadas (solo para entornos de prueba).
- **Versión checkmk**: Asegúrese de que la colección sea compatible con su versión de checkmk (ver `SUPPORT.md` en el repositorio).

### 9. Ajustes y extensiones
- **Atributos CSV extendidos**: Agregue otras columnas al archivo CSV (por ejemplo, etiquetas adicionales o atributos personalizados) si las versiones futuras de CheckMK las admiten.
- **Consultas dinámicas**: Ajuste la consulta en el complemento de búsqueda para usar otros criterios (p.`{"host_labels": {"env": "prod"}}` o `{"folder": "/production"}`).
- **Eliminación del huésped**: Colocar `state: absent` en las tareas de host para eliminar los hosts existentes.
- **Jerarquías de carpetas**: Crea carpetas de nido haciendo caminos como `/parent/child` define en el archivo CSV.
- **automatización**: Planifique el libro de jugadas con un planificador (por ejemplo, Ansible Tower/Awx o Cron) para actualizar la carpeta y los hosts regularmente.
- **Estructura de CSV extendida**: Puede expandir el archivo CSV para definir configuraciones adicionales, como asignaciones de grupo o tiempos de inactividad.

## Referencias
- **Seguridad**: Siempre use un archivo de bóveda para eso `automation_secret` para proteger los datos confidenciales.
- **Versión checkmk**: Asegúrate de que `checkmk.general` la colección es compatible con su versión checkmk (ver `SUPPORT.md` en el repositorio).
- - **documentación**: Se pueden encontrar más detalles sobre módulos y complementos de búsqueda en el [Documentación de Github](https://github.com/Checkmk/ansible-collection-checkmk.general) O en Ansible Galaxy.
- **Entorno de prueba**: Pruebe el libro de jugadas en un entorno no productivo para evitar efectos inesperados.
- **Formato CSV**: Asegúrese de que el archivo CSV esté formateado correctamente (por ejemplo, no faltan columnas o datos JSON no válidos en `labels`).
- **Cambiar la activación**: Después de agregar carpetas y hosts, los cambios deben activarse en Checkmk, ya sea manualmente o mediante la API.

## Conclusión
El libro de jugadas adaptado `create_hosts_and_folders_from_csv.yml` permite que las carpetas y los hosts se creen en Checkmk en función de un archivo CSV y hosts configurados dinámicamente. Con el `checkmk.general` colección y el `community.general.read_csv` el módulo puede automatizar la gestión de las jerarquías de monitoreo de manera flexible y escalable, lo que es particularmente útil para la organización de hosts en entornos grandes. Al adaptar el archivo CSV y las consultas, puede adaptar el libro de jugadas a sus requisitos específicos.