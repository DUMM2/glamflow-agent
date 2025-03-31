import os
from dotenv import load_dotenv
from datetime import datetime
from utils.dynamodb import DynamoDB
from boto3.dynamodb.conditions import Key, Attr

load_dotenv()

class Status:
    def __init__(self):
        dynamodb = DynamoDB()
        self.user_table = dynamodb.user_table
        self.appointment_table = dynamodb.appintment_table
        self.session_table = dynamodb.session_table
        self.business_table = dynamodb.business_table
    

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
                "init_date_time": datetime.now().strftime("%d-%m-%Y_%H:%M:%S"),
                "session_status":"active"
            }
            self.session_table.put_item(Item=item)
            return item
        
        # Set session params
        session_response =  session_response[0]
        session["session_id"]=session_response.get("session_id", None)
        session["init_date_time"]=session_response.get("init_date_time","")
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
        status["today"] = datetime.now().strftime("%d-%m-%Y")
        return status
