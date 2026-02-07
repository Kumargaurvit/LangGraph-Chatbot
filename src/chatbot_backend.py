from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated

# Defining the State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initializing LLM Model using Ollama
llm = ChatOllama(model="gpt-oss:20b-cloud")

# Function to add as a node in the graph
def chat_node(state: ChatState):
    """
    Function to take user query and send it to the llm to get a response
    """
    messages = state['messages']

    response = llm.invoke(messages).content

    return {'messages' : [response]}


# Creating a checkpointer to save the graph state in the memory
checkpointer = InMemorySaver()

# Creating the graph
graph = StateGraph(ChatState)

# Adding nodes to the graph
graph.add_node("chat_node", chat_node)

# Adding edges to the graph
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# Compiling the graph
chatbot = graph.compile(checkpointer=checkpointer)