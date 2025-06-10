# Cómo mostrar todos los atributos de una carpeta en checkmk con Ansible

> Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente.


Esto cómo describe cómo usar el `checkmk.general` colección ansible Los atributos de una carpeta en checkmk consultan y se muestran. La guía usa el complemento de búsqueda `checkmk.general.folder` a los detalles de una carpeta, como B. para mantener críticas o segmentos de red.

## Requisitos previos
- **Ansible**: Instalado y configurado (versión compatible con la colección).
- **Colección de checkmk.general**: Instalado a través de `ansible-galaxy collection install checkmk.general`.
- **Servidor checkmk**: Acceso a un servidor CHECKMK en curso con acceso a la API.
- **Datos de acceso a la API**: Nombre de usuario (`automation_user`) y contraseña/secreto (`automation_secret`) para la API de automatización CheckMK.
- **Carpeta**: La carpeta a solicitar (p. Ej.`/production_servers`) debe existir en checkmk.
- **Bóveda (opcional)**: Para el almacenamiento seguro del `automation_secret`.

## Pasos

### 1. Crea el libro de jugadas Ansible
Cree un archivo YAML (p. Ej.`show_folder_attributes.yml`) para consultar los atributos de una carpeta.

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

 **Explicación de los parámetros**:
- `folder_path`: La ruta de la carpeta en checkmk (p.`/production_servers`).
- `server_url`: La URL del servidor checkmk (p. Ej.`https://monitoring.example.com`).
- `site`: El nombre del sitio checkmk (p. Ej.`mysite`).
- `automation_user`: El nombre de usuario para la API de automatización (p. Ej.`automation`).
- `automation_secret`: La contraseña o el token API (seguro guardado en una variedad de bóveda ansible, p.`vault_automation_secret`).

### 2. Bóveda para datos de acceso seguro (opcional)
Si haces eso `automation_secret` desea guardar de manera segura, crear un archivo de bóveda encriptado:

```bash
ansible-vault create vault.yml
```

Agregue los datos de acceso, p. B.:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

Realice el libro de jugadas con el archivo de bóveda:
```bash
ansible-playbook show_folder_attributes.yml --vault-id vault.yml
```

### 3. Run Playbook
Realice el libro de jugadas para mostrar los atributos de la carpeta:
```bash
ansible-playbook show_folder_attributes.yml
```

### 4. Interpreta la edición
El complemento de búsqueda devuelve un diccionario tipo JSON que contiene los atributos de la carpeta. Los atributos típicos pueden ser:
- `criticality`: Nivel de criticidad de la carpeta (p. Ej.`prod`).
- `network_segment`: Segmento de red (p. Ej.`dmz`).
- Etiquetas definidas por el usuario u otros metadatos, dependiendo de la configuración de checkmk.

Problema de ejemplo:
```json
{
   "title": "production_servers",
   "attributes": {
     "criticality": "prod",
     "network_segment": "dmz" 
  }
}
```

### 5. Tratamiento de errores
- **Las carpetas no existen**: El complemento devuelve un mensaje de error si la carpeta especificada no existe.
- **Datos de acceso no válidos**: Controlar `automation_user` y `automation_secret`.
- **Problemas de red**: Asegúrate de que `server_url` es correcto y el servidor es accesible.

## Alternativa: consulta de API directa
Si desea usar la API directamente (sin Ansible), puede usar la API web de checkmk:
```bash
curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/objects/folder_config/production_servers" \
  -H "Authorization: Bearer automation dein_geheimes_passwort" \
  -H "Accept: application/json" 
```

Esto devuelve los detalles de la carpeta directamente en el formato JSON.

## Referencias
- Los atributos disponibles dependen de la versión checkmk y del conjunto de configuraciones. Consulte el documental de Checkmk para más detalles.
- - Für weitere Informationen zum Lookup-Plugin siehe die Dokumentation der `checkmk.general` colección sobre [Github](https://github.com/Checkmk/ansible-collection-checkmk.general) O Galaxia Ansible.
- Asegúrese de que la prueba de certificado TLS esté configurada correctamente si su servidor usa HTTPS.

## Conclusión
Con el `checkmk.general.folder` el complemento de búsqueda se puede llamar de manera fácil y eficiente todos los atributos de una carpeta en checkmk. Esto es particularmente útil para la automatización de las configuraciones de monitoreo y la documentación de la estructura de la carpeta.