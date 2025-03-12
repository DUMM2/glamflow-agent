import os
import boto3
from datetime import datetime, timedelta
from langchain.tools import tool

from dotenv import load_dotenv
load_dotenv()

class ToolDynamoDB:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', 
                                       region_name=os.getenv("AWS_REGION"),
                                       )


    def put_item(self, table_name:str, item:dict):
        table = self.dynamodb.Table(table_name)
        response = table.put_item(Item=item)
        return response
    

    def get_appointment_items(self, table_name:str, id_phone:int):
        table = self.dynamodb.Table(table_name)
        response = table.query(
            KeyConditionExpression="id_phone = :id_phone", 
            FilterExpression="appoinment_status <> :appoinment_status",
            ExpressionAttributeValues={
                ":id_phone": id_phone, 
                ":appoinment_status": "canceled"
                }
        )
        return response.get("Items", [])
    

    def check_appointment_overlap(self, table_name: str, id_phone: str, new_date_time: str, service_duration: int):
        table = self.dynamodb.Table(table_name)

        # Obtener fecha y hora separadas
        new_date, new_time = new_date_time.split("_")
        new_datetime_obj = datetime.strptime(new_date_time, "%Y-%m-%d_%H:%M")

        # Hora de finalización de la nueva cita
        new_end_time = new_datetime_obj + timedelta(minutes=service_duration)

        # 🔹 Buscar citas existentes del mismo usuario y negocio en la misma fecha
        response = table.query(
            KeyConditionExpression="id_phone = :id_phone AND begins_with(date_time, :new_date)",
            ExpressionAttributeValues={
                ":id_phone": id_phone,
                ":new_date": new_date
            }
        )

        # Recorrer citas existentes y verificar traslapes
        for item in response.get("Items", []):
            existing_datetime_obj = datetime.strptime(item["date_time"], "%Y-%m-%d_%H:%M")
            existing_end_time = existing_datetime_obj + timedelta(minutes=item["service_duration"])

            # 🔥 Verificar si los horarios se traslapan
            if not (new_end_time <= existing_datetime_obj or new_datetime_obj >= existing_end_time):
                return True # ❌ Hay traslape

        return False  # ✅ No hay traslape

    

    def update_item(self, table_name:str, key:str, item:dict):
        table = self.dynamodb.Table(table_name)
        response = table.update_item(Key=key, UpdateExpression="set date = :d, time = :t", ExpressionAttributeValues={":d": item["date"], ":t": item["time"]})
        return response
    

dynamo = ToolDynamoDB()
USER_TABLE = os.getenv("USER_TABLE")
APPOINTMENT_TABLE = os.getenv("APPOINTMENT_TABLE")

@tool
def register_user(user_phone:int, name:str, last_name:str, birth_date:str, postal_code:str) -> dict:
 

    try:
        birth_date = datetime.strptime(birth_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        phone = int(user_phone)
        
        item = {
            "id_phone": phone,
            "name": name,
            "last_name": last_name,
            "birth_date": birth_date,
            "postal_code": postal_code
        }
        
        response = dynamo.put_item(USER_TABLE, item)

        return {"output": "Usuario registrado correctamente en DynamoDB."}
    
    except Exception as e:
        pass
        return {"output": f"Error al registrar usuario: {str(e)}"}
    

@tool
def make_appointment(phone:int, bussines_id:int, service:str, service_duration:int, date:str, time:str) -> dict:
    """
    Registra una cita en la base de datos de DynamoDB.
    Args:
        phone (int): Teléfono del usuario.
        bussines_id (int): Telefono del negocio.
        service (str): Servicio solicitado.
        date (str): Fecha de la cita (dd-mm-yyyy).
        time (str): Hora de la cita (hh:mm).
    Returns:
        dict: Respuesta de cita.
    """


    try:
        date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
        time = datetime.strptime(time, "%H:%M").strftime("%H:%M")
        phone = int(phone)
        bussines_id = int(bussines_id)
        appointment_overlap = dynamo.check_appointment_overlap(APPOINTMENT_TABLE, phone, date + "_" + time, service_duration)
        
        if appointment_overlap:
            return {"output": "Lo siento, ya tienes una cita agendada para ese horario."}
        
        item = {
            "id_phone": phone,
            "id_bussines": bussines_id,
            "service": service,
            "date_time": date.strftime("%Y-%m-%d") + "_" + time.strftime("%H:%M"),
            "service_duration": service_duration,
            "appointment_status": "scheduled",
            "rescheduled_count": 0
        }
        
        response = dynamo.put_item(APPOINTMENT_TABLE, item)
        return {"output": "Cita agendada correctamente en DynamoDB."}
    
    except Exception as e:
        pass
        return {"output": f"Error al agendar cita: {str(e)}"}

@tool
def reschedule_appointment(phone: str, new_date: str = None, new_time: str = None, confirm: str = "no") -> dict:
    """
    Permite reagendar una cita existente para un usuario.

    Args:
        phone (str): Número de teléfono del usuario para identificar su cita.
        new_date (str): Nueva fecha de la cita en formato YYYY-MM-DD. Opcional.
        new_time (str): Nueva hora de la cita en formato HH:MM. Opcional.
        confirm (str): "si" para confirmar el cambio, "no" para solicitar confirmación.

    Returns:
        dict: Mensaje con la información de la cita actualizada o solicitud de confirmación.
    """
    
    # Verificar si el usuario tiene una cita
    response = dynamo.get_item(APPOINTMENT_TABLE, {"id_phone": phone})
    if "Item" not in response:
        return {"output": "No tienes citas registradas. Quieres agendar una cita?"}

    cita_actual = response["Item"]
    # Si no se ha proporcionado una nueva fecha/hora, pedimos los datos al usuario
    if not new_date or not new_time:
        return {
            "output": f"Tu cita actual es el {cita_actual['date']} a las {cita_actual['time']} para {cita_actual['service']}."
                      f" ¿Para qué fecha y hora te gustaría reprogramarla?"
        }
    
    # Si no hay confirmación aún, pedimos confirmación al usuario
    if confirm.lower() != "si":
        return {
            "output": f"Vas a cambiar tu cita de {cita_actual['fecha']} a {new_date} a las {new_time}. "
                      f"¿Confirmas el cambio? Responde 'Sí' para confirmar o 'No' para cancelar."
        }
       
    # Si el usuario confirma, actualizamos la cita
    response = dynamo.update_item(APPOINTMENT_TABLE, {"id_phone": phone}, {"date": new_date, "time": new_time, "appoinment_status": "rescheduled"})
    return {"output": f"Tu cita ha sido reagendada para el {new_date} a las {new_time}. ¡Te esperamos!"}

