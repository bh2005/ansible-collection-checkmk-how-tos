# Cómo automatizar las configuraciones de monitoreo con la colección checkmk ansible

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


Este cómo describe cinco ejemplos concretos de cómo el `checkmk.general` la colección Ansible se puede utilizar para automatizar las configuraciones de monitoreo en Checkmk. Los ejemplos incluyen crear carpetas, reglas, usuarios, grupos de host y el uso del complemento de búsqueda para los atributos de la carpeta.

## Requisitos previos
- **Ansible**: Instalado y configurado (compatible con la colección).
- **Colección de checkmk.general**: Instalado a través de `ansible-galaxy collection install checkmk.general`.
- **Servidor checkmk**: Acceso a un servidor CHECKMK en curso con acceso a la API.
- **Datos de acceso a la API**: Nombre de usuario (`automation_user`) y contraseña/secreto (`automation_secret`) para la API de automatización CheckMK.
- **Bóveda (recomendado)**: Para el almacenamiento seguro del `automation_secret`.
- **Carpeta/hosts**: Algunos ejemplos requieren que existan ciertas carpetas o hosts.

## Ejemplo 1: Crear una carpeta
Este ejemplo muestra cómo crear una carpeta en checkmk para organizar hosts.

### Libro de jugadas
Cree un archivo YAML (p. Ej.`create_folder.yml`)

```yaml
- name: Erstelle einen Ordner für Produktionsserver
  hosts: localhost
  tasks:
    - name: Ordner erstellen
      checkmk.general.checkmk_folder:
        server_url: "https://monitoring.example.com" 
        site: "mysite" 
        automation_user: "automation" 
        automation_secret: "{{ vault_automation_secret }}" 
        path: "/production_servers" 
        attributes:
          criticality: "prod" 
          network_segment: "dmz" 
        state: present
```

### Realizar
```bash
ansible-playbook create_folder.yml --vault-id vault.yml
```

### Resultado
Una carpeta `/production_servers` estará con los atributos `criticality: prod` y `network_segment: dmz` creado.

## Ejemplo 2: Crear una regla de monitoreo
Este ejemplo define una regla para el monitoreo de memoria de los servidores Linux.

### Libro de jugadas
Cree un archivo YAML (p. Ej.`create_rule.yml`)

```yaml
- name: Setze Speicherüberwachungsregel für Linux-Server
  hosts: localhost
  tasks:
    - name: Regel erstellen
      checkmk.general.checkmk_rule:
        server_url: "https://monitoring.example.com" 
        site: "mysite" 
        automation_user: "automation" 
        automation_secret: "{{ vault_automation_secret }}" 
        ruleset: "memory" 
        folder: "/linux_servers" 
        conditions:
          host_tags:
            os: linux
        properties:
          levels:
            warning: 80
            critical: 90
        state: present
```

### Realizar
```bash
ansible-playbook create_rule.yml --vault-id vault.yml
```

### Resultado
Se crea una regla, las advertencias en el 80 % y las alarmas críticas con una utilización de memoria del 90 % para los servidores Linux en la carpeta `/linux_servers` motivado.

## Ejemplo 3: Gestión de usuarios con asignación de roles
Este ejemplo crea un nuevo usuario con los derechos del administrador.

### Libro de jugadas
Cree un archivo YAML (p. Ej.`create_user.yml`)

```yaml
- name: Erstelle einen neuen Benutzer mit Admin-Rechten
  hosts: localhost
  tasks:
    - name: Benutzer erstellen
      checkmk.general.checkmk_user:
        server_url: "https://monitoring.example.com" 
        site: "mysite" 
        automation_user: "automation" 
        automation_secret: "{{ vault_automation_secret }}" 
        username: "jdoe" 
        fullname: "John Doe" 
        password: "{{ vault_user_password }}" 
        roles:
          - admin
        contactgroups:
          - "all_admins" 
        state: present
```

### Realizar
```bash
ansible-playbook create_user.yml --vault-id vault.yml
```

### Resultado
Un usuario `jdoe` será con los derechos del administrador y el grupo de contacto `all_admins` creado.

## Ejemplo 4: Creación de un grupo de host
Este ejemplo muestra cómo crear un grupo de host para los hosts de grupo.

### Libro de jugadas
Cree un archivo YAML (p. Ej.`create_hostgroup.yml`)

```yaml
- name: Erstelle eine Hostgruppe für Webserver
  hosts: localhost
  tasks:
    - name: Hostgruppe erstellen
      checkmk.general.checkmk_hostgroup:
        server_url: "https://monitoring.example.com" 
        site: "mysite" 
        automation_user: "automation" 
        automation_secret: "{{ vault_automation_secret }}" 
        name: "web_servers" 
        title: "Web Servers" 
        state: present
```

### Realizar
```bash
ansible-playbook create_hostgroup.yml --vault-id vault.yml
```

### Resultado
Un grupo anfitrión `web_servers` se crea que resume los hosts con propiedades similares (por ejemplo, servidor web).

## Ejemplo 5: Consultas de los atributos de la carpeta
Este ejemplo muestra cómo pregunta todos los atributos de una carpeta con el complemento de búsqueda.

### Libro de jugadas
Cree un archivo YAML (p. Ej.`show_folder_attributes.yml`)

```yaml
- name: Zeige alle Attribute eines Ordners an
  hosts: localhost
  tasks:
    - name: Abfrage der Ordnerattribute
      ansible.builtin.debug:
        msg: "{{ lookup('checkmk.general.folder', folder_path, server_url='https://monitoring.example.com', site='mysite', automation_user='automation', automation_secret=automation_secret) }}" 
      vars:
        folder_path: "/production_servers" 
        automation_secret: "{{ vault_automation_secret }}" 
```

### Realizar
```bash
ansible-playbook show_folder_attributes.yml --vault-id vault.yml
```

### Resultado
Los atributos de la carpeta `/production_servers`(p.ej.`criticality`,`network_segment`) se emiten en el formato JSON.

## Bóveda para datos de acceso seguro (opcional)
Para todos los ejemplos, puede usar datos confidenciales como `automation_secret` o `vault_user_password` guarde en un archivo de bóveda ansible:

```bash
ansible-vault create vault.yml
```

Contenido del `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
vault_user_password: benutzer_passwort
```

Realice los libros de jugadas con el archivo de bóveda:
```bash
ansible-playbook <playbook>.yml --vault-id vault.yml
```

## Referencias
- **Solución de problemas**: Asegúrese de que se pueda alcanzar el servidor CheckMK, los datos de acceso son correctos y existen la carpeta/hosts especificados.
- - **documentación**: Se pueden encontrar más detalles sobre módulos y opciones en el [Documentación de Github](https://github.com/Checkmk/ansible-collection-checkmk.general) O en Ansible Galaxy.
- **TLS**: Si su servidor usa HTTPS, verifique la prueba de certificado (agregue `validate_certs: false` además, si no hay un certificado válido, solo para entornos de prueba).
- **Versión checkmk**: Asegúrese de que la versión checkmk utilizada sea compatible con la colección (ver `SUPPORT.md`).

## Conclusión
El `checkmk.general` la colección ofrece herramientas potentes para la automatización de las configuraciones de checkmk. Con estos ejemplos, puede administrar y adaptar carpetas, reglas, usuarios, grupos de host y de manera más eficiente.