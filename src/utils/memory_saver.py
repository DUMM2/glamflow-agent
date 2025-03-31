import boto3
from typing import Any, Dict, Optional, Sequence
from langchain_core.runnables import RunnableConfig
from datetime import datetime
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    CheckpointTuple,
    Checkpoint,
    CheckpointMetadata,
    ChannelVersions,
)
from langgraph.checkpoint.serde.base import SerializerProtocol

class DynamoDBSaver(BaseCheckpointSaver):
    """
    Saver simplificado para DynamoDB que utiliza una única tabla para almacenar el checkpoint.
    
    - Se utiliza la clave compuesta por:
         session_id: identificador de la sesión.
         session_init_date_time: se usa el valor fijo "latest" para actualizar el mismo registro.
    - En el método `put` se guarda el checkpoint completo (todo el historial de mensajes).
    - En el método `get_tuple`, se recupera el checkpoint y se limita la lista de mensajes a los últimos n 
      (sin modificar el dato almacenado en la base).
    """

    def __init__(
        self,
        *,
        client_config: Optional[Dict[str, Any]] = None,
        serde: Optional[SerializerProtocol] = None,
        table_name: str,
        max_messages: int = 5,  # Número máximo de mensajes a retornar en memoria
    ) -> None:
        # Se inicializa la clase base, pasando el objeto 'serde'
        super().__init__(serde=serde)
        # Se crean el cliente y el recurso de DynamoDB usando boto3.
        self.dynamodb = boto3.resource("dynamodb", **(client_config or {}))
        # Nombre de la tabla en DynamoDB
        self.table_name = table_name
        # Obtenemos la referencia a la tabla
        self.table = self.dynamodb.Table(self.table_name)
        # Número máximo de mensajes que se cargarán en memoria al recuperar el checkpoint
        self.max_messages = max_messages

    def validate_configurable(self, configurable: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """
        Valida que en la configuración se haya pasado el parámetro 'session_id'.
        Si no está presente, se lanza un error.
        """
        if not configurable or "session_id" not in configurable:
            raise ValueError("Missing 'session_id' in configurable")
        return {"session_id": configurable["session_id"], "session_init_date_time": configurable["session_init_date_time"]}

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """
        Recupera el checkpoint almacenado en DynamoDB usando la clave:
            - session_id (proporcionado en configurable)
            - session_init_date_time: "latest"
            
        Luego, deserializa el checkpoint y la metadata. Antes de retornarlo, se limita la lista 
        de mensajes a los últimos 'max_messages' sin modificar el dato completo almacenado en la base.
        """
        # Validamos la configuración y obtenemos el session_id.
        configurable = self.validate_configurable(config.get("configurable"))
        key = {"session_id": configurable["session_id"], "init_date_time": configurable["session_init_date_time"]}
        
        # Obtenemos el ítem de DynamoDB
        response = self.table.get_item(Key=key)
        item = response.get("Item")
        if not item:
            return None

        try:
            # Deserializamos el checkpoint y la metadata usando el serializador (serde)
            checkpoint = self.serde.loads_typed([item["type"], item["checkpoint"].value])
            metadata = self.serde.loads_typed([item["type"], item["metadata"].value])

            # Creamos una copia del checkpoint para limitar la cantidad de mensajes en memoria
            # sin modificar el registro almacenado.
            if isinstance(checkpoint, dict):
                checkpoint_truncated = checkpoint.copy()
                channel_values = checkpoint.get("channel_values", {}).copy()
                if "messages" in channel_values:
                    messages = channel_values["messages"]
                    # Se toman solo los últimos 'max_messages' mensajes.
                    channel_values["messages"] = messages[-self.max_messages:]
                checkpoint_truncated["channel_values"] = channel_values
            else:
                checkpoint_truncated = checkpoint

            # Retornamos un CheckpointTuple con la configuración y el checkpoint truncado.
            return CheckpointTuple(
                config={"configurable": key},
                checkpoint=checkpoint_truncated,
                metadata=metadata,
                parent_config=None,
                pending_writes=[],
            )
        except KeyError:
            return None

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """
        Guarda (o actualiza) el checkpoint en la tabla DynamoDB.
        
        Se utiliza la clave:
            - session_id: del configurable.
            - session_init_date_time: "latest" (fijo)
            
        Esto sobrescribe el registro existente, permitiendo mantener todo el historial
        de mensajes en la base de datos.
        """
        # Validamos la configuración y extraemos el session_id.
        configurable = self.validate_configurable(config.get("configurable"))
        session_id = configurable["session_id"]
        init_date_time = configurable["session_init_date_time"]
        key = {"session_id": session_id, "init_date_time": init_date_time}
        
        # Serializamos el nuevo checkpoint y la metadata.
        type1, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
        type2, serialized_metadata = self.serde.dumps_typed(metadata)
        if type1 != type2:
            raise ValueError("Checkpoint and metadata serialization types do not match.")
        
        # Armamos el ítem a guardar. Este ítem contendrá el checkpoint completo,
        # es decir, todos los mensajes y el estado, sin truncar.

        # Usamos update ite, para insertar o actualizar el registro.
        #self.table.put_item(Item=item)
        self.table.update_item(
            Key=key,
            UpdateExpression='SET #type = :type_v, checkpoint = :checkpoint_v, metadata = :metadata_v',
            ExpressionAttributeNames={
                '#type':'type'
            },
            ExpressionAttributeValues={
                ':type_v':type1,
                ':checkpoint_v':serialized_checkpoint,
                ':metadata_v':serialized_metadata
            }
        )
        return {"configurable": key}

    # Los métodos list, put_writes, y los asíncronos se pueden omitir o implementar según se requiera.
    # En este ejemplo, nos centramos en get_tuple y put para simplificar la implementación.

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ):
        """
        Método no implementado para este saver simplificado.
        """
        raise NotImplementedError("El método 'list' no se implementa en SimpleDynamoDBSaver.")

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """
        Método no implementado para este saver simplificado.
        """
        #raise NotImplementedError("El método 'put_writes' no se implementa en SimpleDynamoDBSaver.")


    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
            """Get the checkpoint tuple from DynamoDB"""
            configurable = self.validate_configurable(config.get("configurable"))
            key = {
                "session_id": configurable["session_id"],
                "created_at": configurable["created_at"]
            }
            item = self.dynamodb.get_checkpoint(key)
            
            try:
                # Deserialize the checkpoint and metadata
                checkpoint = self.serde.loads_typed([item["type"], item["checkpoint"].value])
                metadata = self.serde.loads_typed([item["type"], item["metadata"].value])

                if isinstance(checkpoint, dict):
                    checkpoint_truncated = checkpoint.copy()
                    channel_values = checkpoint.get("channel_values", {}).copy()
                    if "messages" in channel_values:
                        messages = channel_values["messages"]
                        channel_values["messages"] = messages[-self.max_messages:]
                    checkpoint_truncated["channel_values"] = channel_values
                else:
                    checkpoint_truncated = checkpoint

                return CheckpointTuple(
                    config={"configurable": key},
                    checkpoint=checkpoint_truncated,
                    metadata=metadata,
                    parent_config=None,
                    pending_writes=[]
                )

            except KeyError:
                return None


    async def aput(
            self,
            config: RunnableConfig,
            checkpoint: Checkpoint,
            metadata: Optional[CheckpointMetadata] = None,
            new_versions: Optional[ChannelVersions] = None
        ) -> None:
        """Put the checkpoint into DynamoDB"""
        configurable = self.validate_configurable(config.get("configurable"))
        session_id = configurable["session_id"]
        created_at = configurable["created_at"]

        key = {
            "session_id": session_id,
            "created_at": created_at
        }

        # Serialize the checkpoint and metadata
        type1, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
        type2, serialized_metadata = self.serde.dumps_typed(metadata)

        if type1 != type2:
            raise ValueError("Checkpoint and metadata types do not match")
        
        # Update the item
        if self.dynamodb.save_checkpoint(key, type1, serialized_checkpoint, serialized_metadata, datetime.now().isoformat()):
            return {"configurable": key}
        else:
            raise ValueError("Error saving checkpoint")


    async def alist(self, config: RunnableConfig) -> None:
        """No implemented"""
        #raise NotImplementedError("List is not implemented")
        
    async def aput_writes(
            self, 
            config: RunnableConfig,
            writes:  None,
            task_id: str,
            task_path: str = ""
        ) -> None:
        """No implemented"""
        #raise NotImplementedError("put_writes is not implemented")