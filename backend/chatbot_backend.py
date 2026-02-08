import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated
import sqlite3
import requests

# ------------ LOADING ENV VARIABLES ---------------

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY") 

# ------------ TOOLS SETUP ---------------

search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Performs basic arithmetic operation on two numbers.
    Supported operations: add, subtract, multiply, dividde

    Args: first_num: float, second_num: float, operation: str
    """

    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mult":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error" : "Division by zero"}
            result = first_num / second_num
        else:
            return {"error" : f"Unsupported Operation '{operation}"}

        return {'first_num' : first_num, 'second_num' : second_num, 'operation' : operation, 'result' : result}
    except Exception as e:
        return {'error' : str(e)}
    
@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetches the latest stock price for a given symbol (eg. GOOG, AAPL, TSLA)
    Uses Alpha Vantage to fetch the price data
    """
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"
    r = requests.get(url)
    stock_data = r.json()

    return stock_data
    
tools = [search_tool, calculator, get_stock_price]    

# Initializing LLM Model using Ollama
llm = ChatOllama(model="gpt-oss:20b-cloud")

# Binding llm with the created tools
llm_with_tools = llm.bind_tools(tools=tools)

# ------------ STATE & NODE SETUP ------------

# Defining the State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Function to add as a node in the graph
def chat_node(state: ChatState):
    """
    Function to take user query and send it to the llm to get a response
    """
    messages = state['messages']

    response = llm.invoke(messages)

    return {'messages' : [response]}

# Creating the tool node
tool_node = ToolNode(tools)

# ------------ SQLITE DATABASE ------------

conn = sqlite3.connect(database='backend/chat_db/chat_history.db', check_same_thread=False)

# ------------ GRAPH CREATION ------------

# Creating a checkpointer to save the graph state in the SQLite Database
checkpointer = SqliteSaver(conn=conn)

# Creating the graph
graph = StateGraph(ChatState)

# Adding nodes to the graph
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

# Adding edges to the graph
graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node", tools_condition)

graph.add_edge("tools", "chat_node")

# Compiling the graph
chatbot = graph.compile(checkpointer=checkpointer)