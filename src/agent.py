import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from utils.prompt import AGENT_PROMPT
from utils.memory_saver import DynamoDBSaver
from utils.tools import (
    register_user, 
    finish_session,
    cancel_appointment,
    consult_appointment,
    register_appointment,
    update_appointment,
    get_free_hours
    )

load_dotenv()

class AgentAppointmentManagement:
    def __init__(self):
        self.memory = DynamoDBSaver(
            table_name=os.getenv("SESSION_TABLE"),
            max_messages=20,
            client_config={
                "endpoint_url":'http://localhost:8000'
            }
        )

        self.model = ChatOpenAI(
                    model=os.getenv("LLM_MODEL"), 
                    temperature=0.5, 
                    max_tokens=100
                    )
        self.tools = [
            register_user,
            finish_session,
            cancel_appointment,
            consult_appointment,
            register_appointment,
            update_appointment,
            get_free_hours
            ]
        
        self.agent = create_react_agent(
            model=self.model, 
            tools=self.tools,
            prompt=AGENT_PROMPT,
            checkpointer=self.memory,
            debug=False
            )
        
    def conversation(self, user_input:str, cfg:dict):
        messages = {"messages": [
                HumanMessage(content=user_input),
                SystemMessage(content=f'¿El usuario esta registrado? {cfg["configurable"]["is_register"]}', id="00001"),
                SystemMessage(content=f'El nombre del usuario es: {cfg["configurable"]["user_name"]}', id="00002"),
                SystemMessage(content=f'La fecha de hoy es: {cfg["configurable"]["today"]}', id="00003")
                ]}
        print(messages)
        response = self.agent.invoke(
            input=messages,
            config=cfg
            )
        print(response)
        return response
