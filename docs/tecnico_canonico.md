
> 🔒 DOCUMENTO CANÓNICO
>
> Este archivo constituye la ÚNICA fuente de verdad técnica del subsistema
> JARVIS Commercial Bot.  
> Cualquier otro documento es derivado, explicativo o comercial.


Documentación Técnica Canónica - JARVIS Commercial Bot
Arquitectura del Sistema
JARVIS Commercial Bot sigue los principios arquitectónicos del ecosistema JARVIS, implementando una separación clara de dominios cognitivos y respetando la inmutabilidad del CORE.

Estructura de Módulos
jarvis_commercial_bot/
├── app/ # Aplicación principal
│ ├── gateway/ # Capa de entrada y seguridad
│ ├── session/ # Gestión de estado de sesión
│ ├── rules/ # Motor de reglas y guardrails
│ ├── llm/ # Adaptador para modelos de lenguaje
│ ├── context/ # Gestión de catálogo y datos
│ ├── handoff/ # Sistema de escalamiento
│ ├── responses/ # Generación de respuestas
│ ├── observability/ # Logs y métricas
│ └── utils/ # Utilidades generales
├── scripts/ # Scripts de mantenimiento
├── data/ # Datos persistentes
├── tests/ # Suite de tests
└── docs/ # Documentación



### Dominios Cognitivos

El sistema respeta la separación de dominios definida en el manual JARVIS v1.2:

- **CORE**: No se modifica ni se extiende. El bot opera como un AGENT externo.
- **AGENTS**: El bot comercial es un agente especializado con capacidades de conversación.
- **TOOLS**: Utilidades puras sin estado cognitivo (generadores de ID, utilidades de tiempo).
- **INTERFACES**: Endpoints de API para comunicación con sistemas externos.
- **RADIO**: No se utiliza en este subsistema para mantener la estabilidad.

## Flujo de Procesamiento

### Recepción de Mensajes

1. **Gateway**: Recibe el webhook y valida la firma de seguridad.
2. **Session Manager**: Recupera o crea una sesión para el usuario.
3. **Rules Engine**: Verifica el mensaje contra reglas y guardrails.
4. **LLM Adapter**: Procesa el mensaje con el modelo de lenguaje configurado.
5. **Response Generator**: Formatea la respuesta final.
6. **Session Manager**: Actualiza la sesión con el nuevo intercambio.

### Escalamiento a Humano

1. **Handoff Manager**: Evalúa si se requiere escalamiento basado en reglas.
2. **Notifier**: Envía notificación al operador correspondiente.
3. **Session Manager**: Actualiza el estado de la sesión a "escalado".

## Configuración

### Variables de Entorno

El sistema utiliza las siguientes variables de entorno configurables:

```bash
# Configuración del servidor
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Configuración de base de datos
DATABASE_URL=sqlite:///./data/bot.db

# Configuración de LLM
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your_mistral_api_key
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

# Configuración de Tienda Nube
TIENDANUBE_API_KEY=your_tiendanube_api_key
TIENDANUBE_STORE_ID=your_store_id
TIENDANUBE_WEBHOOK_SECRET=your_webhook_secret

# Configuración de notificaciones
NOTIFICATION_PROVIDER=email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_email_password
Reglas y Guardrails
El motor de reglas se configura mediante patrones y umbrales definidos en app/rules/patterns.py:

Patrones prohibidos (contenido sensible, discriminación, etc.)
Umbrales de longitud de mensaje
Detección de spam y comportamiento anómalo
Validación de inyección de prompts
Despliegue
Requisitos
Python 3.11+
SQLite (para desarrollo) o PostgreSQL (para producción)
Acceso a APIs externas (LLM, Tienda Nube)
Instalación
Clonar el repositorio:
bash

git clone https://github.com/jarvis/commercial-bot.git
cd commercial-bot
Crear entorno virtual:
bash

python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
Instalar dependencias:
bash

pip install -r requirements.txt
Configurar variables de entorno:
bash

cp .env.example .env
# Editar .env con las configuraciones específicas
Inicializar base de datos:
bash

python -m app.context.store
Sincronizar catálogo:
bash

python scripts/sync_catalog.py
Iniciar aplicación:
bash

uvicorn app.main:app --host 0.0.0.0 --port 8000
Docker
Para despliegue con Docker:

bash

# Construir imagen
docker build -t jarvis-commercial-bot .

# Ejecutar contenedor
docker run -d \
  --name jarvis-bot \
  -p 8000:8000 \
  --env-file .env \
  jarvis-commercial-bot
Monitoreo y Observabilidad
Logs
El sistema implementa logging estructurado en JSON con los siguientes niveles:

INFO: Operaciones normales
WARNING: Eventos inesperados pero no críticos
ERROR: Errores que requieren atención
DEBUG: Información detallada para depuración
Métricas
Se registran las siguientes métricas clave:

Webhooks recibidos: Por fuente y tipo de evento
Mensajes procesados: Tiempo de respuesta y tasa de éxito
Solicitudes LLM: Por proveedor, tiempo de respuesta y tasa de error
Escalamientos: Por razón y frecuencia
Operaciones de base de datos: Por tipo y rendimiento
Testing
Suite de Tests
El sistema incluye una suite completa de tests unitarios:

test_rules.py: Tests para el motor de reglas
test_sessions.py: Tests para el gestor de sesiones
test_gateway.py: Tests para el gateway de webhooks
Ejecución de Tests
bash

# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app

# Ejecutar tests específicos
pytest tests/test_rules.py
Mantenimiento
Tareas Periódicas
Sincronización de Catálogo: Actualización diaria del catálogo de productos
Limpieza de Sesiones: Eliminación de sesiones inactivas
Optimización de Base de Datos: Reindexación y limpieza
Actualización de Modelos: Incorporación de mejoras en los modelos LLM
Actualizaciones
El sistema sigue un ciclo de versionado semántico:

Mayor: Cambios arquitectónicos importantes
Menor: Nuevas funcionalidades compatibles
Parche: Correcciones de errores y mejoras menores
Seguridad
Validación de Webhooks
Todos los webhooks entrantes se validan mediante HMAC-SHA256:

python

def verify_webhook_signature(signature, payload, secret):
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
Control de Acceso
El sistema implementa control de acceso basado en tokens:

Tokens de API para comunicación entre sistemas
Tokens de sesión para mantener contexto de usuario
Tokens de webhook para validar eventos externos
Privacidad de Datos
No se almacenan datos personales sensibles
Las sesiones tienen un tiempo de vida limitado
Los datos se cifran en tránsito y en reposo
Troubleshooting
Problemas Comunes
Error de conexión con LLM:
Verificar API keys
Comprobar cuotas y límites
Revisar configuración de red
Sincronización de catálogo fallida:
Verificar credenciales de Tienda Nube
Comprobar límites de la API
Revisar logs de errores
Respuestas lentas:
Monitorear tiempo de respuesta del LLM
Verificar rendimiento de la base de datos
Revisar cuellos de botella en el código
Depuración
Para habilitar modo de depuración:

bash

export DEBUG=true
export LOG_LEVEL=DEBUG
O mediante variables de entorno en el archivo .env.

Extensión
El sistema está diseñado para ser extensible siguiendo los principios del manual JARVIS:

Nuevos proveedores LLM: Implementar la clase LLMProvider
Canales de notificación: Extender la clase Notifier
Reglas personalizadas: Agregar patrones al motor de reglas
Fuentes de datos: Implementar nuevos loaders en context/
Cualquier extensión debe respetar la separación de dominios y no modificar el CORE de JARVIS.



## requirements.txt
```txt
# Framework web
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Base de datos
aiosqlite==0.19.0
sqlalchemy==2.0.23

# Validación y serialización
pydantic==2.5.0
pydantic-settings==2.1.0

# Cliente HTTP
httpx==0.25.2

# Logging estructurado
structlog==23.2.0

# Utilidades
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Desarrollo y testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1

# Documentación
mkdocs==1.5.3
mkdocs-material==9.4.8
Dockerfile
dockerfile

# Etapa de construcción
FROM python:3.11-slim as builder

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Etapa de ejecución
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Crear usuario no root
RUN useradd --create-home --shell /bin/bash app

# Copiar dependencias de la etapa de construcción
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p data logs && \
    chown -R app:app /app

# Cambiar al usuario no root
USER app

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


## Contrato de Aprendizaje

Este subsistema **NO posee aprendizaje autónomo**.

- No ajusta pesos
- No modifica reglas
- No altera comportamiento por experiencia

Toda interacción se registra **únicamente con fines de observabilidad
y futura ingesta controlada**.



## Observabilidad (Principio Transversal)

La observabilidad **no es un módulo**, es una propiedad sistémica.

Todos los dominios del subsistema deben:
- Emitir logs estructurados
- Registrar métricas
- Permitir trazabilidad de decisiones



## Riesgos Conocidos Postergados

Los siguientes riesgos han sido identificados y conscientemente postergados:

- Protección contra replay attacks
- Rate limiting avanzado
- Circuit breaker distribuido

Su mitigación está planificada para Fase D+.



## Estado de Madurez por Módulo

| Módulo        | Estado        |
|--------------|---------------|
| Gateway      | Estable       |
| Session      | Estable       |
| Rules        | Heurístico    |
| LLM Adapter  | Dependiente externo |
| Observability| Parcial       |
