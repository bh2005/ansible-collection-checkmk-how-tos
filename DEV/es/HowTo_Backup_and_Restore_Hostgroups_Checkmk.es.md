# Cómo asegurar los grupos de host de checkmk en un repositorio de git y copiar en una nueva instancia

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


Este cómo describe cómo los grupos de host de una instancia de checkmk (instancia 1) con el `checkmk.general` asegure la colección ANSIL en un repositorio de Git y luego se copie a una nueva instancia de checkmk (instancia2). Utiliza el complemento de búsqueda `checkmk.general.hostgroups`, Para acceder a los datos del grupo de host, guárdelo en un archivo YAML y use el módulo `checkmk.general.checkmk_hostgroup`, para crear los grupos de host en la nueva instancia. Los datos se usan con el módulo `ansible.builtin.git` asegurado en un repositorio de git.

## Requisitos previos
- **Ansible**: Instalado y configurado (compatible con la colección).
- **Colección de checkmk.general**: Instalado a través de `ansible-galaxy collection install checkmk.general`.
- **Instancias de checkmk**: Acceso a ambas instancias de checkmk (instancia1 para copia de seguridad, instancia2 para recuperación) con acceso a la API.
- **Datos de acceso a la API**: Nombre de usuario (`automation_user`) y contraseña/secreto (`automation_secret`) para la API de automatización de ambas instancias.
- **Git**: Instalado en el controlador Ansible y un repositorio Git configurado (local o remoto, por ejemplo, en GitHub, GitLab).
- **Bóveda (recomendado)**: Para el almacenamiento seguro de los datos de acceso (`automation_secret`).
- - **Dependencias**: Módulo de pitón `netaddr` en el controlador (requerido para algunos módulos checkmk, ver [Ansible-colection-checkmk.general/roles/agent/readme.md](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/roles/agent/README.md)).
- - **Llave ssh**: Para acceder a un repositorio de git remoto (opcional, ver [Documental ansible para conoce_hosts](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/known_hosts_module.html)).

## Pasos

### 1. Prepare el repositorio de Git
Configure un repositorio Git en el que se guarde la configuración del grupo host.

#### Local
Crear un repositorio local:
```bash
mkdir checkmk-hostgroups-backup
cd checkmk-hostgroups-backup
git init
```

#### Remoto (opcional)
Si usa un repositorio remoto (por ejemplo, en GitHub), clona o agréguelo:
```bash
git clone git@github.com:dein-benutzer/checkmk-hostgroups-backup.git
```
Asegúrese de que la clave SSH del controlador Ansible esté registrada en el repositorio. Alternativamente, puede usar HTTPS con nombre de usuario/contraseña o token de acceso personal.

### 2. Grupos de host seguros de la instancia1
Cree un libro de jugadas para llamar a todos los grupos de host de la instancia1 y guárdelo en un archivo YAML, que luego se lleva al repositorio de git.

#### Playbook:`backup_hostgroups.yml` 
```yaml
- name: Backup Checkmk-Hostgruppen in Git
  hosts: localhost
  tasks:
    # Hostgruppen abrufen
    - name: Abrufen aller Hostgruppen aus Instanz1
      ansible.builtin.set_fact:
        hostgroups: "{{ lookup('checkmk.general.hostgroups', server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret) }}" 
      vars:
        instance1_url: "https://monitoring1.example.com" 
        instance1_site: "mysite1" 
        instance1_user: "automation" 
        instance1_secret: "{{ vault_instance1_secret }}" 

    # Hostgruppen in Datei speichern
    - name: Speichere Hostgruppen in Datei
      ansible.builtin.copy:
        content: "{{ hostgroups | to_nice_yaml }}" 
        dest: "{{ backup_dir }}/hostgroups.yml" 
      vars:
        backup_dir: "./checkmk-hostgroups-backup" 

    # Git-Operationen
    - name: Git-Status prüfen
      ansible.builtin.git:
        repo: "{{ git_repo }}" 
        dest: "{{ backup_dir }}" 
        accept_hostkey: true
        version: main
      register: git_status
      vars:
        git_repo: "git@github.com:dein-benutzer/checkmk-hostgroups-backup.git" 
        backup_dir: "./checkmk-hostgroups-backup" 

    - name: Änderungen committen
      ansible.builtin.command:
        cmd: git commit -m "Backup der Checkmk-Hostgruppen vom {{ ansible_date_time.iso8601 }}" 
        chdir: "{{ backup_dir }}" 
      when: git_status.changed
      vars:
        backup_dir: "./checkmk-hostgroups-backup" 

    - name: Änderungen pushen
      ansible.builtin.command:
        cmd: git push origin main
        chdir: "{{ backup_dir }}" 
      when: git_status.changed
      vars:
        backup_dir: "./checkmk-hostgroups-backup" 
```

#### Explicación
- **Complemento de búsqueda**:`checkmk.general.hostgroups` llame a todos los grupos de host de la instancia 1, incluidos sus atributos (p.`name`,`title`).
- **Ahorrar**: Los grupos de host están en un archivo YAML (`hostgroups.yml`) en el directorio `checkmk-hostgroups-backup` guardado.
- **Operaciones Git**: El módulo `ansible.builtin.git` sincroniza el repositorio y el `ansible.builtin.command`-Tasks führen `git commit` y `git push` de cuando hay cambios.
- **Bóveda**: El `automation_secret` por ejemplo1, una bóveda variables (`vault_instance1_secret`) guardado.
- **Edición de muestra**: El archivo `hostgroups.yml` podría verse así:
```yaml
  - name: web_servers
    title: Web Servers
  - name: db_servers
    title: Database Servers
  ```

#### Realizar
```bash
ansible-playbook backup_hostgroups.yml --vault-id vault.yml
```

#### Resultado
Los grupos anfitriones están en `hostgroups.yml` almacenado y colocado en el repositorio de Git y empujado.

### 3. Restaurar grupos anfitriones en instancia2
Cree un libro de jugadas para importar los grupos de host seguros desde el archivo YAML en instancia 2.

#### Playbook:`restore_hostgroups.yml` 
```yaml
- name: Hostgruppen aus Git in Instanz2 wiederherstellen
  hosts: localhost
  tasks:
    # Repository klonen oder aktualisieren
    - name: Git-Repository klonen oder aktualisieren
      ansible.builtin.git:
        repo: "{{ git_repo }}" 
        dest: "{{ backup_dir }}" 
        accept_hostkey: true
        version: main
      vars:
        git_repo: "git@github.com:dein-benutzer/checkmk-hostgroups-backup.git" 
        backup_dir: "./checkmk-hostgroups-backup" 

    # Hostgruppen aus Datei laden
    - name: Lade Hostgruppen aus YAML-Datei
      ansible.builtin.set_fact:
        hostgroups: "{{ lookup('file', backup_dir + '/hostgroups.yml') | from_yaml }}" 
      vars:
        backup_dir: "./checkmk-hostgroups-backup" 

    # Hostgruppen in Instanz2 erstellen
    - name: Erstelle Hostgruppen in Instanz2
      checkmk.general.checkmk_hostgroup:
        server_url: "{{ instance2_url }}" 
        site: "{{ instance2_site }}" 
        automation_user: "{{ instance2_user }}" 
        automation_secret: "{{ vault_instance2_secret }}" 
        name: "{{ item.name }}" 
        title: "{{ item.title }}" 
        state: present
      loop: "{{ hostgroups }}" 
      vars:
        instance2_url: "https://monitoring2.example.com" 
        instance2_site: "mysite2" 
        instance2_user: "automation" 
        instance2_secret: "{{ vault_instance2_secret }}" 
```

#### Explicación
- **Repositorio de git**: El módulo `ansible.builtin.git` clon o actualiza el repositorio para `hostgroups.yml`-Datei verfügbar zu machen.
- **Archivo de carga**: El complemento de búsqueda `file` lee el `hostgroups.yml`-Datei und wandelt sie mit `from_yaml` convertir a una lista de diccionarios de grupos host.
- **Crear grupos anfitriones**: El módulo `checkmk.general.checkmk_hostgroup` crea cada grupo de host en instancia2 con los atributos `name` y `title`.
- **Bóveda**: El `automation_secret` por ejemplo2, una variable de bóveda (`vault_instance2_secret`) guardado.

#### Realizar
```bash
ansible-playbook restore_hostgroups.yml --vault-id vault.yml
```

#### Resultado
Los grupos anfitriones `hostgroups.yml`(p.ej.`web_servers`,`db_servers`) se crean en instancia2.

### 4. Bóveda para datos de acceso seguro
Guarde los datos de acceso de forma segura en un archivo de bóveda para ambas instancias:

```bash
ansible-vault create vault.yml
```

Contenido del `vault.yml`:
```yaml
vault_instance1_secret: dein_geheimes_passwort_instanz1
vault_instance2_secret: dein_geheimes_passwort_instanz2
```

Realice los libros de jugadas con el archivo de bóveda:
```bash
ansible-playbook backup_hostgroups.yml --vault-id vault.yml
ansible-playbook restore_hostgroups.yml --vault-id vault.yml
```

### 5. Tratamiento de errores
- **No hay grupos anfitriones**: Si la instancia1 no tiene ningún grupo de host, es `hostgroups.yml`-Datei leer. Überprüfe die Konfiguration in Instanz1.
- **Datos de acceso no válidos**: Asegúrate de que `automation_user` y `automation_secret` son correctos para ambas instancias.
- **Acceso a git**: Verifique los datos de acceso a la tecla SSH o HTTPS (por ejemplo, el token de acceso personal) para obtener errores Git.
- **Archivo no encontrado**: Asegúrate de que `hostgroups.yml` en el `backup_dir` existe antes de realizar el libro de jugadas Restaur.
- **Certificados TLS**: Si se usa https, verifique los certificados o establezca `validate_certs: false`(solo para entornos de prueba).
- **Versión checkmk**: Asegúrese de que la colección sea compatible con las versiones checkmk de ambas instancias (ver `SUPPORT.md`).

## Referencias
- **automatización**: Planifique los libros de jugadas con un programador (por ejemplo, Ansible Tower/Awx o Cron) para llevar a cabo copias de seguridad regulares.
- **Expansión**: Para asegurar más configuraciones (por ejemplo, carpetas, reglas), puede usar el libro de jugadas con complementos de búsqueda adicionales como `checkmk.general.folder` o `checkmk.general.rules` expandir.
- **Repositorio de git**: Use un repositorio dedicado para copias de seguridad para evitar conflictos. Para archivos grandes (por ejemplo, para copias de seguridad adicionales como `omd backup`) Verifique el uso de git lfs.
- - **documentación**: Se pueden encontrar más detalles sobre módulos y complementos de búsqueda en el [Documentación de Github](https://github.com/Checkmk/ansible-collection-checkmk.general) O en Ansible Galaxy.
- **Atributos del grupo anfitrión**: La colección actualmente es compatible `name` y `title` para grupos de acogida. CheckMK-API Documentation Verifique los atributos personalizados.

## Conclusión
Con el `checkmk.general` puede hacer una copia de seguridad de los grupos de host de una instancia de checkmk y copiarlos a otra instancia. Esto se muestra cómo exporta los grupos de host a un archivo YAML, la versión en un repositorio GIT y restauración en una nueva instancia, que es útil para la migración o sincronización de las configuraciones de monitoreo.