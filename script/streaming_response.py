from openai import OpenAI
from dotenv import load_dotenv
from openai.types.chat.chat_completion import ChatCompletion
import os

load_dotenv()

client = OpenAI()

LLM = os.environ.get("MODEL")


# print(f"response: {type(response)}")

# print(response.choices[0].message.content)

# temperature: control the response's stability (1.0 is the most stable answer and 2.0 is the most unpredictable answer)
# max_tokens
def ask_openai(user_question, temperature = 1.0, max_tokens = 256):
    response = client.chat.completions.create(
        model=LLM,
        messages=[
            {
                'role': "user",
                'content': user_question,
            }
        ],
        temperature = temperature,
        max_tokens = max_tokens,
        stream = True
    )

    return response

def make_conversation():
    # while True:
        # user_question = input("Message to my AI Assitant: ")
    user_question = 'Give me the way to comprehend insec skill in League of Legend with Leesin?'
    print('-----------------------------------------')
    response = ask_openai(user_question)
    print(response)
    for chunk in response:
        print(chunk)
        # chunk_message = chunk.choices[0].delta.content
        # print(chunk_message, end = "", flush=True)

if __name__ == '__main__':
   make_conversation()






