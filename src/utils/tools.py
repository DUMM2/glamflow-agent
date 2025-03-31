from datetime import datetime, timedelta, time
from langchain_core.tools import tool
from utils.dynamodb import DynamoDB
from langchain_core.runnables.config import RunnableConfig

dynamodb = DynamoDB()
OPEN = time(10, 0)
CLOSE = time(18, 0)
    
@tool
def register_user(name:str, birth_date:str, postal_code:str, config:RunnableConfig):
    """
    Registra un usuario en la base de datos.
    Args:
        name (str): Nombre del usuario.
        birth_date (str): Fecha de nacimiento del usuario (dd-mm-yyyy).
        postal_code (str): Código postal del usuario.
    """
    user_state = config.get("configurable", {})
    
    birth_date = datetime.strptime(birth_date, "%d-%m-%Y").strftime("%d-%m-%Y")
    phone = user_state.get("user_id", 0)
    item = {
            "user_id": int(phone),
            "name": name,
            "birth_date": birth_date,
            "postal_code": postal_code,
            "register_date_time": datetime.now().strftime("%d-%m-%Y_%H:%M:%S")

        }
    try:
        dynamodb.user_table.put_item(Item=item)
        return {"Output": "Usuario registrado correctamente"}
    except Exception as e:
        return {"Output": f"No se puedo registrar al usuario en la base por motivo: {e}"}
    
@tool
def finish_session(config:RunnableConfig):
    """
    Finalizar la session de la conversacion. Se ejecuta cuando el usuario se despide o 
    ya no tiene interes en continuar la conversacion, o no necesita nada mas.
    """
    user_state = config.get("configurable", {})
    user_id = int(user_state.get("user_id", 0))
    business_id =  int(user_state.get("business_id", 0))
    init_date_time = user_state.get("session_init_date_time", "")

    try:
        key={
                "session_id": f'{user_id}-{business_id}',
                "init_date_time":str(init_date_time)
            }
        print(key)
        dynamodb.session_table.update_item(
            Key=key,
            UpdateExpression='SET #status = :status, final_date_time = :f_datetime',
        ExpressionAttributeNames={
            '#status': 'session_status'
        },
        ExpressionAttributeValues={
            ':status': 'closed',
            ':current_status': 'active',  # Valor actual esperado
            ':f_datetime' : datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        },
        ConditionExpression='attribute_exists(session_id) AND #status = :current_status'
        )
        return {"Output": "Session finalizada, despidete"}
    except Exception as e:
        return {"Output":f"No se pudo finalizar session {e}"}


@tool
def cancel_appointment(date_appointment:str,config: RunnableConfig):
    """
    Cancela una cita que coincida con la fecha que indica el usaurio.
    Se modifica el estado de la cita en la base de datos.
    Args:
        date_appointment (str): Fecha de la cita
    """
    user_state = config.get("configurable", {})
    user_id = user_state.get("user_id", 0)
    try:
        dynamodb.update_item(
            table=dynamodb.appintment_table,
            key={
                "user_id": int(user_id),
                "date_appointment": str(date_appointment)
            },
            column_to_update="appointment_status",
            value_to_update="canceled"
        )
        return {"Output": "Cita cancelada correctamente"}
    except Exception as e:
        return {"Output":f"No se pudo cancelar la cita {e}"}
    

@tool
def consult_appointment(config: RunnableConfig):
    """
    Consulta todas las citas activas del mismo usuario y muestra la hora de inicio y hora final de la cita
    """
    user_state = config.get("configurable", {})
    user_id = user_state.get("user_id", 0)
    
    try:
        response = dynamodb.get_appointments(
            table=dynamodb.appintment_table,
            user_id=int(user_id)
            )
        appointment_dates = [appt["date_appointment"] for appt in response if "date_appointment" in appt]
        if response:
            return {"appointments": response}
        else:
            return {"message": "No hay citas registradas para este usuario."}
    except Exception as e:
        return {"Output":f"No se pudo verificar las citas {e}"}
    

@tool
def register_appointment(date_appointment:str, config: RunnableConfig):
    """
    Registra una cita si no hay otra cita que se solape en el mismo negocio.

    Args:
        date_appointment (str): Fecha y hora de la cita en formato "YYYY-MM-DD HH:MM:SS".
    """
    user_state = config.get("configurable", {})
    user_id = user_state.get("user_id", 0)
    business_id = user_state.get("business_id", 0)    
    date_format = "%Y-%m-%d %H:%M:%S"
    date_appointment = datetime.strptime(date_appointment, date_format)
    date_appointment_end = date_appointment + timedelta(hours=1)

    try:
        if date_appointment.time() < OPEN or date_appointment.time() > CLOSE:
            return {"Output": "El negocio no esta abierto en este horario."}
        # consulta las citas existentes del mismo negocio
        response = dynamodb.business_appointments(
            table=dynamodb.appintment_table,
            business_id=int(business_id)
        )
        existing_appointments = response.get("Items", [])

        # Validar solapamiento con citas activas
        for appt in existing_appointments:
            existing_start = datetime.strptime(appt["date_appointment"], date_format)
            existing_end = datetime.strptime(appt["date_appointment_end"], date_format)

            # Si la nueva cita comienza antes de que termine otra cita y termina después de que comienza otra cita, se solapan
            if date_appointment < existing_end and date_appointment_end > existing_start:
                return {"error": "Ya existe una cita agendada en el horario propuesto."}
                
        # Si no hay citas quee se solapen, se registra la cita
        # dynamodb.put_item(
        #     table_name=APPOINTMENT_TABLE,
        #     item={
        #         "user_id": int(user_id),
        #         "business_id": int(business_id),
        #         "date_appointment": str(date_appointment),
        #         "date_appointment_end": str(date_appointment_end),
        #         "appointment_status": str("active")
        #     }
        # )
        dynamodb.put_item_appointment(item={
                "user_id": int(user_id),
                "business_id": int(business_id),
                "date_appointment": str(date_appointment),
                "date_appointment_end": str(date_appointment_end),
                "appointment_status": str("active")
            })
        return {"message": "Cita agendada exitosamente."}
    except Exception as e:
        return {"error": f"Error al agendar cita: {str(e)}"}
    

@tool
def update_appointment(date_appointment:str, new_date_appointment:str, config: RunnableConfig):
    """
    Reagenda una cita si no hay otra cita que se solape en el mismo negocio.

    Args:
        date_appointment (str): Fecha y hora de la cita ya programada en formato "YYYY-MM-DD HH:MM:SS".
        new_date_appointment (str): Nueva fecha y hora de la cita en formato "YYYY-MM-DD HH:MM:SS".
    """
    user_state = config.get("configurable", {})
    user_id = user_state.get("user_id", 0)
    business_id = user_state.get("business_id", 0)    
    date_format = "%Y-%m-%d %H:%M:%S"
    new_date_appointment = datetime.strptime(new_date_appointment, date_format)
    new_date_appointment_end = new_date_appointment + timedelta(hours=1)


    try:
        if new_date_appointment.time() < OPEN or new_date_appointment.time() > CLOSE:
            return {"error": "El negocio no esta abierto en este horario."}
        # consulta las citas existentes del mismo negocio
        response = dynamodb.business_appointments(
            table=dynamodb.appintment_table,
            business_id=int(business_id)
        )
        existing_appointments = response.get("Items", [])

        # Validar solapamiento con citas activas
        for appt in existing_appointments:
            existing_start = datetime.strptime(appt["date_appointment"], date_format)
            existing_end = datetime.strptime(appt["date_appointment_end"], date_format)

            # Si la nueva cita comienza antes de que termine otra cita y termina después de que comienza otra cita, se solapan
            if new_date_appointment < existing_end and new_date_appointment_end > existing_start:
                return {"error": "Ya existe una cita agendada en el horario propuesto."}
                
            
        # Si no hay citas quee se solapen, se actualiza la cita
        dynamodb.update_item(
            table=dynamodb.appintment_table,
            key={
                "user_id": int(user_id), 
                "date_appointment": str(date_appointment)
            },
            column_to_update="appointment_status",
            value_to_update="canceled"
        )

        # dynamodb.put_item(
        #     table_name=APPOINTMENT_TABLE,
        #     item={
        #         "user_id": int(user_id),
        #         "business_id": int(business_id),
        #         "date_appointment": str(new_date_appointment),
        #         "date_appointment_end": str(new_date_appointment_end),
        #         "appointment_status": str("active")
        #     }
        # )
        dynamodb.put_item_appointment(item={
            "user_id": int(user_id),
            "business_id": int(business_id),
            "date_appointment": str(new_date_appointment),
            "date_appointment_end": str(new_date_appointment_end),
            "appointment_status": str("active")
        })


        return {"message": "Cita agendada exitosamente."}
    except Exception as e:
        return {"error": f"Error al agendar cita: {str(e)}"}
    

@tool
def get_free_hours(date_appointment:str, config: RunnableConfig):
    """
    Consulta las horas disponibles para agendar una cita en una fecha específica.
    Args:
        date_appointment (str): Fecha de la cita en formato "YYYY-MM-DD HH:MM:SS".
    """
    user_state = config.get("configurable", {})
    business_id = user_state.get("business_id", 0)
    date_format = "%Y-%m-%d %H:%M:%S"
    date_appointment = datetime.strptime(date_appointment, date_format)

    try:
        # consulta las citas existentes del mismo negocio
        response = dynamodb.business_appointments(
            table=dynamodb.appintment_table,
            business_id=int(business_id)
        )
        existing_appointments = response.get("Items", [])

        # Filtrar horas ocupadas
        busy_hours = []
        for appt in existing_appointments:
            existing_start = datetime.strptime(appt["date_appointment"], date_format)
            if existing_start.date() == date_appointment.date():
                busy_hours.append(existing_start.time())
                
        # Generar horas disponibles
        free_hours = []
        current_time = datetime.combine(date_appointment.date(), OPEN)
        while current_time.time() < CLOSE:
            if current_time.time() not in busy_hours:
                free_hours.append(current_time.time())
            current_time += timedelta(hours=1)

        return {"Horas disponibles": free_hours}
    except Exception as e:
        return {"error": f"Error al consultar horas disponibles: {str(e)}"}