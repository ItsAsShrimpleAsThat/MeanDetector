from openai import OpenAI

keyFile = open("api.key", "r") # open API key file.
apiKey = keyFile.read()

client = OpenAI(
  api_key=apiKey
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "test test test test"}
  ]
)

print(completion.choices[0].message.content);
