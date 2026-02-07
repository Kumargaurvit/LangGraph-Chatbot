import streamlit as st
from langchain_core.messages import HumanMessage
from backend.chatbot_backend import chatbot
import uuid

############# PAGE CONFIG #############

st.set_page_config(page_title="LangGraph Chatbot")

############# UTILITY FUNCTIONS #############

def generate_thread_id():
    '''
    Function to generate a new thread id for different chat sessions
    '''
    thread_id = uuid.uuid4()

    return thread_id

def reset_chat():
    '''
    Function to Reset the Chat when the New Chat button is clicked
    '''
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    '''
    Function Add thread id to the chat thread store
    '''
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    '''
    Function to load conversation for a particular thread id
    '''
    THREAD_CONFIG = {'configurable' : {'thread_id' : thread_id}}
    conversation = chatbot.get_state(config=THREAD_CONFIG).values['messages']
    return conversation

############# SESSION SETUP #############

# Creating a message store to store chat history for that specific streamlit session
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# Creating a thread id store to store seperate threads for seperate chat sessions
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

# Creating a chat thread store to store all the threads
if "chat_thread" not in st.session_state:
    st.session_state["chat_thread"] = []

# Adding the thread id to the chat thread store
add_thread(st.session_state['thread_id'])

############# SIDEBAR UI #############
 
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.title("My Conversations")

# Displaying all the thread id as a button, 
# clicking any of the thread id button will restore the chat for the thread
for thread_id in st.session_state['chat_thread'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
        
            temp_messages.append({'role' : role, 'content' : message.content})
        
        st.session_state['message_history'] = temp_messages

############# CHAT UI #############

# Displaying the previous messages in the chat history
for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
        st.text(message['content'])

# Taking User Input
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