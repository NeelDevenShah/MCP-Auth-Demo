import asyncio
from crewai import Agent, Task, Crew, LLM
from crewai_tools import MCPServerAdapter
from fastmcp.server.auth.providers.bearer import RSAKeyPair
from pydantic import SecretStr
from dotenv import load_dotenv
import os
import jwt

# How many previous messages to remember
MEMORY_SIZE = 6

def get_gemini_llm():
    return LLM(
        api_key=os.getenv("GEMINI_API_KEY", ""),
        model="gemini/gemini-2.5-flash",
    )

async def main():
    load_dotenv()
    # Load keys from files
    with open("mcp_auth/private.pem", "r") as f:
        private_key_pem = f.read()
    with open("mcp_auth/public.pem", "r") as f:
        public_key_pem = f.read()

    key_pair = RSAKeyPair(
        private_key=SecretStr(private_key_pem),
        public_key=public_key_pem
    )

    token = key_pair.create_token(
        subject="alice",
        issuer="https://dev-issuer.com",
        audience="my-mcp-server",
        additional_claims={"job_role": "Manager", "id": "123", "name": "Alice"}
        # additional_claims={"job_role": "AssistantManager", "id": "123"}
        # additional_claims={"job_role": "Officer", "id": "123"} # Change the role here, as the system is following RBAC
    )
    headers = {"Authorization": f"Bearer {token}"}

    claims = jwt.decode(
        token,
        public_key_pem,
        algorithms=["RS256"],
        audience="my-mcp-server",
        issuer="https://dev-issuer.com"
    )
    print('------------------------------')
    print(claims)
    print('--------------------------------')
    role = claims.get("job_role", "")
    print(f"Authenticated as {claims['name']} with role {role} with id {claims['id']}")

    # Setup allowed servers by role
    if role == "Manager":
        servers = [
            {"url": "http://localhost:8001/sse", "transport": "sse", "headers": headers},  # HR Management
            {"url": "http://localhost:8002/sse", "transport": "sse", "headers": headers},  # Project Management
            {"url": "http://localhost:8003/sse", "transport": "sse", "headers": headers},  # CRM
        ]
        permitted_server = ['hr_management', 'project_management', 'crm']
        non_permitted_server = ['NA']

    elif role == "AssistantManager":
        servers = [
            {"url": "http://localhost:8001/sse", "transport": "sse", "headers": headers},  # HR Management
            {"url": "http://localhost:8002/sse", "transport": "sse", "headers": headers},  # Project Management
        ]
        permitted_server = ['hr_management', 'project_management']
        non_permitted_server = ['crm']

    else:
        servers = [{"url": "http://localhost:8001/sse", "transport": "sse", "headers": headers}]  # HR Management only
        permitted_server = ['hr_management']
        non_permitted_server = ['project_management', 'crm']

    gemini_llm = get_gemini_llm()

    # The conversation memory: list of dicts (role: "user"/"assistant", content: text)
    conversation_memory = []

    with MCPServerAdapter(servers) as aggregated_tools:
        agent = Agent(
            role=f"{role} Agent",
            goal=f"Use only allowed tools and always confirm data modifications and your details are: {role} with id {id} with name {claims['name']}",
            backstory=f"""Testing roles, The Agent has access to the following tools: {str(permitted_server)} and does not have access to the following tools: {str(non_permitted_server)} based on the role of the user.

IMPORTANT SAFETY PROTOCOL: Before using any tools that create, add, update, or modify data in the production database, you MUST:
1. Identify if the requested operation involves data modification (create, add, update, delete, approve, etc.)
2. If it's a data modification operation, ask the user for explicit confirmation
3. Only proceed with the data modification after receiving user approval
4. For read-only operations (check, list, get, view), proceed normally without confirmation

Data modification operations include: creating employee records, updating project tasks, adding customer profiles, approving leave requests, etc.
Read-only operations include: checking employee status, listing project tasks, viewing customer details, etc.""",
            tools=aggregated_tools,
            llm=gemini_llm,
            verbose=True,
            reasoning=False
        )

        print("You can now chat with the system. Type 'exit' to quit.")
        print("\nAvailable systems based on your role:")
        print(f"- HR Management System: Employee records, leave requests, performance reviews")
        print(f"- Project Management System: Task tracking, milestones, team management")
        print(f"- CRM System: Customer profiles, interactions, sales opportunities")
        print(f"\nYour access: {', '.join(permitted_server)}")
        
        while True:
            user_input = input("\nUser: ").strip()
            if user_input.lower() == "exit":
                print("Exiting chat.")
                break

            # Add user input to memory
            conversation_memory.append({"role": "user", "content": user_input})
            # Trim memory to last MEMORY_SIZE turns (user+AI pairs)
            conversation_memory = conversation_memory[-MEMORY_SIZE:]

            # Build a conversation/history string for context
            memory_prompt = ""
            for m in conversation_memory[:-1]:  # all except current user
                who = "User" if m["role"] == "user" else "Assistant"
                memory_prompt += f"{who}: {m['content']}\n"
            # Add latest user input
            memory_prompt += f"User: {user_input}\nAssistant: "

            # Make an agent Task using the memory as context
            task = Task(
                agent=agent,
                description=memory_prompt,
                expected_output="""Provide the most accurate and relevant answer using available tools and conversation context. 

CRITICAL: If the user request involves data modification (create, update, add, delete, approve), you must:
1. First ask the user for explicit confirmation before proceeding
2. Explain what data will be modified and the potential impact
3. Only execute the modification after receiving user approval
4. For read-only operations, proceed immediately without confirmation

Always prioritize data safety and user consent for any production database changes."""
            )

            # The Crew object is required to run the agent+task, but only for this step
            crew = Crew(
                agents=[agent],
                tasks=[task],
                llm=gemini_llm,
                verbose=True
            )
            result = crew.kickoff()

            print(f"Assistant: {str(result)}")
            # Store agent response in memory
            conversation_memory.append({"role": "assistant", "content": str(result)})
            # Again, trim
            conversation_memory = conversation_memory[-MEMORY_SIZE:]

if __name__ == "__main__":
    asyncio.run(main())

# # Sample Questions for HR Management:
# Check employee records
# Create a new employee record for John Doe
# Submit a leave request for employee EMP-001
# Check leave request status
# Create a performance review for employee EMP-001

# # Sample Questions for Project Management:
# List all project tasks
# Create a new task for project PROJ-001
# Update task status for TASK-001
# Check task progress
# Get project summary

# # Sample Questions for CRM:
# List customer profiles
# Add a new customer profile
# Record a customer interaction
# Create a sales opportunity
# Check sales pipeline