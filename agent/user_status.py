import os
import boto3
from dotenv import load_dotenv
from datetime import datetime
from boto3.dynamodb.conditions import Key

load_dotenv()


class Status:
    def __init__(self):
        dynamodb = boto3.resource("dynamodb", endpoint_url='http://localhost:8000', region_name=os.getenv("AWS_REGION"))
        self.user_table = dynamodb.Table(os.getenv("USER_TABLE"))
        self.appointment_table = dynamodb.Table(os.getenv("APPOINTMENT_TABLE"))
        self.session_table = dynamodb.Table(os.getenv("SESSION_TABLE"))
        self.business_table = dynamodb.Table(os.getenv("BUSINESS_TABLE"))
    
    def session_status(self, user_id:str):
        session = {}
        user_id = int(user_id)

        session_response = self.session_table.query(
            IndexName="StatusIndex",
            KeyConditionExpression=Key("status").eq("active") & Key("user_id").eq(user_id)
        )
        session_response = session_response.get("Item", {})

        # Create session if not exist active
        if "user_id" not in session_response:
            self.session_table.put_item(Item={
                "user_id":user_id,
                "init_date_time": datetime.now().strftime("%d-%m-%y_%H:%M"),
                "status":"active",
                "messages_histoy":[]
            })
            session = {"session_id":user_id, "messages_history":[]}
            return session
        
        # Set session params
        session["session_id"]=session_response.get("user_id", None)
        session["init_date_time"]=session_response.get("init_date_time","")
        session["messages_history"]=session_response.get("messages_histoy",[])
        return session

    def user_status(self, user_id:str, business_id:str):
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


            


# d = Status()
# user_id="5571098839"
# business_id="8877665544"

# session = d.session_status(user_id=user_id)
# print(session)
# user_status = d.user_status(user_id=user_id, business_id=business_id)
# print(user_status)


