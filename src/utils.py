import uuid

def generate_thread_id():
    '''
    Function to generate a new thread id for different chat sessions
    '''
    thread_id = uuid.uuid4()

    return thread_id