import os
from typing import Annotated
from datetime import datetime
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from agent_appt_management.utils import DynamoDB
from langchain_core.runnables.config import RunnableConfig

dynamodb = DynamoDB()
USER_TABLE = os.getenv("USER_TABLE")

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

@tool
def check_user_registration(config:RunnableConfig):
    """
    Verifica si un usuario está registrado antes de solicitar su información.
    """
    user_state = config.get("configurable", {})
    if user_state.get("is_registered", False):
        return {"Output": "El usuario ya esta registrado"}
    return {"Output": "El usuario no esta registrado"}
    
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
    
    birth_date = datetime.strptime(birth_date, "%d-%m-%Y").strftime("%Y-%m-%d")
    phone = user_state.get("user_number", 0)
    item = {
            "user_id": int(phone),
            "name": name,
            "birth_date": birth_date,
            "postal_code": postal_code,
            "register_date_time": datetime.now().strftime("%d-%m-%y_%H:%M")

        }
    try:
        dynamodb.put_item(table_name=USER_TABLE, item=item)
        return "Usuario registrado correctamente"
    except Exception as e:
        return f"No se puedo registrar al usuario en la base por motivo: {e}"
    
