import streamlit as st
from src.chatbot_backend import chatbot
from langchain_core.messages import HumanMessage

st.title("LangGraph Chatbot")

# Creating a config to pass to the checkpointer
CONFIG = {'configurable' : {'thread_id' : 'thread_1'}}

# Creating a message store to store chat history for that specific streamlit session
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input(placeholder='Ask Anything:')

if user_input:
    # Adding the user query to the message history store
    st.session_state['message_history'].append({'role' : 'user', 'content' : user_input})
    
    # Displaying the user query
    with st.chat_message("user"):
        st.text(user_input)

    # Invoking the chatbot workflow to generate a response
    response = chatbot.invoke({"messages" : [HumanMessage(content=user_input)]}, config=CONFIG)

    # Extracting only the answer from the response
    ai_response = response['messages'][-1].content

    # Adding the response to the message history store
    st.session_state['message_history'].append({'role' : 'assistant', 'content' : ai_response})

    # Displaying the Response
    with st.chat_message("assistant"):
        st.text(ai_response)