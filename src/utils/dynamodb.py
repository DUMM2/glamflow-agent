import os
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

load_dotenv()


class DynamoDB:
    def __init__(self):
        USER_TABLE = os.getenv("USER_TABLE")
        SESSION_TABLE = os.getenv("SESSION_TABLE")
        APPOINTMENT_TABLE = os.getenv("APPOINTMENT_TABLE")
        BUSINESS_TABLE = os.getenv("BUSINESS_TABLE")

        AWS_REGION = os.getenv("AWS_REGION")
        URL_DYNAMODB_LOCAL = os.getenv("URL_DYNAMODB_LOCAL")

        self.dynamodb = boto3.resource("dynamodb", endpoint_url=URL_DYNAMODB_LOCAL, region_name=AWS_REGION)

        self.session_table = self.dynamodb.Table(SESSION_TABLE)
        self.user_table = self.dynamodb.Table(USER_TABLE)
        self.appintment_table = self.dynamodb.Table(APPOINTMENT_TABLE)
        self.business_table = self.dynamodb.Table(BUSINESS_TABLE)


    def put_item_appointment(self, item):
        self.appintment_table.put_item(
            Item=item
        )

    
    def get_item(self, table_name:str, key_name:str, key_value, filter_key:str, filter_value):
        """
        Consulta una tabla de DynamoDB para obtener elementos basados en una clave de partición y un filtro.

        Args:
            table_name (str): Nombre de la tabla en DynamoDB.
            key_name (str): Nombre de la clave de partición.
            key_value (int): Valor de la clave de partición a consultar.
            filter_key (str): Nombre del atributo a excluir en la consulta.
            filter_value (str): Valor del atributo a excluir en la consulta.

        Returns:
            List[Dict]: Lista de elementos obtenidos de DynamoDB.
        """
        table = self.dynamo.Table(table_name)
        response = table.query(
            KeyConditionExpression=f"{key_name} = :key_value",
            FilterExpression=f"{filter_key} <> :filter_value",
            ExpressionAttributesValues={
                ":key_value":key_value,
                ":filter_value":filter_value
            }
        )
        return response.get("Items", [])
    

    def update_item(self, table:str, key:dict, column_to_update:str, value_to_update:any):
        
        try:
            response = table.update_item(
                Key=key,
                UpdateExpression=f"SET {column_to_update} = :new_status",
                ExpressionAttributeValues={
                    ":new_status": value_to_update
                    }
                    )
        except Exception as e:
            return {"error": f"Error al actualizar la cita: {str(e)}"}


    def get_appointments(self, table ,user_id:int):
        try:
            response = table.query(
                KeyConditionExpression="user_id = :user_id",
                FilterExpression="appointment_status = :status",
                ExpressionAttributeValues={":user_id": int(user_id), ":status": "active"}
                )
            return response.get("Items", [])
        except Exception as e:
            return {"error": f"Error al consultar citas: {str(e)}"}


    def  business_appointments(self, table,business_id:int):
        try:
            response = table.query(
                IndexName="BusinessIndex",
                FilterExpression="appointment_status = :status",
                KeyConditionExpression=Key('business_id').eq(int(business_id)),
                ExpressionAttributeValues={":status": "active"}
                )
            return response
        except Exception as e:
            return {"error": f"Error al consultar citas: {str(e)}"}