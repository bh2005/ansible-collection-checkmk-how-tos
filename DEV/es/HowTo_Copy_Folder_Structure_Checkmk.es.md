# Cómo copiar la estructura de la carpeta de una instancia de cheque

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


Este cómo describe cómo copiar la estructura de la carpeta de una instancia checkmk (instancia1) en otra instancia checkmk (instancia2) por `checkmk.general` colección ansible utilizada. Será el complemento de búsqueda `checkmk.general.folder` se utiliza para acceder a las carpetas y sus atributos de la instancia1, y el módulo `checkmk.general.checkmk_folder` para crear estas carpetas en instancia2.

## Requisitos previos
- **Ansible**: Instalado y configurado (compatible con la colección).
- **Colección de checkmk.general**: Instalado a través de `ansible-galaxy collection install checkmk.general`.
- **Instancias de checkmk**: Acceso a ambas instancias de checkmk (instancia 1 e instancia2) con acceso a la API.
- **Datos de acceso a la API**: Nombre de usuario (`automation_user`) y contraseña/secreto (`automation_secret`) para la API de automatización de ambas instancias.
- **Bóveda (recomendado)**: Para el almacenamiento seguro de los datos de acceso (`automation_secret`).
- **Acceso a la red**: Ambos servidores checkmk deben ser accesibles.

## Pasos

### 1. Llamar a la estructura de la carpeta de la instancia1
Cree un libro de jugadas para consultar la estructura de la carpeta de la instancia 1. Este libro de jugadas usa el complemento de búsqueda `checkmk.general.folder`, para recolectar los atributos de todas las carpetas.

#### Playbook:`get_folder_structure.yml` 
```yaml
- name: Abrufen der Ordnerstruktur von Instanz1
  hosts: localhost
  tasks:
    - name: Sammle alle Ordner von Instanz1
      ansible.builtin.set_fact:
        folders: "{{ folders | default([]) + [lookup('checkmk.general.folder', item, server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret)] }}" 
      loop: "{{ instance1_folders }}" 
      vars:
        instance1_url: "https://monitoring1.example.com" 
        instance1_site: "mysite1" 
        instance1_user: "automation" 
        instance1_secret: "{{ vault_instance1_secret }}" 
        instance1_folders:
          - "/" 
          - "/production_servers" 
          - "/test_servers" 
          - "/development" 

    - name: Zeige gesammelte Ordner an
      ansible.builtin.debug:
        msg: "{{ folders }}" 
```

#### Explicación
- **Bucle**: La lista `instance1_folders` contiene las rutas de las carpetas que se deben llamar (por ejemplo, carpeta raíz `/` y subcarpetas como `/production_servers`).
- **Complemento de búsqueda**:`checkmk.general.folder` llame a los atributos de cada carpeta (p.`criticality`,`network_segment`) lejos.
- **set_fact**: Los resultados están en la variable `folders` guardado.
- **Bóveda**: El `automation_secret` por ejemplo1, una bóveda variables (`vault_instance1_secret`) guardado.

#### Realizar
```bash
ansible-playbook get_folder_structure.yml --vault-id vault.yml
```

#### Resultado
La variable `folders` contiene una lista de diccionarios con los atributos de todas las carpetas llamadas, p. B.:
```json
[
  {"path": "/", "attributes": {"criticality": "prod"}},
  {"path": "/production_servers", "attributes": {"criticality": "prod", "network_segment": "dmz"}},
  ...
]
```

### 2. Cree estructura de carpeta en instancia2
Cree un segundo libro de jugadas para replicar la estructura de la carpeta en el instante2. El módulo `checkmk.general.checkmk_folder` se usa para crear las carpetas con los mismos atributos.

#### Playbook:`create_folder_structure.yml` 
```yaml
- name: Erstellen der Ordnerstruktur in Instanz2
  hosts: localhost
  tasks:
    - name: Erstelle Ordner in Instanz2
      checkmk.general.checkmk_folder:
        server_url: "{{ instance2_url }}" 
        site: "{{ instance2_site }}" 
        automation_user: "{{ instance2_user }}" 
        automation_secret: "{{ vault_instance2_secret }}" 
        path: "{{ item.path }}" 
        attributes: "{{ item.attributes }}" 
        state: present
      loop: "{{ folders }}" 
  vars:
    instance2_url: "https://monitoring2.example.com" 
    instance2_site: "mysite2" 
    instance2_user: "automation" 
    instance2_secret: "{{ vault_instance2_secret }}" 
    folders: "{{ hostvars['localhost']['folders'] | default([]) }}" 
```

#### Explicación
- **Bucle**: Iterado a través de la lista `folders` eso proviene del primer libro de jugadas.
- **Checkmk_folder**: Crea cada carpeta con la ruta (`path`) y los atributos (`attributes`) de instancia1.
- **Bóveda**: El `automation_secret` por ejemplo2, una variable de bóveda (`vault_instance2_secret`) guardado.
- **carpeta**: La variable `folders` debe estar disponible en el primer libro de jugadas (por ejemplo, guardando un archivo o entrega entre los libros de jugadas).

#### Realizar
```bash
ansible-playbook create_folder_structure.yml --vault-id vault.yml
```

#### Resultado
La estructura de la carpeta de la instancia 1 (p. Ej.`/`,`/production_servers`,`/test_servers`,`/development`) se crea en instancia2 con los mismos atributos.

### 3. Bóveda para datos de acceso seguro
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
ansible-playbook get_folder_structure.yml --vault-id vault.yml
ansible-playbook create_folder_structure.yml --vault-id vault.yml
```

### 4. Combine los libros de jugadas (opcionales)
Para simplificar el proceso, puede combinar ambos pasos en un libro de jugadas:

#### Libro de jugadas combinado:`copy_folder_structure.yml` 
```yaml
- name: Kopieren der Ordnerstruktur von Instanz1 nach Instanz2
  hosts: localhost
  tasks:
    - name: Abrufen der Ordnerstruktur von Instanz1
      ansible.builtin.set_fact:
        folders: "{{ folders | default([]) + [lookup('checkmk.general.folder', item, server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret)] }}" 
      loop: "{{ instance1_folders }}" 
      vars:
        instance1_url: "https://monitoring1.example.com" 
        instance1_site: "mysite1" 
        instance1_user: "automation" 
        instance1_secret: "{{ vault_instance1_secret }}" 
        instance1_folders:
          - "/" 
          - "/production_servers" 
          - "/test_servers" 
          - "/development" 

    - name: Erstellen der Ordner in Instanz2
      checkmk.general.checkmk_folder:
        server_url: "{{ instance2_url }}" 
        site: "{{ instance2_site }}" 
        automation_user: "{{ instance2_user }}" 
        automation_secret: "{{ vault_instance2_secret }}" 
        path: "{{ item.path }}" 
        attributes: "{{ item.attributes }}" 
        state: present
      loop: "{{ folders }}" 
  vars:
    instance2_url: "https://monitoring2.example.com" 
    instance2_site: "mysite2" 
    instance2_user: "automation" 
    instance2_secret: "{{ vault_instance2_secret }}" 
```

#### Realizar
```bash
ansible-playbook copy_folder_structure.yml --vault-id vault.yml
```

### 5. Tratamiento de errores
- **Las carpetas no existen**: El complemento de búsqueda proporciona un mensaje de error si una carpeta no existe en el instante1. Revise la lista `instance1_folders`.
- **Datos de acceso no válidos**: Asegúrate de que `automation_user` y `automation_secret` son correctos para ambas instancias.
- **Problemas de red**: Verifique si ambos servidores están disponibles y el `server_url` correcto.
- **Certificados TLS**: Si se usa https, asegúrese de que los certificados sean válidos o establecidos `validate_certs: false`(solo para entornos de prueba).

## Referencias
- **Lista de carpetas**: La lista `instance1_folders` debe contener las rutas de todas las carpetas que se deben copiar. Puede expandir dinámicamente la lista pidiéndole a la API CheckMK directamente que busque todas las carpetas.
- **Atributos**: No todos los atributos (por ejemplo, etiquetas personalizadas) están disponibles en cada versión de checkmk. Consulte la documentación de la API de su versión CheckMK.
- - **documentación**: Se pueden encontrar más detalles sobre módulos y complementos en el [Documentación de Github](https://github.com/Checkmk/ansible-collection-checkmk.general) O en Ansible Galaxy.
- **Escalada**: El libro de jugadas se puede ajustar para estructuras de carpetas grandes para consultar subcarpetas recursivamente (requiere consultas de API adicionales).

## Conclusión
Con el `checkmk.general` colección Ansible Puede copiar de manera eficiente la estructura de la carpeta de una instancia de checkmk a otra. Esto muestra cómo puede replicar las carpetas y sus atributos con un esfuerzo mínimo, lo que es particularmente útil para la sincronización de entornos de monitoreo.