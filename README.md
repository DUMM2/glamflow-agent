
# Agente Piloto
Este es el trabajo de un agente para administracion de citas mediante whatsapp. Las funciones principales son agendar, reagendar, cancelar citas.

Tambien como piloto mantiene la persistencia de los datos.

## Configuraciones necesarias

Para ejecutar el proyecto es necesario tener un archivo de ambiente "".env"", similar a este:
```sh
TWILIO_ACCOUNT_SID=twilio-token
TWILIO_AUTH_TOKEN=twilio-secret
OPENAI_API_KEY=openai-apikey

AWS_ACCESS_KEY_ID=fackeAccesKeyID
AWS_SECRET_ACCESS_KEY=fackeSecretAccesKey
AWS_REGION=mx-central-1

LLM_MODEL=gpt-4o-mini
USER_TABLE=gf-user-dev
APPOINTMENT_TABLE=gf-appointment-dev
SESSION_TABLE=gf-session-dev
BUSINESS_TABLE=gf-business-dev

#DEV
URL_DYNAMODB_LOCAL=http://localhost:8000
AWS_ACCESS_KEY_ID=fackeAccesKeyID
AWS_SECRET_ACCESS_KEY=fackeSecretAccesKey
```
### Dependencias
Instala estas dependencias para desarrollo:
* Ngrok
* Docker
* AWS NoSQL-Workbench

### Ejecutar Agente (Whatsapp)
Para ejecutar la integracion con WhatsApp debe tenerce los token de Twilio. Debes tener una cuenta configurada para usar el webhook.

Dentro de la carpeta fuente "src":
```sh
cd src
```
aejecuta la API localmente:
```sh
uvicorn whatsapp:app --host 0.0.0.0 --port 80 --reload
```
Para exponer el servicio e ntegrarlo a twilio, crea un puente con ngrok a twilio:
```sh
ngrok http --url=infinite-seriously-racer.ngrok-free.app 80
```


### Ejecuta el Agente sin WhatsApp
ESto solo ejecuta el angente de manera local, con proposito de hacer desarrollo:
```sh
python main.py
```


## Setup DynamoDB locally
To setup DynamoDB locally, you need **Docker** and **aws cli** installed on your machine.

Descarga la imagen docker:
```sh
docker pull amazon/dynamodb-local
```

Configura un perfil local de AWS:
```sh
aws configure --profile local
```

Inicia la instancia de dynamodb
```sh
docker run -p 8000:8000 amazon/dynamodb-local -jar DynamoDBLocal.jar -sharedDb
```

Crea las tablas en la base dynamodb
```sh
chmod +x setup_dynamodb_local.sh
```