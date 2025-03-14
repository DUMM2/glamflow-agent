import os
import asyncio
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from fastapi import FastAPI, Form, Response, Request, HTTPException
from fastapi.responses import StreamingResponse
from user_status import Status
from agent_appt_management.agent import AgentAppointmentManagement

load_dotenv()

agent = AgentAppointmentManagement()
stat = Status()
app = FastAPI()

# Configura tus credenciales de Twilio
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

validator = RequestValidator(auth_token)
print(validator)

@app.post("/webhook")
async def chat(
    request: Request, From: str = Form(...), To: str=Form(...), Body: str = Form(...) 
):
    validator = RequestValidator(auth_token)
    form_ = await request.form()
    if not validator.validate(
        str(request.url), 
        form_, 
        request.headers.get("X-Twilio-Signature", "")
    ):
        raise HTTPException(status_code=400, detail="Error in Twilio Signature")

    # Status check
    user_id, business_id = int(From.split("+")[1]), int(To.split("+")[1])
    user_input = Body
    print(user_id, business_id)

    session_dict = await stat.session_status(user_id, business_id)
    user_stat_dict = await stat.user_status(user_id, business_id)
    messages_history = session_dict["messages_history"]

    config = {"configurable":{
        "thread_id":user_id,
        "user_id":user_id,
        "user_name":user_stat_dict["user_name"],
        "business_id":business_id,
        "is_register":user_stat_dict["is_register"],
        "session_init_date_time":session_dict["init_date_time"]
        }
    }

    # Agent calls
    agent_response = agent.conversation(user_input, config)
    agent_msg = agent_response["messages"][-1].content

    to_whatsapp = client.messages.create(
        body=agent_msg,
        from_=To,
        to=From
    )

    return Response(content=str(to_whatsapp), media_type="application/xml")




def appointemt_reminder(from_, to, date, time):
    message = client.messages.create(
        from_=from_,
        content_sid='HX1337700caec11268b7fe1dad85912206',
        content_variables=f'{{"1": "{date}", "2": "{time}"}}',
        to=to
    )
    return message.sid