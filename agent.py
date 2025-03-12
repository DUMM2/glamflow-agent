import os
from dotenv import load_dotenv
from prompt import AGENT_PROMPT
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from tools.dynamo_tool import register_user

load_dotenv()

class AgentOpenAI:
    def __init__(self, STATE):
        self.state = STATE
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"), 
            temperature=0.5, 
            max_tokens=100
            )
        self.memory = ConversationBufferMemory(
            return_messages=True, 
            output_key="output",
            )
        
        self.tools = [register_user]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_PROMPT),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        self.agent_conversation = AgentExecutor(
            agent=self.agent,
            memory=self.memory,
            tools=self.tools,
            max_iterations=3,
            return_intermediate_steps=True,
            verbose=True
        )
    

    def conversation(self, user_input:str):
        response = self.agent_conversation.invoke({
            "input": user_input
        })
        return response

if __name__ == "__main__":
    state = {
        "user_number": "1234567890",
        "name": "Dan",
        "business_id": "5566778899",
        "is_registered": False
    }
    agent = AgentOpenAI(state)
    print("="*100)
    while True:
        user_input = input("User: ")
        if user_input == "exit":
            break
        response = agent.conversation(user_input)
        print()
        print("Agent:", response["output"])