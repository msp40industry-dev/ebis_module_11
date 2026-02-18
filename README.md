# 🤖 Chatbot Python con RAG - POC Academia de Programación

Asistente conversacional especializado en Python que utiliza Retrieval-Augmented Generation (RAG) para responder preguntas sobre programación. El sistema combina recuperación semántica de documentación indexada con generación de respuestas contextualizadas mediante GPT-4o.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Stack Técnico](#stack-técnico)
- [Arquitectura](#arquitectura)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Troubleshooting](#troubleshooting)

## ✨ Características

- **💬 Chat con historial completo**: El modelo mantiene el contexto de toda la conversación
- **🔍 RAG sobre FAQ de Python**: Recupera respuestas relevantes desde una base vectorial antes de generar la respuesta
- **🖼️ Soporte de imágenes**: Adjunta capturas de código PNG para análisis visual
- **🎙️ Voz a texto**: Transcripción local con Vosk (sin enviar audio a la nube)
- **📊 Monitorización con MLflow**: Tracking completo de parámetros, métricas y trazas por ejecución

## 🛠️ Stack Técnico

### Backend
- **FastAPI**: API REST
- **OpenAI GPT-4o**: Generación de respuestas
- **Pinecone Local**: Base de datos vectorial (vía Docker)
- **OpenAI text-embedding-3-small**: Generación de embeddings
- **Vosk**: Speech-to-text en español (modelo `vosk-model-small-es-0.42`)
- **MLflow**: Tracking de experimentos

### Frontend
- **Streamlit**: Interfaz de usuario personalizada

### Infraestructura
- **Docker**: Para ejecutar Pinecone Local
- **Python 3.13**: Entorno de ejecución

## 🏗️ Arquitectura

```
├── backend.py                    # Aplicación FastAPI principal
├── frontend.py                   # Interfaz Streamlit
├── indexing_code.py             # Script para indexar documentos en Pinecone
├── faq_pairs.json               # Documentos FAQ sobre Python
├── routers/
│   ├── chat_with_history.py     # Endpoint de chat con RAG
│   └── transcribe.py            # Endpoint de transcripción de voz
├── features/
│   ├── rag_generation/
│   │   └── rag_generation.py    # Lógica RAG (retrieval + generation)
│   └── monitoring/
│       └── mlflow_setup.py      # Configuración MLflow
└── models/
    └── vosk-model-small-es-0.42/  # Modelo de transcripción de voz
```

## 📦 Requisitos Previos

Asegúrate de tener instalado:

- **Python 3.13+**
- **Docker Desktop** (para Pinecone Local)
- **Una API Key de OpenAI** ([obtener aquí](https://platform.openai.com/api-keys))

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/chatbot-python-rag.git
cd chatbot-python-rag
```

### 2. Crear entorno virtual

```bash
python -m venv poc_venv
source poc_venv/bin/activate  # En Windows: poc_venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Descargar el modelo Vosk

```bash
# macOS/Linux
curl -L -o vosk-model-small-es-0.42.zip https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
unzip vosk-model-small-es-0.42.zip -d models/
rm vosk-model-small-es-0.42.zip

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip" -OutFile "vosk-model-small-es-0.42.zip"
Expand-Archive -Path "vosk-model-small-es-0.42.zip" -DestinationPath "models\"
Remove-Item "vosk-model-small-es-0.42.zip"
```

## ⚙️ Configuración

### 1. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
touch .env
```

Añade tu API Key de OpenAI:

```bash
OPENAI_API_KEY=tu-api-key-aqui
MLFLOW_TRACKING_URI=http://localhost:8080
MLFLOW_EXPERIMENT_NAME=chatbot-fastapi
```

⚠️ **IMPORTANTE**: Reemplaza `tu-api-key-aqui` con tu API Key real de OpenAI.

### 2. Crear archivos `__init__.py`

El proyecto requiere archivos vacíos para que Python reconozca las carpetas como paquetes:

```bash
# macOS/Linux
touch features/__init__.py
touch features/rag_generation/__init__.py
touch features/monitoring/__init__.py
touch routers/__init__.py

# Windows (PowerShell)
New-Item -Path "features\__init__.py" -ItemType File
New-Item -Path "features\rag_generation\__init__.py" -ItemType File
New-Item -Path "features\monitoring\__init__.py" -ItemType File
New-Item -Path "routers\__init__.py" -ItemType File
```

## 🎯 Uso

Sigue estos pasos **en orden** para levantar el sistema completo:

### **Paso 1: Levantar Pinecone Local**

Arranca el contenedor Docker de Pinecone:

```bash
docker run -d \
  --name pinecone-local \
  -p 5080:5080 \
  -p 5081:5081 \
  ghcr.io/pinecone-io/pinecone-local:latest
```

Verifica que esté corriendo:

```bash
curl http://localhost:5080/indexes
# Debería devolver: {"indexes":[]}
```

Si el contenedor ya existe pero está parado:

```bash
docker start pinecone-local
```

### **Paso 2: Indexar documentos en Pinecone**

Ejecuta el script de indexing para cargar los documentos FAQ en la base vectorial:

```bash
python indexing_code.py
```

Deberías ver:

```
Upsert complete
```

### **Paso 3: Levantar MLflow**

En una **nueva terminal** (con el entorno virtual activado):

```bash
mlflow ui --port 8080
```

Accede a MLflow en: http://localhost:8080

### **Paso 4: Levantar el backend**

En otra **nueva terminal** (con el entorno virtual activado):

```bash
uvicorn backend:app --port 8000
```

Espera a ver:

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### **Paso 5: Levantar el frontend**

En otra **nueva terminal** (con el entorno virtual activado):

```bash
streamlit run frontend.py
```

El navegador debería abrirse automáticamente en: http://localhost:8501

## 🎮 Probando el Sistema

Una vez que todo esté corriendo:

1. **Chat con texto**: Escribe "¿Qué es Python?" en el input del chat
2. **Chat con imagen**: Adjunta una captura de pantalla de código PNG
3. **Chat con voz**: Graba un mensaje de voz usando el botón del micrófono
4. **Monitorización**: Revisa las métricas en MLflow (http://localhost:8080)

## 📂 Estructura del Proyecto

```
.
├── backend.py                    # Aplicación FastAPI
├── frontend.py                   # Interfaz Streamlit
├── indexing_code.py             # Script de indexing
├── faq_pairs.json               # Documentos FAQ
├── .env                         # Variables de entorno (NO subir a Git)
├── requirements.txt             # Dependencias Python
├── recordings/                  # Audios grabados (generado automáticamente)
├── routers/
│   ├── __init__.py
│   ├── chat_with_history.py     # Endpoint /chat_with_history
│   └── transcribe.py            # Endpoint /transcribe
├── features/
│   ├── __init__.py
│   ├── rag_generation/
│   │   ├── __init__.py
│   │   └── rag_generation.py    # Pipeline RAG
│   └── monitoring/
│       ├── __init__.py
│       └── mlflow_setup.py      # Configuración MLflow
└── models/
    └── vosk-model-small-es-0.42/  # Modelo Vosk
```

## 🐛 Troubleshooting

### Error: "Connection refused" en puerto 5080

**Causa**: Pinecone Local no está corriendo.

**Solución**:

```bash
docker start pinecone-local
curl http://localhost:5080/indexes  # Verificar
```

### Error: "Connection refused" en puerto 8080

**Causa**: MLflow no está corriendo.

**Solución**:

```bash
mlflow ui --port 8080
```

### Error: "Failed to create a model" (Vosk)

**Causa**: El modelo Vosk no está descargado o está en la ubicación incorrecta.

**Solución**:

```bash
ls models/vosk-model-small-es-0.42/  # Verificar que existe
# Si no existe, descárgalo siguiendo el paso 4 de Instalación
```

### Error: "API request to OpenAI failed"

**Causa**: API Key no configurada o inválida.

**Solución**:

1. Verifica que el archivo `.env` existe y contiene tu API Key
2. Asegúrate de que el API Key es válida en https://platform.openai.com/api-keys
3. Reinicia el backend después de modificar el `.env`

### El backend tarda mucho en arrancar

**Normal**: Vosk tarda 30-60 segundos en cargar el modelo la primera vez. Espera a ver `Application startup complete.`

### Pinecone está vacío después de reiniciar Docker

**Causa**: Pinecone Local pierde datos al reiniciar el contenedor.

**Solución**:

```bash
python indexing_code.py  # Re-indexar
```

Para persistir datos entre reinicios, usa un volumen Docker:

```bash
docker run -d \
  --name pinecone-local \
  -p 5080:5080 \
  -p 5081:5081 \
  -v pinecone-data:/data \
  ghcr.io/pinecone-io/pinecone-local:latest
```

## 🔒 Seguridad

⚠️ **NO subas tu archivo `.env` a Git**. Añade `.env` a tu `.gitignore`:

```bash
echo ".env" >> .gitignore
```

⚠️ **NO hardcodees tu API Key** en el código. Usa siempre variables de entorno.

## 📝 Notas de Desarrollo

- El proyecto usa Pinecone Local para desarrollo sin necesidad de cuenta cloud
- Vosk transcribe localmente, sin enviar audio a servicios externos
- MLflow corre en modo servidor local (no requiere configuración adicional)
- El frontend se recarga automáticamente al guardar cambios

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Miguel Sánchez Pinto**

- LinkedIn: [tu-perfil](https://www.linkedin.com/in/miguel-sánchez-pinto-03771922a)
- GitHub: [@tu-usuario](https://github.com/msp40industry-dev)

## 🙏 Agradecimientos

- [OpenAI](https://openai.com/) por GPT-4o y embeddings
- [Pinecone](https://www.pinecone.io/) por la base de datos vectorial
- [Vosk](https://alphacephei.com/vosk/) por el modelo de speech-to-text
- [Streamlit](https://streamlit.io/) por el framework de UI
- [MLflow](https://mlflow.org/) por el tracking de experimentos

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub
