from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from interact_with_db import create_pgconnection, init_db, create_new_chat, insert_new_message, update_chat_name, retrieve_all_chats
from send_email import send_email
from image_generation import image_generation
import uuid

load_dotenv()

LLM = os.environ.get("MODEL")
conn = create_pgconnection()
init_db(conn)
client = OpenAI()

st.set_page_config(page_title="Chat Application")

col1, col2 = st.columns(2)  # Điều chỉnh tỷ lệ để giảm khoảng cách
# st.title(":blue[Nguyen Tuan Duc]")
with col1:
    image_path = os.path.join(os.path.dirname(__file__), "aifoundation.png")
    st.image(image_path, width=250)
with col2:
    st.title("""
        :blue[AI Foundation]
                Hi I'm AI foundation Chatbot
                How can I help you?
    """)

if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = [{'role': 'system', 'content': "You are an AI assistant and whenever it comes to sending email, you have to ask people to confirm content, and you just be able to send once at a time"}]
    st.session_state['chat_history'].append({'role': 'assistant', 'content': "Hello I'm Your virtual assistant. How can I help you?"})

if "chat_selected" not in st.session_state:
    st.session_state['chat_selected'] = None

if "all_chats" not in st.session_state:
    st.session_state['all_chats'] = retrieve_all_chats(conn)

# Apply custom CSS to style the sidebar
st.markdown(
    """
    <style>
        /* Change sidebar background color */
        [data-testid="stSidebar"] {
            background-color: #696969 !important; /* Blue */
        }

        /* Change all text color inside the sidebar */
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Specifically change sidebar title and subheader color */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2 {
            color: white !important;
        }

        /* Change all buttons background color */
        [data-testid="stButton"] button {
            background-color: 	#181818 !important; /* White background */
            color: white !important; /* Blue text */
            border-radius: 10px !important; /* Rounded corners */
            padding: 10px 20px !important; /* Adjust padding */
            font-size: 16px !important; /* Adjust font size */
        }
        
        [data-testid="stButton"] button p {
            color: white !important;  /* Ensure text inside button is blue */
        }
    </style>
    """,
    unsafe_allow_html=True
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to a given recipient with a subject and message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "receiver": {
                        "type": "string",
                        "description": "The recipient email address."
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line."
                    },
                    "body": {
                        "type": "string",
                        "description": "Body of the email message."
                    }
                },
                "required": [
                    "receiver",
                    "subject",
                    "body"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "image_generation",
            "description": "Generate a URL for an image based on the user's description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_description": {
                        "type": "string",
                        "description": "A detailed description of the image to generate."
                    }
                },
                "required": [
                    "image_description"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

# Sidebar content
with st.sidebar:
    st.title("AI Foundation")  # This will be white
    st.subheader("Chat history")  # This will also be white
    if st.button("*+* Create new Chat", key="new_chat_button"):
        new_chat_id = str(uuid.uuid4())
        first_message = "Hello I'm Your virtual assistant. How can I help you?"
        create_new_chat(conn, new_chat_id, "New chat", str(uuid.uuid4()), first_message,"assistant")
        st.session_state['chat_selected'] = new_chat_id
        st.session_state['chat_history'] = [{'role': 'system','content': "You are an AI assistant and whenever it comes to sending email, you have to ask people to confirm content every time, and you just be able to send once at a time"}]
        st.session_state['chat_history'].append({'role': 'assistant', 'content': "Hello I'm Your virtual assistant. How can I help you?"})
        st.session_state['all_chats'][new_chat_id] = {
            "name" : "New chat",
            "chat_history" : st.session_state['chat_history']
        }

    count_history_display = 0
    for chat_id in reversed(list(st.session_state["all_chats"].keys())):
        if count_history_display <= 7:
            count_history_display += 1
            chat_data = st.session_state["all_chats"][chat_id]
            button_label = chat_data["name"]
            if st.button(button_label, key=f"chat_button_{chat_id}"):
                st.session_state["chat_selected"] = chat_id
                st.session_state['chat_history'] = st.session_state['all_chats'][chat_id]["chat_history"]


if st.session_state['chat_selected']:
    chat_id = st.session_state['chat_selected']

    #display chat history
    for history in st.session_state['chat_history']:
        if isinstance(history, dict):
            if history['role'] == 'assistant':
                st.chat_message("ai").write(history['content'])
            if history['role'] == 'user':
                st.chat_message("human").write(history['content'])


    def call_task(name, args):
        if name == "image_generation":
            return image_generation(**args)
        if name == 'send_email':
            return send_email(**args)

    def ask_openai(messages):
        response = client.chat.completions.create(
            model=LLM,
            messages=messages,
            tools=tools,
            tool_choice='auto',
            # stream=stream
        )
        return response

    def append_to_chat_history(chat_session, prompt):
        import json
        st.session_state['chat_history'].append({"role": "user", "content": prompt})
        insert_new_message(conn, str(uuid.uuid4()), st.session_state['chat_selected'], "user", prompt)

        response = ask_openai(chat_session)
        message = response.choices[0].message
        if message.tool_calls and len(message.tool_calls) != 0:
            function = message.tool_calls[0].function
            function_name = function.name
            arguments = json.loads(function.arguments)
            tool_call_id = message.tool_calls[0].id
            result = call_task(function_name, arguments)
            supply_result_to_model = {
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call_id
            }
            try:
                st.session_state['chat_history'].append(message)
                st.session_state['chat_history'].append(supply_result_to_model)
            except Exception as e:
                st.write(f"An error occurrred: {e}")
            # insert_new_message(conn, str(uuid.uuid4()), st.session_state['chat_selected'], "tool", supply_result_to_model['content'])



    def ask_openai_stream(chat_history, stream = True):
        response = client.chat.completions.create(
            model=LLM,
            messages=chat_history,
            tools=tools,
            tool_choice='auto',
            stream=stream
        )

        return response

    def response_generator(chat_history):
        for chunk in ask_openai_stream(chat_history, stream=True):
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def run_application():
        prompt = st.chat_input("Message AI Foundation asisstant ...")
        chat_id = st.session_state['chat_selected']
        if prompt:
            update_chat_name(conn, chat_id, prompt)
            st.chat_message("human").write(prompt)
            append_to_chat_history(st.session_state['chat_history'], prompt)
            output = response_generator(st.session_state['chat_history'])
            with st.chat_message("ai"):
                ai_message = st.write_stream(output)

            st.session_state['chat_history'].append({'role': "assistant", "content": ai_message})
            insert_new_message(conn, str(uuid.uuid4()), st.session_state['chat_selected'], "assistant", ai_message)

    if __name__ == "__main__":
        run_application()

else:
    st.markdown(
        "<h3 style='text-align: center;'>CREATE NEW CHAT TO START CONVERSATION</h3>",
        unsafe_allow_html=True
)


