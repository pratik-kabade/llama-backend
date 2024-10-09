import streamlit as st
import requests

# Initialize the chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Temporary variable to hold user input
if 'input' not in st.session_state:
    st.session_state['input'] = ""

# Function to call the API and get a response (streamed token by token)
def stream_response(user_input):
    try:
        with requests.post('http://localhost:5000/', json={'prompt': user_input}, stream=True) as response:
            response.raise_for_status()
            bot_response = ""
            for line in response.iter_lines():
                if line:
                    part = line.decode('utf-8')
                    bot_response += part  # Append each streamed part to the response
                    yield part  # Yield part to update in Streamlit
    except Exception as e:
        yield f"Error: {e}"

# Function to call the API and get the full response at once
def get_entire_response(user_input):
    try:
        response = requests.post('http://localhost:5000/api/get-response', json={'prompt': user_input})
        response.raise_for_status()
        return response.json().get('response', 'Error: No response from API')
    except Exception as e:
        return f"Error: {e}"

# Set up the chatbot interface
st.title("Chatbot")

# Display chat history
for message in st.session_state['messages']:
    if message['role'] == 'user':
        st.markdown(f"<div style='text-align: right; background-color: #f1f1f1; padding: 8px; border-radius: 5px;'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left; background-color: #d1e7dd; padding: 8px; border-radius: 5px;'>{message['content']}</div>", unsafe_allow_html=True)

# Input for user message
user_input = st.text_input("You:", value=st.session_state['input'], key="input")

# Radio buttons to select response type (streaming or entire response)
response_type = st.radio("Response Type:", ('Streamed', 'Entire Response'))

# When the 'Send' button is clicked
if st.button("Send"):
    if user_input:
        # Append user message
        st.session_state['messages'].append({"role": "user", "content": user_input})

        # Handle response type based on user selection
        if response_type == 'Streamed':
            # Create a placeholder for streaming output
            message_placeholder = st.empty()

            # Stream the response token by token
            bot_response = ""
            for part in stream_response(user_input):
                bot_response += part
                # Update the Streamlit placeholder with the current bot response
                message_placeholder.markdown(f"<div style='text-align: left; background-color: #d1e7dd; padding: 8px; border-radius: 5px;'>{bot_response}</div>", unsafe_allow_html=True)

            # Add the final bot response to the session state
            st.session_state['messages'].append({"role": "bot", "content": bot_response})

        else:
            # Get the entire response at once
            bot_response = get_entire_response(user_input)

            # Append the bot response to the session state
            st.session_state['messages'].append({"role": "bot", "content": bot_response})

        # Clear the input by using an intermediate variable
        st.session_state['input'] = ""  # This line is valid before the next rerun
        st.experimental_rerun()  # Rerun the script to refresh the input field and display new messages

