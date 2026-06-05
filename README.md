# AI_Travel_Planner_Agent_System
This project is a Real-World Multi-Agent AI System built using LangGraph.  
The system uses four AI agents that work together to plan a complete trip automatically.

------------------------------------------------------------------------------------
Features:

------------------------------------------------------------------------------------
✈️ Flight Search Agent

🏨 Hotel Search Agent

🗓️ Itinerary Planning Agent

🤖 Final Response Agent

🧠 Memory using SQLite

🌐 Real-time API Integration

💻 Streamlit Web Interface

----------------------------------------------------------------------------------------------
Tech Stack:

-----------------------------------------------------------------------------------------------
Python

LangGraph

LangChain

Groq

Llama 3.3 70B

SQLite

Streamlit

Tavily API

AviationStack API

---------------------------------------------------------------------------------------
Project Workflow:

----------------------------------------------------------------------------------------
Flight Agent searches flights

Hotel Agent searches hotels

Itinerary Agent creates travel plan

Final Agent combines everything together

SQLite stores conversation memory
______________________________________________________________________________________

Step 1: Create Python Environment
--------------------------------------------------------------------------------------
Open the terminal inside the project folder and run:

	python -m venv venv
Now activate the environment:

	venv\Scripts\activate
 --------------------------------------------------------------------------------- 
Step 2: Install Dependencies
-------------------------------------------------------------------------------------
Run the following command:

	pip install langgraph langchain langchain-openai langchain-groq langchain-community langchain-tavily python-dotenv tavily-python requests streamlit pip install langgraph langchain-groq sqlite3

------------------------------------------------------------------------------------------------------------

Step 3: Setup .env File
------------------------------------------------------------------------------------------------------------

Create a .env file inside the project folder.

Add the following keys:

GROQ_API_KEY=your_groq_api_key

TAVILY_API_KEY=your_tavily_api_key

AVIATIONSTACK_API_KEY=your_aviationstack_api_key


---------------------------------------------------------------------------------------------------------

Step 4: Get API Keys
---------------------------------------------------------------------------------------------------------
Get Groq API Key
https://console.groq.com

Get Tavily API Key
https://tavily.com

Get AviationStack API Key
https://aviationstack.com
--------------------------------------------------------------------------------------------------------
Step 5: Run the Application
----------------------------------------------------------------------------------------------------------
Run Streamlit Web App

	streamlit run frontend.py
This will launch the Multi-Agent AI web application.
