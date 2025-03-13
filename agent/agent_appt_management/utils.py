import os
import boto3
from dotenv import load_dotenv

load_dotenv()


class DynamoDB:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", endpoint_url='http://localhost:8000', region_name=os.getenv("AWS_REGION"))

    def put_item(self, table_name:str, item:dict):
        table = self.dynamodb.Table(table_name)
        response = table.put_item(Item=item)
        return response
    
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
