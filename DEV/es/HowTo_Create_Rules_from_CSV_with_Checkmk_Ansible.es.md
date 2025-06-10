# Cómo crear reglas en checkmk desde un archivo CSV con la colección Ansible

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


Esto cómo describe cómo `rules.yml` del repositorio [Checkmk/ansible-colection-checkmk. General](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/rules.yml) ajuste para crear reglas en checkmk según un archivo CSV. Usa el `checkmk.general` colección ansible a reglas (`checkmk.general.rules`) para varios reglas, así como para el módulo `community.general.read_csv` para leer la información regular de un archivo CSV. Además, las reglas existentes se pueden consultar y guardar dinámicamente.

## Requisitos previos
- **Ansible**: Instalado y configurado (compatible con las colecciones).
- **Colección de checkmk.general**: Instalado a través de `ansible-galaxy collection install checkmk.general`.
- **Comunidad. Colección General**: Instalado a través de `ansible-galaxy collection install community.general`(para el `read_csv`-Modul).
- **Servidor checkmk**: Acceso a una instancia de checkmk con API web activada.
- **Datos de acceso a la API**: Nombre de usuario (`automation_user`) y contraseña/secreto (`automation_secret`) para la API de automatización.
- **Bóveda (recomendado)**: Para el almacenamiento seguro del `automation_secret`.
- **Acceso a la red**: El controlador Ansible debe poder comunicarse con el servidor CheckMK a través de HTTP/HTTPS.
- **Archivo CSV**: Un archivo CSV con la información regular que se lee en el libro de jugadas.

## Preparar el archivo CSV
Cree un archivo CSV (p. Ej.`rules.csv`) que define las reglas. El archivo debe contener las siguientes columnas:
- `ruleset`: Nombre del conjunto de reglas (por ejemplo, B.`notification_parameters`,`host_tags`,`checkgroup_parameters:filesystem`).
- `folder`: Carpeta objetivo para la regla (p. Ej.`/` para raíz o `/my_folder`).
- `conditions`: Formato JSON para condiciones estándar (p. Ej.`{"host_name": ["web.*"]}`).
- `value`: Formato JSON para regulaciones (p. Ej.`{"method": "email", "contact_all": true}`).
- `description`: Descripción de la regla (p. Ej.`Email notifications for web servers`).

 **Ejemplo`rules.csv`**:
```csv
ruleset,folder,conditions,value,description
notification_parameters,/,{"host_name": ["web.*"]},{"method": "email", "contact_all": true},Email notifications for web servers
host_tags,/,{"host_name": ["db.*"]},{"tag_id": "db_role", "tag_value": "primary"},Tag primary for database servers
checkgroup_parameters:filesystem,/my_folder,{"service_labels": {"type": "critical"}},{"levels": [85, 95]},Filesystem thresholds for critical services
```

Guarde el archivo en el mismo directorio que el libro de jugadas o adapte la ruta en el libro de jugadas.

## Pasos

### 1. Cree o adapte el libro de jugadas
Crea un nuevo libro de jugadas (p. Ej.`create_rules_from_csv.yml`) o ajuste el original `rules.yml` para leer las reglas del archivo CSV.

 **Playbook:`create_rules_from_csv.yml`**:
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "https://monitoring.example.com" 
    site: "mysite" 
    automation_user: "automation" 
    automation_secret: "{{ vault_automation_secret }}" 
    csv_file: "rules.csv" 
  tasks:
    # CSV-Datei einlesen
    - name: Read rules from CSV file
      community.general.read_csv:
        path: "{{ csv_file }}" 
        key: description
      register: rules_data

    # Regeln erstellen
    - name: Create rules from CSV
      checkmk.general.rules:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        ruleset: "{{ item.ruleset }}" 
        folder: "{{ item.folder }}" 
        conditions: "{{ item.conditions | from_json }}" 
        value: "{{ item.value | from_json }}" 
        description: "{{ item.description }}" 
        state: present
      loop: "{{ rules_data.list }}" 

    # Bestehende Regeln abrufen und speichern
    - name: Get all notification rules
      ansible.builtin.copy:
        content: "{{ query('checkmk.general.rules', 'notification_parameters', server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) | to_nice_yaml }}" 
        dest: "notification_rules.yml" 
```

#### Explicación
- **Lectura de CSV**: El módulo `community.general.read_csv` lee el archivo `rules.csv` y almacena los datos en `rules_data`. La opción `key: description` indica cada línea después del `description`-Feld.
- **Crear reglas**: La tarea creó reglas para los reglamientos especificados (`ruleset`), con condiciones (`conditions`), Valores (`value`) y descripciones (`description`) del archivo CSV. Los campos `conditions` y `value` se salvan de JSON.
- **Elevar las reglas**: La última tarea sigue siendo similar a la original y almacena todas las reglas del conjunto de regla `notification_parameters` en un archivo yaml (`notification_rules.yml`).
- **Bóveda**: El `automation_secret` se guarda de forma segura en una variable de bóveda.

### 2. Ajuste las variables
Ajuste las variables en el libro de jugadas a su entorno:
- **servidor_url**: Reemplace con la URL de su servidor CHECKMK (p. Ej.`https://monitoring.example.com`).
- **sitio**: Reemplace con el nombre de su sitio Checkmk.
- **Automatización_user**: Use el nombre de usuario para la API de automatización (p. Ej.`automation`).
- **Automatización_secret**: Use la variable de bóveda (p. Ej.`{{ vault_automation_secret }}`).
- **csv_file**: Asegúrese de que la ruta al archivo CSV sea correcta (p. Ej.`rules.csv` en el mismo directorio que el libro de jugadas).

#### Crear el archivo de bóveda
```bash
ansible-vault create vault.yml
```

Contenido del `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

### 3. Proporcionar archivo CSV
Crea el archivo `rules.csv` en el mismo directorio que el libro de jugadas o se ajusta a la ruta en la variable `csv_file` a. Contenido de ejemplo:
```csv
ruleset,folder,conditions,value,description
notification_parameters,/,{"host_name": ["web.*"]},{"method": "email", "contact_all": true},Email notifications for web servers
host_tags,/,{"host_name": ["db.*"]},{"tag_id": "db_role", "tag_value": "primary"},Tag primary for database servers
checkgroup_parameters:filesystem,/my_folder,{"service_labels": {"type": "critical"}},{"levels": [85, 95]},Filesystem thresholds for critical services
```

### 4. Run Playbook
Realice el libro de jugadas para crear las reglas:

```bash
ansible-playbook create_rules_from_csv.yml --vault-id vault.yml
```

### 5. Tareas del libro de jugadas
El libro de jugadas lleva dos tareas principales:
1. **Dirigir el archivo CSV**:
   - Liest die `rules.csv` archivo y almacena los datos en `rules_data`.
2. **Creación de reglas**:
   - Erstellt Regeln für die angegebenen Rulesets (z. B. `notification_parameters`,`host_tags`,`checkgroup_parameters:filesystem`) Basado en las entradas CSV, con las condiciones, valores y descripciones especificadas.
3. **Reglas de llamada**:
   - Ruft alle Regeln für das Ruleset `notification_parameters` fuera y guárdelo en `notification_rules.yml`.

### 6. Active los cambios
Después de ejecutar el libro de jugadas, los cambios en CheckMK deben activarse, ya que agregar reglas cambia la configuración:
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
   - **Setup > General > Rule-based notifications**, um die Benachrichtigungsregel zu überprüfen.
   - **Setup > Hosts > Host tags**, um die Host-Tag-Regel zu überprüfen.
   - **Setup > Services > Service monitoring rules**, um die Service-Parameter-Regel zu überprüfen.
2. Überprüfe die Regeln:
   - Wähle das entsprechende Ruleset aus und prüfe, ob die Regel mit der Beschreibung (z. B. `Notificaciones por correo electrónico para servidor web`) y las condiciones/valores se crearon correctamente.
3. Verifique las reglas almacenadas:
   - Öffne die Datei `notification_rules.yml` para ver las reglas solicitadas.
4. Alternativamente, verifique las reglas a través de la API CHECKMK:
```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/rule/collections/all?ruleset_name=notification_parameters" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json" 
   ```

### 8. Tratamiento de errores
- **Archivo CSV no encontrado**: Asegúrate de que `rules.csv` existió y el camino en `csv_file` correcto.
- **Formato CSV no válido**: Verifique si el archivo CSV las columnas requeridas (`ruleset`,`folder`,`conditions`,`value`,`description`) contiene y formateado correctamente. Datos JSON en `conditions` y `value` debe ser válido.
- **Por lo general ya hay**: Si ya existe una regla con las mismas propiedades, el módulo ignora la creación (comportamiento idempotente). Configuración `state: absent`, para eliminar las reglas existentes.
- - **Conjunto de reglas no válido**: Asegúrate de que `ruleset` en el archivo CSV hay un conjunto de reglas CheckMK válido (p.`notification_parameters`). Consultar el [Documentación de checkmk](https://docs.checkmk.com/latest/en/rest_api.html) para reglamentos válidos.
- **Datos de acceso no válidos**: Asegúrate de que `automation_user` y `automation_secret` son correctos.
- **Problemas de red**: Verifique la accesibilidad del servidor checkmk (`server_url`) y el puerto compartido correcto (http/https).
- **Certificados TLS**: En https, asegúrese de que el certificado sea válido o establecido `validate_certs: false` en el libro de jugadas (solo para entornos de prueba).
- **Versión checkmk**: Asegúrese de que la colección sea compatible con su versión de checkmk (ver `SUPPORT.md` en el repositorio).

### 9. Ajustes y extensiones
- **Atributos CSV extendidos**: Agregue más columnas al archivo CSV (p. Ej.`properties` para propiedades regulares como `disabled`) Si las versiones futuras de cheCkmk las admiten.
- **Condiciones complejas**: Expandir el `conditions`-Spalte, um komplexere Bedingungen wie mehrere Host- oder Service-Muster zu definieren.
- **Eliminación de reglas**: Colocar `state: absent` en la tarea regular de eliminar las reglas existentes.
- **Otros reglas**: Adapte el archivo CSV a las reglas para otros reglas (p. Ej.`active_checks:http`,`inventory_df_rules`) para crear.
- **automatización**: Planifique el libro de jugadas con un programador (por ejemplo, Ansible Tower/Awx o Cron) para actualizar las reglas regularmente.
- **Copia de seguridad de reglas**: Extienda la última tarea para consultar y guardar reglas para otros reglas.

## Referencias
- **Seguridad**: Siempre use un archivo de bóveda para eso `automation_secret` para proteger los datos confidenciales.
- **Versión checkmk**: Asegúrate de que `checkmk.general` la colección es compatible con su versión checkmk (ver `SUPPORT.md` en el repositorio).
- - **documentación**: Se pueden encontrar más detalles sobre módulos y complementos de búsqueda en el [Documentación de Github](https://github.com/Checkmk/ansible-collection-checkmk.general) O en Ansible Galaxy.
- **Entorno de prueba**: Pruebe el libro de jugadas en un entorno no productivo para evitar efectos inesperados.
- **Formato CSV**: Asegúrese de que el archivo CSV esté formateado correctamente (por ejemplo, no faltan columnas o datos JSON no válidos en `conditions` o `value`).
- **Cambiar la activación**: Después de agregar reglas, los cambios deben activarse en Checkmk, ya sea manualmente o mediante la API.

## Conclusión
El libro de jugadas adaptado `create_rules_from_csv.yml` permite que las reglas en checkmk se creen en función de un archivo CSV y consulten dinámicamente las reglas existentes. Con el `checkmk.general` colección y el `community.general.read_csv` puede automatizar la administración de control de manera flexible y escalable, lo cual es particularmente útil para la configuración de notificaciones, etiquetas y parámetros de servicio en entornos grandes. Al adaptar el archivo CSV, puede adaptar el libro de jugadas a sus requisitos específicos.