import os
from datetime import datetime
from langchain_core.tools import tool
from agent_appt_management.utils import DynamoDB
from langchain_core.runnables.config import RunnableConfig

dynamodb = DynamoDB()

@tool
def state_check(config: RunnableConfig) -> dict:
    """Verifica la variable de estado 'user_state'
        Args:
            
        Returns:
            dict: Variable de estado
    """
    # Obtener configuraciones
    user_state = config.get("configurable", {})
    # Obtener configuracion especifica si no default
    id_session = user_state.get("thread_id", None)
    id_phone = user_state.get("user_number", "")
    id_business = user_state.get("business_id", "")
    is_registered = user_state.get("is_registered", False)

    print(f"    session: {id_session}")
    print(f"    user_phone: {id_phone}")
    print(f"    bussines_phone: {id_business}")
    print(f"    user is registered: {is_registered}")
    return {"Output": " State Checked"}

# @tool
# def check_user_registration(config:RunnableConfig):
#     """
#     Verifica si un usuario está registrado antes de solicitar su información.
#     """
#     user_state = config.get("configurable", {})
#     if user_state.get("is_registered", False):
#         return {"Output": "El usuario ya esta registrado"}
#     return {"Output": "El usuario no esta registrado"}
    
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
            "register_date_time": datetime.now().strftime("%d-%m-%y_%H:%M")

        }
    try:
        dynamodb.put_item(table_name=dynamodb.user_table, item=item)
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
            ':f_datetime' : datetime.now().strftime("%d-%m-%y_%H:%M:%S")
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
            table_name=APPOINTMENT_TABLE,
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
    Consulta todas las citas activas del mismo usuario y las muestra.
    """
    user_state = config.get("configurable", {})
    user_id = user_state.get("user_id", 0)
    
    try:
        response = dynamodb.get_appointments(
            table_name=APPOINTMENT_TABLE,
            user_id=int(user_id)
            )
        appointment_dates = [appt["date_appointment"] for appt in response if "date_appointment" in appt]
        if response:
            return {"appointments": response}
        else:
            return {"message": "No hay citas registradas para este usuario."}
    except Exception as e:
        return {"Output":f"No se pudo verificar las citas {e}"}


