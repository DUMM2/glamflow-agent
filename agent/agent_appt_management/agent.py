import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from agent_appt_management.tools import register_user, check_user_registration
from agent_appt_management.prompt import AGENT_PROMPT

load_dotenv()

class AgentAppointmentManagement:
    def __init__(self):
        self.memory = MemorySaver() # No productivo

        self.model = ChatOpenAI(
                    model=os.getenv("LLM_MODEL"), 
                    temperature=0.5, 
                    max_tokens=100
                    )
        self.tools = [
            check_user_registration,
            register_user
            ]
        
        self.agent = create_react_agent(
            model=self.model, 
            tools=self.tools,
            prompt=AGENT_PROMPT,
            checkpointer=self.memory,
            debug=False
            )
        
    def conversation(self, user_input:str, cfg:dict):
        response = self.agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=cfg
            )
        return response
