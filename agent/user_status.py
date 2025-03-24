import os
import boto3
import boto3.dynamodb
from boto3.dynamodb.types import Binary
from dotenv import load_dotenv
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from langgraph.checkpoint.serde.base import SerializerProtocol


# dev
import json

load_dotenv()


class Status:
    def __init__(self):
        dynamodb = boto3.resource("dynamodb", endpoint_url='http://localhost:8000', region_name=os.getenv("AWS_REGION"))
        self.user_table = dynamodb.Table(os.getenv("USER_TABLE"))
        self.appointment_table = dynamodb.Table(os.getenv("APPOINTMENT_TABLE"))
        self.session_table = dynamodb.Table(os.getenv("SESSION_TABLE"))
        self.business_table = dynamodb.Table(os.getenv("BUSINESS_TABLE"))
    

    async def session_status(self, user_id:str, business_id:str):
        session = {}
        user_id = int(user_id)
        session_id = str(user_id) +"-"+ str(business_id)

        session_response = self.session_table.query(
            KeyConditionExpression= Key("session_id").eq(session_id),
            FilterExpression=Attr("session_status").eq("active")
        )

        session_response = session_response.get("Items", {})
        # Create session if not exist active
        if  len(session_response) == 0:
            item = {
                "session_id":str(user_id) +"-"+ str(business_id),
                "init_date_time": datetime.now().strftime("%d-%m-%y_%H:%M:%S"),
                "session_status":"active"
            }
            self.session_table.put_item(Item=item)
            return item
        
        
        # Set session params
        session_response =  session_response[0]
        session["session_id"]=session_response.get("session_id", None)
        session["init_date_time"]=session_response.get("init_date_time","")
        session["messages_history"]=session_response.get("messages_history",[])
        return session


    async def user_status(self, user_id:str, business_id:str):
        status = {}
        user_id = int(user_id)
        business_id = int(business_id)

        # Chec if user is register
        user_response = self.user_table.get_item(
            Key={"user_id":user_id}
        )

        user_response = user_response.get("Item", {})
        status["user_name"] = user_response.get("name", "")
        status["user_id"] = user_id
        status["business_id"] = business_id 
        status["is_register"] = True if "name" in user_response else False
        
        return status
