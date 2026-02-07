import streamlit as st
from langchain_core.messages import HumanMessage
from src.chatbot_backend import chatbot
from src.utils import *

############# PAGE CONFIG #############

st.set_page_config(page_title="LangGraph Chatbot")

############# SESSION SETUP #############

# Creating a message store to store chat history for that specific streamlit session
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# Displaying the previous messages in the chat history
for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
        st.text(message['content'])

# Creating a thread id store to store seperate threads for seperate chat sessions
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

############# SIDEBAR UI #############
 
st.sidebar.title("LangGraph Chatbot")

st.sidebar.button('New Chat')

st.sidebar.title("My Conversations")

st.sidebar.text(st.session_state['thread_id'])

############# CHAT UI #############

user_input = st.chat_input(placeholder='Ask Anything:')

if user_input:
    # Adding the user query to the message history store
    st.session_state['message_history'].append({'role' : 'user', 'content' : user_input})
    
    # Displaying the user query
    with st.chat_message("user"):
        st.text(user_input)

    # Creating a config to pass to the checkpointer
    CONFIG = {'configurable' : {'thread_id' : st.session_state['thread_id']}}

    # Streaming the output of the chatbot, rather than waiting for the response to generate and then print it as a whole
    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, _ in chatbot.stream(
                {'messages' : [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode = "messages"
            )
        )

        # Addding the chatbot response to the message history store
        st.session_state["message_history"].append({'role' : 'assistant', 'content' : ai_message})