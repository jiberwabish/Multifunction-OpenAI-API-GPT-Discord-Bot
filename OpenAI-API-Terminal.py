# jiberwabish 2024 - OpenAI API Chatbot - Terminal version 
# host on your own computer
# before running:
# 1 install missing packages - pip install openai tiktoken
# 2 enter your own api key below
# 3 modify the OpenAI variable if you wish to change your bots identity

import openai, time, tiktoken, os

openai.api_key = 'your key here'

#variable I use as a pre-prompt to provide the bot a personality
OpenAI = {"role": "system", "content": "You are a helpful and friendly chat bot. You are a programming expert of all programming languages. Respond to my message as effectively as you can. Use Markdown formatting and ensure code is in codeblocks."}
identity = OpenAI
history = [identity] #fill history with identity to start the conversation
costing = "placeholder"
model = "gpt-3.5-turbo-0125" #set gpt3 as default model
banner = f"\n\033[94mOpenAI\x1b[0m is now online in {model} mode.\n\x1b[90m💬 Ask something and press enter to chat.\n⌨️ !code - Enter Multi-line input mode. Good for providing code samples.\n🧠 !thanks -- Clear chat history\n🔁 !gpt3 or !gpt4 -- Model selection\n👋 !exit -- Quit\x1b[0m"

# Set up tokenizer
#declare global totals
modelTemp = 0.5
totalCost = 0
totalTokens = 0
model_max_tokens = 16000
num_tokens = 0
prompt_token_count = 0

os.system('cls')
#banner at the top of the terminal
print(banner)

def calculateCost():
    global totalCost
    global totalTokens
    global history
    global num_tokens
    global prompt_token_count
    #calculate cost
    if model == "gpt-4-0125-preview": #estimate without breaking out prompt and completion
        cost_per_token = 0.02 / 1000 # actual pricing is $0.01/1000 tokens input, $0.03/1000 tokens output
    elif model == "gpt-3.5-turbo-0125": #estimate without breaking out prompt and completion
        cost_per_token = 0.001 / 1000 # actual pricing is $0.0005/1000 tokens input, $0.0015/1000 tokens output
    totalTokens = num_tokens_from_messages(history) - 4
    totalCost = totalTokens * cost_per_token
    global costing
    costing = f"🪙 ${totalCost:.4f} - 🎟️ {totalTokens} - 🤖 {model}"

#calculating token numbers for token calculator
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
        number_tokens = 0
        for message in messages:
            number_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                number_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    number_tokens += -1  # role is always required and always 1 token
        number_tokens += 2  # every reply is primed with <im_start>assistant
        return number_tokens
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

def stream_openai(prompt,history):
    global num_tokens, prompt_token_count, model
    fullMessage = ""
    user_response_obj = {"role": "user", "content": prompt}

    history.append(user_response_obj)
    prompt_token_count = num_tokens_from_messages(history)
    
    #send the first message that will continually be editted
    response = openai.ChatCompletion.create(model=model, messages=history, stream=True, temperature=modelTemp, request_timeout=240)
    # Iterate over the response stream
    print("\n\033[94mOpenAI\033[0m ")
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta']
        if 'content' in chunk_message:
            print(chunk_message['content'], end='')
            fullMessage += chunk_message['content']
        elif chunk["choices"][0]["finish_reason"] != None:
            break
    history.append({"role": "assistant", "content": fullMessage})
    return fullMessage

def resetConvoHistory():
    global history, totalCost, totalTokens, identity
    history = [identity]
    return
    

# Main Loop
while True:
    user_input = input("\n\x1b[32mYou\x1b[0m \n")
    if user_input == '!thanks':
        resetConvoHistory()
        os.system("cls")
        print(banner)
        print(f"\n\x1b[90mConversation history cleared. -- Model: {model}\x1b[0m")
        continue
    elif user_input == '!code':
        user_input_lines = []
        print("\x1b[90mEnter or paste your message. Type 'eof' as the final line when you're done:\x1b[0m")
        while True:
            line = input()
            if line == "eof":
                break
            user_input_lines.append(line)
        # Joining the list of lines into a single string with newline characters
        user_input = "\n".join(user_input_lines)
        # Now you can call your function with the multi-line input
        response = stream_openai(user_input, history)
        calculateCost()
        print(f"\n\n\x1b[90m{costing} -- '!thanks' to start a new conversation.") 
    elif user_input == '!gpt3':
        model = "gpt-3.5-turbo-0125"
        print(f"\x1b[90mModel set to {model}.")
        continue
    elif user_input == '!gpt4':
        model = "gpt-4-0125-preview"
        print(f"\x1b[90mModel set to {model}.")
    elif user_input == "!exit":
        history.clear() #clears the array first
        print("\033[94mOpenAI:\x1b[0m See you later!")
        time.sleep(1)
        break
    else:    
        try:
            response = stream_openai(user_input,history)
            calculateCost()
            print(f"\n\n\x1b[90m{costing} -- '!thanks' to start a new conversation.")       
        except Exception as e:
            error = str(e)
            print(f'Shoot..Something went wrong or timed out. Error{error}')