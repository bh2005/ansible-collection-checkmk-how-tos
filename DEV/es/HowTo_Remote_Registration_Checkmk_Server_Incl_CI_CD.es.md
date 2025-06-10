# Cómo: Uso del registro remoto. Playbooks para checkmk

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


Este documento describe cómo hacer el libro de jugadas Ansible `remote-registration.yml` de la colección checkmk ansible (`checkmk.general`) Use para registrar un servidor de checkmk remoto en un entorno de vigilancia distribuido. El libro de jugadas automatiza el registro de un servidor remoto con un servidor Central CheckMK. Los pasos incluyen la preparación, configuración y ejecución del libro de jugadas.

## Requisitos previos
Antes de usar el libro de jugadas, asegúrese de que se cumplan los siguientes requisitos:
- **Ansible**: Ansible (Versión compatible con la colección, ver soporte.md) debe instalarse.
- **Colección de checkmk.general**: Instalado a través de `ansible-galaxy collection install checkmk.general`.
- **Servidor checkmk**: Un servidor Central CheckMK y un servidor remoto tienen que ejecutarse. Ambos deben ser accesibles.
- **Datos de acceso**: Necesita los datos de acceso para el `automation_user` y `automation_secret` tanto para el servidor central como el remoto.
- **Conectividad de red**: Los servidores deben poder comunicarse entre sí a través de las URL especificadas.
- **Bibliotecas de pitón**: El `netaddr`-Bibliothek ist für einige Rollen erforderlich:
```bash
  pip install netaddr
  ```

## Descripción general del libro de jugadas
El libro de jugadas `remote-registration.yml`(Disponible en: https://github.com/checkmk/ansible-collection-checkmk.general/blob/playbooks/usecases/remote-registration.yml) realiza las siguientes tareas:
1. Registre un servidor checkmk remoto con un servidor Central CheckMK.
2. Configura la conexión para la vigilancia distribuida.
3. Activa los cambios en el servidor central.

Aquí hay un ejemplo del libro de jugadas (basado en la estructura del repositorio):

```yaml
- name: Register a remote site
  hosts: localhost
  tasks:
    - name: Register remote site
      checkmk.general.site:
        server_url: "{{ central_server_url }}" 
        site: "{{ central_site }}" 
        automation_user: "{{ central_automation_user }}" 
        automation_secret: "{{ central_automation_secret }}" 
        remote_url: "{{ remote_server_url }}" 
        remote_site: "{{ remote_site }}" 
        remote_automation_user: "{{ remote_automation_user }}" 
        remote_automation_secret: "{{ remote_automation_secret }}" 
        state: present
```

## Instrucciones paso a paso

### Paso 1: Preparación del inventario
Crear un archivo de inventario (`inventory/hosts.ini`) para definir los hosts objetivo. Porque el libro de jugadas en `localhost` una configuración simple es suficiente:

```ini
[localhost]
localhost ansible_connection=local
```

Guarde este archivo en un directorio como `inventory/hosts.ini`.

### Paso 2: Defina las variables
Crear un archivo variable (`group_vars/all.yml`) para definir los parámetros requeridos. Un ejemplo:

```yaml
central_server_url: "http://central-server.example.com/" 
central_site: "central" 
central_automation_user: "automation" 
central_automation_secret: "your-central-secret" 
remote_server_url: "http://remote-server.example.com/" 
remote_site: "remote" 
remote_automation_user: "automation" 
remote_automation_secret: "your-remote-secret" 
```

Reemplace los valores con las URL reales y acceda a los datos de su servidor CheckMK.

### Paso 3: clon o copia del libro de jugadas
Clonar el repositorio de la colección o copiar esto de checkmk `remote-registration.yml`-Playbook in Ihr Projektverzeichnis:

```bash
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
```

Alternativamente, puede copiar el libro de jugadas directamente desde el repositorio: https://github.com/checkmk/ansible-collection-checkmk.general/blob/main/playbooks/usecases/remote-registration.yml

Guarde el libro de jugadas z. B. como `remote-registration.yml` en tu proyecto.

### Paso 4: Instalación de dependencias
Instale la colección checkmk ansible y las bibliotecas de Python requeridas:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Paso 5: Ejecutando el libro de jugadas
Realice el libro de jugadas con el siguiente comando:

```bash
ansible-playbook -i inventory/hosts.ini remote-registration.yml
```

Asegúrese de que el archivo variable (`group_vars/all.yml`) se encuentra en el mismo directorio o en una ruta reconocida por Ansible.

### Paso 6: Verifique el registro
1. Regístrese en el servidor Central Checkmk.
2. Navegar también **Configuración> Monitoreo distribuido** Y verifique si el servidor remoto se ha registrado correctamente.
3. Verifique que la conexión esté activa y los datos están sincronizados.

## Solución de problemas
- **Error de red**: Asegúrate de que `central_server_url` y `remote_server_url` son correctos y se pueden alcanzar los servidores.
- **Error de autenticación**: Verifique los datos de acceso (`automation_user` y `automation_secret`) para ambos servidores.
- **Error de módulo**: Consulte la documentación del `checkmk.general.site`-Module: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/site.py
- **Registro**: Activar el registro detallado `-v` o `-vvv` en la versión del libro de jugadas para identificar errores:
```bash
  ansible-playbook -i inventory/hosts.ini remote-registration.yml -vvv
  ```

## Mejores prácticas
- **Almacenamiento seguro de secretos**: Guardar datos confidenciales como `automation_secret` en archivos variables cifrados (por ejemplo, con `ansible-vault`).
- **Ídem**: El libro de jugadas es ideMpotent, es decir, es decir, las explicaciones repetidas no conducen a cambios inesperados.
- **Versiones**: Verifique la compatibilidad de las versiones checkmk y la colección Ansible en el soporte.
- **documentación**: Mantenga sus variables y configuraciones bien documentadas para facilitar los cambios posteriores.

## Integración en CI/CD
Para integrar el libro de jugadas en una tubería CI/CD (por ejemplo, con acciones de GitHub), cree un archivo de flujo de trabajo:

```yaml
name: Register Remote Checkmk Site

on:
  push:
    branches:
      - main

jobs:
  register-site:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          pip install ansible netaddr
          ansible-galaxy collection install checkmk.general
      - name: Run Ansible Playbook
        env:
          ANSIBLE_CENTRAL_AUTOMATION_USER: ${{ secrets.CENTRAL_AUTOMATION_USER }}
          ANSIBLE_CENTRAL_AUTOMATION_SECRET: ${{ secrets.CENTRAL_AUTOMATION_SECRET }}
          ANSIBLE_REMOTE_AUTOMATION_USER: ${{ secrets.REMOTE_AUTOMATION_USER }}
          ANSIBLE_REMOTE_AUTOMATION_SECRET: ${{ secrets.REMOTE_AUTOMATION_SECRET }}
        run: |
          ansible-playbook -i inventory/hosts.ini remote-registration.yml
```

Guarde secretos en la configuración del repositorio de su herramienta CI/CD.

## Conclusión
El `remote-registration.yml`-Playbook automatisiert die Registrierung eines Remote-Checkmk-Servers in einer verteilten Überwachungsumgebung. Mit den oben beschriebenen Schritten können Sie es lokal oder in einer CI/CD-Pipeline ausführen. Für weitere Details zu den Modulen und Optionen konsultieren Sie die offizielle Dokumentation: https://github.com/Checkmk/ansible-collection-checkmk.general.