from typing import TypedDict, Annotated
import operator
import sqlite3
import re

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq
from dotenv import load_dotenv

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

load_dotenv()


# ======================
# CLEANER FUNCTION
# ======================

def clean_text(text: str) -> str:
    if not text:
        return ""

    # remove rupee symbol and other currencies if needed
    text = re.sub(r"[₹]", "", text)

    return text


# ======================
# LLM
# ======================

llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)


# ======================
# STATE
# ======================

class TravelState(TypedDict):

    messages: Annotated[
        list[AnyMessage],
        operator.add
    ]

    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


# ======================
# FLIGHT AGENT
# ======================

def flight_agent(state: TravelState):

    query = state["user_query"]

    flight_data = clean_text(search_flights(query))

    return {

        "flight_results": flight_data,

        "messages": [

            AIMessage(
                content="Flight results fetched"
            )

        ],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# ======================
# HOTEL AGENT
# ======================

def hotel_agent(state: TravelState):

    query = f"Best hotels for {state['user_query']}"

    hotel_results = clean_text(tavily_search(query))

    return {

        "hotel_results": hotel_results,

        "messages": [

            AIMessage(
                content="Hotel information fetched"
            )

        ],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# ======================
# ITINERARY AGENT
# ======================

def itinerary_agent(state: TravelState):

    prompt = f"""

Create travel itinerary.

User Query:
{state['user_query']}

Flights:
{state['flight_results']}

Hotels:
{state['hotel_results']}
"""

    response = llm.invoke([

        SystemMessage(
            content="You are expert travel planner"
        ),

        HumanMessage(
            content=prompt
        )

    ])

    return {

        "itinerary": clean_text(response.content),

        "messages": [response],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# ======================
# FINAL AGENT
# ======================

def final_agent(state: TravelState):

    prompt = f"""

Generate final travel response.

Flights:
{state['flight_results']}

Hotels:
{state['hotel_results']}

Itinerary:
{state['itinerary']}
"""

    response = llm.invoke([

        HumanMessage(content=prompt)

    ])

    return {

        "messages": [response],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# ======================
# GRAPH
# ======================

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


# ======================
# SQLITE CHECKPOINTER
# ======================

conn = sqlite3.connect(
    "travel_memory.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn)

app = graph.compile(checkpointer=checkpointer)


# ======================
# RUN
# ======================

if __name__ == "__main__":

    config = {
        "configurable": {
            "thread_id": "user_1"
        }
    }

    user_input = input("Enter travel request: ")

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    print("\nFINAL RESPONSE\n")

    for msg in result["messages"]:
        print(clean_text(msg.content))