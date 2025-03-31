import asyncio
from utils.status import Status
from agent import AgentAppointmentManagement


if __name__ == "__main__":
    # Harcode user_id==user_phone_number
    user_id = "5566776677"
    # Hardcode business_id==business_phone_number
    business_id = "5599889966"

    # Instantiate methods
    stat = Status()
    agent = AgentAppointmentManagement()

    # Get User & session status
    session_dict = asyncio.run(stat.session_status(user_id, business_id))
    user_stat_dict = asyncio.run(stat.user_status(user_id, business_id))
    print(session_dict)

    config = {"configurable":{
        "session_id":str(user_id) +"-"+ str(business_id),
        "user_id":user_id,
        "user_name":user_stat_dict["user_name"],
        "business_id":business_id,
        "is_register":user_stat_dict["is_register"],
        "session_init_date_time":session_dict["init_date_time"],
        "today": user_stat_dict["today"]
        }
    }
    print(config)

    print("="*100)
    while True:
        user_input = input("User: ")
        if user_input == "exit":
            break
        response = agent.conversation(user_input, config)
        #print(response["messages"][-1].response_metadata)
        print()
        print("Agent:", response["messages"][-1].content)