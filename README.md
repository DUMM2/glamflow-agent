# Glamflow Agent

Este directorio contiene el código fuente del agente conversacional de Glamflow, especializado en belleza y cuidado personal. El agente está diseñado para interactuar con los usuarios a través de WhatsApp, ofreciendo servicios como registro de usuarios, agendamiento de citas, envío de recordatorios y procesamiento de pagos en línea.

## Estructura del Directorio

- `agent.py`: Implementación principal del agente conversacional utilizando LangChain y OpenAI.
- `prompt.py`: Contiene el prompt utilizado para guiar las respuestas del agente.
- `tools/`: Directorio que contiene herramientas adicionales utilizadas por el agente.
  - `dynamo_tool.py`: Herramientas para interactuar con DynamoDB.

## Archivos

### agent.py

Este archivo contiene la clase `AgentOpenAI` que configura y ejecuta el agente conversacional. Utiliza LangChain para manejar la memoria de la conversación y OpenAI para generar respuestas.

### prompt.py

Contiene el prompt `AGENT_PROMPT` que define las instrucciones y el comportamiento del agente. Este prompt guía al agente para que sea amable, útil y enfocado en los servicios del negocio.

### tools/dynamo_tool.py

Este archivo contiene herramientas para interactuar con DynamoDB, como registrar usuarios y gestionar citas. Utiliza Boto3 para comunicarse con DynamoDB y LangChain para definir las herramientas.

## Instalación

Para instalar las dependencias necesarias, ejecuta:

```sh
conda env create -f environment.yml
```
para activar el entorno, ejecuta:
```sh
conda activate glamflow
```

## Uso
```sh
python agent.py
```

## Configuración
Crea un archivo `.env` en el directorio raíz con las siguientes variables de entorno:

```sh
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=your_aws_region
OPENAI_API_KEY=openai_api_key
LLM_MODEL=gpt-4o-mini
USER_TABLE=gf-user-dev
APPOINTMENT_TABLE=gf-appointment-dev
```
