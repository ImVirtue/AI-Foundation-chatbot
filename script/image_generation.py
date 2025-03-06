from openai import OpenAI
import os
from dotenv import load_dotenv
import requests

load_dotenv()

client = OpenAI()
LLM = os.environ.get("MODEL")

def image_generation(image_description, size = "1024x1024"):
    print(f"LLM: {LLM}")
    response = client.images.generate(
        model = 'dall-e-3',
        prompt = image_description,
        size = size,
        quality = "hd"
    )

    image_url = response.data[0].url
    return image_url

if __name__ == '__main__':
    user_question = "Generate a image that has Leesin and Yasuo in League of Legend"

    response = image_generation((user_question))
    print(response)
