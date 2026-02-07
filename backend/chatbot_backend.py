from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated
import sqlite3

# Defining the State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initializing LLM Model using Ollama
llm = ChatOllama(model="llama3.2")

# Function to add as a node in the graph
def chat_node(state: ChatState):
    """
    Function to take user query and send it to the llm to get a response
    """
    messages = state['messages']

    response = llm.invoke(messages)

    return {'messages' : [response]}

############# SQLite Database #############

conn = sqlite3.connect(database='backend/chat_db/chat_history.db', check_same_thread=False)

# Creating a checkpointer to save the graph state in the SQLite Database
checkpointer = SqliteSaver(conn=conn)

# Creating the graph
graph = StateGraph(ChatState)

# Adding nodes to the graph
graph.add_node("chat_node", chat_node)

# Adding edges to the graph
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# Compiling the graph
chatbot = graph.compile(checkpointer=checkpointer)