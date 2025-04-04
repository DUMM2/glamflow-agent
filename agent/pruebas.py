import os
import boto3
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key, Attr
from agent_appt_management.utils import DynamoDB

load_dotenv()


user_id = "5566776677"
business_id = "5599889966"
dynamodb = DynamoDB()
USER_TABLE = os.getenv("USER_TABLE")
SESSION_TABLE = os.getenv("SESSION_TABLE")
APPOINTMENT_TABLE = os.getenv("APPOINTMENT_TABLE")


def get_user_appointments(user_id):
    dynamodb = boto3.resource("dynamodb", endpoint_url='http://localhost:8000', region_name=os.getenv("AWS_REGION"))
    table = dynamodb.Table(APPOINTMENT_TABLE)  # Nombre de la tabla

    try:
        response = table.query(
            KeyConditionExpression="user_id = :user_id",
            FilterExpression="appointment_status = :status",
            ExpressionAttributeValues={":user_id": int(user_id), ":status": "active"}
        )

        return response.get("Items", [])  # Devuelve la lista de citas del usuario

    except Exception as e:
        return {"error": f"Error al consultar citas: {str(e)}"}


def agendar_cita(user_id, business_id, date_appointment):
    dynamodb = boto3.resource("dynamodb", endpoint_url='http://localhost:8000', region_name=os.getenv("AWS_REGION"))
    table = dynamodb.Table(APPOINTMENT_TABLE)  # Nombre de la tabla
    date_format = "%Y-%m-%d %H:%M:%S"
    date_appointment = datetime.strptime(date_appointment, date_format)
    date_appointment_end = date_appointment + timedelta(hours=1)
    

    try:
        print("1")
        response = table.query(
            KeyConditionExpression=Key('user_id').eq(user_id),
            FilterExpression=Attr('date_appointment').lt(date_appointment_end.strftime(date_format)) &
            Attr('date_appointment_end').gt(date_appointment.strftime(date_format))
        )
        print("2")

        existing_appointments = response.get('Items', [])

        print("3")

        print("Verificar si hay solapamientos")
        if existing_appointments:
            return {"error": "Ya existe una cita agendada en el horario propuesto."}

        table.put_item(
            Item={
                "user_id": int(user_id),
                "business_id": int(business_id),
                "date_appointment": str(date_appointment),
                "date_appointment_end": str(date_appointment_end),
                "appointment_status": "active"
            }
        )
    
        return {"message": "Cita agendada exitosamente."}
    
    except Exception as e:
        return {"error": f"Error al agendar cita: {str(e)}"}



def get_business_appointments(business_id):
    dynamodb = boto3.resource("dynamodb", endpoint_url='http://localhost:8000', region_name=os.getenv("AWS_REGION"))
    table = dynamodb.Table(APPOINTMENT_TABLE)  # Nombre de la tabla
    print(business_id)
    try:
        resp = table.query(
            # Add the name of the index you want to use in your query.
            IndexName="BusinessIndex",
            KeyConditionExpression=Key('business_id').eq(int(business_id)),
            )
        
        print(resp)
        return resp.get("Items", [])  # Devuelve la lista de citas del usuario

    except Exception as e:
        return {"error": f"Error al consultar citas: {str(e)}"}




#appointments = get_user_appointments(user_id)
#appointments = get_business_appointments(business_id)
#appointment_dates = [(appt["date_appointment"]) for appt in appointments if "date_appointment" in appt]
#
#print(json.dumps(appointment_dates, indent=4))

#agendar_cita(user_id, business_id,"2025-04-14 10:30:00")

appointments = get_business_appointments(business_id)

appointment_dates = [
    {"date": appt["date_appointment"], "business_id": int(appt["business_id"])} 
    for appt in appointments 
    if "date_appointment" in appt and "business_id" in appt
]

print(json.dumps(appointment_dates, indent=4))  # `indent=4` para mejor legibilidad