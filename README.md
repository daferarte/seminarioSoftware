# 🚀 Sistema de Gestión de Eventos - FastAPI + MySQL

Este proyecto es una **API REST** desarrollada en **FastAPI** bajo una arquitectura modular de **cuatro capas**:  
`routers → services → repositories → models`.  
Permite gestionar **participantes, eventos, registros y asistencias**, con autenticación JWT y carga masiva desde Excel.

---

## 📂 Estructura del proyecto

```
app/
├── api/
│   └── v1/
│       ├── routers/
│       │   ├── staff_router.py
│       │   ├── participant_router.py
│       │   ├── event_router.py
│       │   ├── registration_router.py
│       │   └── attendance_router.py
│       └── __init__.py
│
├── core/
│   ├── config.py          # Configuración global
│   ├── database.py        # Conexión a MySQL
│   ├── jwt.py             # Generación y validación JWT
│   ├── dependencies.py    # Dependencias globales (auth)
│   └── security.py        # Hash de contraseñas
│
├── models/                # Modelos SQLAlchemy
├── schemas/               # Esquemas Pydantic
├── repositories/          # Capa de persistencia
├── services/              # Lógica de negocio
└── main.py                # Punto de entrada principal
```

---

## ⚙️ Requisitos previos

### 🧱 1. Instalar dependencias del sistema
Asegúrate de tener instalado:

- Python **3.11+**
- MySQL o MariaDB (en local o contenedor)
- `pip` actualizado:
  ```bash
  python -m pip install --upgrade pip
  ```

---

## 🐍 Instalación del entorno

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/gestion-eventos-fastapi.git
cd gestion-eventos-fastapi
```

### 2️⃣ Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🛢️ Configurar la base de datos MySQL

Crea una base de datos vacía en MySQL (por ejemplo, `seminario`):

```sql
CREATE DATABASE seminario CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Luego, crea un archivo **`.env`** en la raíz del proyecto con tus credenciales:

```env
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=seminario

SECRET_KEY=clave-secreta-123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 🧱 Migraciones con Alembic

Genera y aplica las tablas de tu modelo a la base de datos:

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

Si ya existe la estructura de base de datos, solo ejecuta:
```bash
alembic upgrade head
```

---

## 🧩 Ejecutar la aplicación

Inicia el servidor local con:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

Documentación interactiva:
- Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔐 Autenticación

1. Crea un usuario `Staff` (desde `/staff/`).
2. Inicia sesión en `/auth/login` con usuario y contraseña.
3. Copia el **access token** recibido.
4. Presiona el botón **Authorize** en Swagger y pega:
   ```
   Bearer <tu_token>
   ```

Ahora podrás acceder a los endpoints protegidos como `/events`, `/registrations`, etc.

---

## 📥 Importar participantes desde Excel

El endpoint `/participants/import-excel` permite subir un archivo `.xlsx` con la siguiente estructura:

| document_id | document_type | first_name | last_name | email | phone_number | career | idnumber |
|--------------|---------------|-------------|------------|--------|---------------|----------|
| 1080048252 | CC | Juliana | Peñafiel | juliana.penafiel@campusucc.edu.co | 3117448684 | Ingeniería de software | 922874 |

Carga el archivo en Swagger y el sistema insertará los registros automáticamente, omitiendo duplicados.

---

## 🧰 Comandos útiles

| Comando | Descripción |
|----------|--------------|
| `alembic revision --autogenerate -m "msg"` | Crea nueva migración |
| `alembic upgrade head` | Aplica migraciones |
| `uvicorn app.main:app --reload` | Ejecuta el servidor |
| `pip install -r requirements.txt` | Instala dependencias |
| `black . && isort .` | Formatea el código |

---

## 🧪 Pruebas rápidas (curl)

Registrar participante:
```bash
curl -X POST "http://127.0.0.1:8000/participants/"  -H "Content-Type: application/json"  -d '{"document_id":"12345","document_type":"CC","first_name":"Daniel","last_name":"Arteaga","email":"daniel@ucc.edu.co","phone_number":"3001234567","career":"Ingeniería de Software","idnumber":"54321"}'
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT** — libre para uso académico y comercial.  
Desarrollado por **Daniel Fernando Arteaga Fajardo**, Universidad Cooperativa de Colombia – Sede Pasto.

---

## 💡 Créditos

- **FastAPI** — Framework moderno para APIs con Python  
- **SQLAlchemy + Alembic** — ORM y migraciones automáticas  
- **Pandas + OpenPyXL** — Procesamiento de archivos Excel  
- **JWT (python-jose)** — Autenticación segura  
- **Passlib** — Hash seguro de contraseñas  
