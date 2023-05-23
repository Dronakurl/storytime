import openai
import os

apikey = os.getenv("OPENAI_API_KEY")
if apikey is None:
    print("OPENAI_API_KEY not set")
    raise EnvironmentError("OPENAI_API_KEY not set")
openai.api_key = apikey

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell the world about the ChatGPT API in the style of a pirate."}],
)

print(completion.choices[0].message.content)
