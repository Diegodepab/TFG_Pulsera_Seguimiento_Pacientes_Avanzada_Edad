# Configuración de acceso a Amazon S3 para el proyecto Bracelet

Este documento explica cómo **crear un usuario IAM en AWS**, generar sus claves de acceso (`API_S3_ACCESS_KEY_ID` y `API_S3_SECRET_ACCESS_KEY`) y configurar tu entorno local para trabajar con el bucket S3 del proyecto.

---

## 1. Crear un usuario IAM en AWS

1. Accede a la consola de AWS: [https://console.aws.amazon.com](https://console.aws.amazon.com)
2. Ve a **IAM → Usuarios**.
3. Haz clic en **Agregar usuario**.
4. Escribe un nombre, por ejemplo: `tfm-s3-user`.
5. Selecciona **Acceso programático** (Programmatic access) para generar claves.
6. Asigna **permisos mínimos**:
   - Lo recomendable es crear una política personalizada para permitir acceso solo al bucket que usarás, por ejemplo `bracelet-tests`.
7. Finaliza la creación del usuario.

---

## 2. Generar claves de acceso

1. Dentro del usuario recién creado, ve a **Credenciales de seguridad → Claves de acceso (Access Keys)**.
2. Haz clic en **Crear clave de acceso**.
3. AWS generará:
   - `Access Key ID` → **API_S3_ACCESS_KEY_ID**
   - `Secret Access Key` → **API_S3_SECRET_ACCESS_KEY**
4. ⚠️ **Importante:** el `Secret Access Key` solo se muestra una vez. Guárdalo en un lugar seguro.
5. Descarga el archivo `.csv` para backup.

---

## 3. Configurar la política mínima para S3

Si quieres que el usuario solo tenga acceso a un bucket específico, usa esta política JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::TU_CUENTA:user/tfm-s3-user" },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::bracelet-tests",
        "arn:aws:s3:::bracelet-tests/*"
      ]
    }
  ]
}```
> Reemplaza `TU_CUENTA` por tu número de cuenta AWS.

---

## 4. Configurar variables de entorno en tu proyecto

Crea un archivo `.env` en la raíz de tu proyecto (o usa las variables de entorno del sistema):

```bash
API_S3_ACCESS_KEY_ID=tu_access_key_id
API_S3_SECRET_ACCESS_KEY=tu_secret_access_key
```
5. Configurar CORS en el bucket S3

Para permitir que tu frontend (http://localhost:3000) pueda subir y bajar archivos:

Ve a S3 → bucket bracelet-tests → Permisos → CORS.

usa este JSON:
```
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "HEAD"],
    "AllowedOrigins": ["http://localhost:3000"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]```

6. Probar el acceso a S3

Desde la terminal, puedes probar subir y bajar archivos:

# Subir un archivo
aws s3 cp ./modelo.glb s3://bracelet-tests/modelos3d/modelo.glb

# Descargar un archivo
aws s3 cp s3://bracelet-tests/modelos3d/modelo.glb ./modelo-descargado.glb


Si estos comandos funcionan, tu usuario y credenciales están correctamente configurados.