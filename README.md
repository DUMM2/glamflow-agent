
## DEV
The proyect has configured for run with DynamoDB locally, because boto3 was pointed to local. 
Change this for prod environment.

## Run proyect

For run any part of aplication you need to set "".env"" file as folows:
```sh
TWILIO_ACCOUNT_SID=twilio-token
TWILIO_AUTH_TOKEN=twilio-secret
OPENAI_API_KEY=openai-apikey

AWS_ACCESS_KEY_ID=fackeAccesKeyID
AWS_SECRET_ACCESS_KEY=fackeSecretAccesKey
AWS_REGION=mx-central-1

LLM_MODEL = gpt-4o-mini
USER_TABLE = gf-user-dev
APPOINTMENT_TABLE=gf-appointment-dev
SESSION_TABLE=gf-session-dev
BUSINESS_TABLE=gf-business-dev
```
### Dependences
Install and setup ngrok:

### Full aplication
For run all aplication you need twilio tokens defined in .env.
Afther  go to agen dir that run:
```sh
cd agent
```
and run service(API) locally:
```sh
uvicorn whatsapp:app --host 0.0.0.0 --port 80 --reload
```
To expose that to web use ngrok(just for dev or test). No use in a production:
```sh
ngrok http --url=infinite-seriously-racer.ngrok-free.app 80
```

Configure twilio endpoint or webhook to point ngrok url.

### Run Agent locally
This only ejecute the Agent on local [for dev].
for this inside agent directory ejecute this in terminal:
```sh
python main.py
```


## Setup DynamoDB locally
To setup DynamoDB locally, you need **Docker** and **aws cli** installed on your machine.


## Ejecute

Open a terminal in root directory. Alow ejecution acces for script with:
```sh
chmod +x setup_dynamodb_local.sh
```

Execute script
```sh
./setup_dynamodb.sh
```