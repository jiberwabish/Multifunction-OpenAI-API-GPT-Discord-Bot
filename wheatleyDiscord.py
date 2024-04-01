# host on your own computer and private server and connect to your Discord bot with your Token
# fill in your own keys etc just below the imports
# Jiberwabish 2023

#so many libraries to import
import openai
from openai import OpenAI
import os
import tiktoken
import requests
import time
import emoji
import discord
from discord.ext import commands
from discord import Game, Activity, ActivityType, app_commands
import asyncio
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import json
from datetime import datetime
import logging
import base64
from PIL import Image, PngImagePlugin
from io import BytesIO
import io
import random
import socket
import subprocess
import sseclient
from better_profanity import profanity
from youtube_transcript_api import YouTubeTranscriptApi
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
# Import required libraries for comfy
import websocket # NOTE: websocket-client library from GitHub (https://github.com/websocket-client/websocket-client)
import uuid      # For generating unique client IDs
import json      # For JSON handling
import urllib.request  # For making HTTP requests
import urllib.parse    # For URL encoding
import google.generativeai as genai #gemini
from dotenv import load_dotenv


# Initialize the scheduler
scheduler = AsyncIOScheduler()

# Timezone
time_zone = timezone('America/Toronto')

#set api keys and other variabls
aiclient = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

discordBotToken = 'fill this in'
googleApiKey1 = "fill this in" #main
googleApiKey1Count = 0
googleApiKey = googleApiKey1
googleEngineID1 = "b48770d9232164d53"
googleEngineID = googleEngineID1
location = "Encino California"

#configure Gemini
genai.configure(api_key=googleApiKey)
text_generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 16000,
}
image_generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 16000,
}

text_model = genai.GenerativeModel(model_name="gemini-pro", generation_config=text_generation_config)#, safety_settings=safety_settings)

#variable I use as a pre-prompt to provide the bot a personality
#model temperature, 0 is more precise answers, 1 is more creative, and you can use decimals
modelTemp = float(0.7)
model = "gpt-3.5-turbo-0125"
lmStudioModel = "dagbs/dolphin-2.8-mistral-7b-v02-GGUF/dolphin-2.8-mistral-7b-v02.Q4_K_M.gguf"
#default comfy dimensions
w = 1024
h = 1024
#history is the conversation history array, this line immediately fills it with the bots identity
#then going forward it will keep track of what the users says and what the bots response is as well
#so it can carry on conversations
history = []
intentHistory = []
ghistory = []
costing = "placeholder"

# Set up tokenizer
#declare global totals
totalCost = 0
totalTokens = 0
prompt_token_count = 0
fullDate =""
imgGenNum = 0
cleanedBotSearchGen = ""

#setup !search variables
url1 = ""
url2 = ""
url3 = ""
url4 = ""

#!file variable
inputContent = ""
outputFile = "outputFile.txt"

#variables needed for comfyui image creation
img2imgPrompt = "watercolor style"
denoise = 0.4
image = ""
randomNum = random.randint(1000,9999)

#provide the year day and date so he's aware and then jam that into the history variable
def setSystemPrompt():
    global fullDate, location, identity, wheatley
    now = datetime.now()
    year = now.year
    month = now.strftime("%B")
    day = now.strftime("%A")
    dayOfMo = now.day
    time = now.strftime("%H:%M:%S")
    fullDate = str(year) + " " + str(month) + " " + str(dayOfMo) + " " + str(day) + " " + str(time)
    #user_date_obj = {"role": "system", "content": f"The Current Date is:{fullDate} Location is: {location}"}
    wheatley = {"role": "system", "content": f"Date: {fullDate} Location: {location}. You: You are a helpful and empathetic chat bot named Wheatley. I am your friend Steve. Please respond to my message as effectively as you can. Use emoji's in your response. Use codeblocks only when returning code and use Markdown format to improve readability of your responses."}
    #history.append(user_date_obj)
    #system_response_obj = identity        
    history.append(wheatley)
    identity = wheatley
    print(history)

#default identity, temp identity
#setSystemPrompt()
artist = {"role": "system", "content": "The user will describe what they would like a picture of and you will describe it how they want it. Feel free to embelish if there are missing details. Try to make each picture in a totally different style than the last. for example real life photography versus painting versus cartoon etc. Do not answer in proper sentences, instead just break your ideas up by commas"}


#banner at the top of the terminal after script is run
print("\x1b[36mWheatley\x1b[0m is now online in Discord.")

#calculating token numbers for token calculator
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    number_tokens = 0
    for message in messages:
        number_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            number_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                number_tokens += -1  # role is always required and always 1 token
    number_tokens += 2  # every reply is primed with <im_start>assistant
    return number_tokens
    
#tokenizer costing function
def calculateCost():
    global totalCost
    global totalTokens
    global history
    global prompt_token_count
    #calculate cost
    if (model == "gpt-3.5-turbo-0125"):
        cost_per_token = 0.0015 / 1000  # $0.0015 for turbo3.5 16k per 1000 tokens
    elif (model == "gpt-4-0125-preview"):
        cost_per_token = 0.003 / 1000  # $0.0015 for turbo3.5 16k per 1000 tokens
    elif (model == lmStudioModel or model == "Gemini"):
        cost_per_token = 0 / 1000  # $0.0015 for turbo3.5 16k per 1000 tokens
    elif (model == "open-mixtral-8x7b"):
        cost_per_token = 0.0007 / 1000  # $0.0015 for turbo3.5 16k per 1000 tokens
    totalTokens = num_tokens_from_messages(history) - 4
    totalCost = totalTokens * cost_per_token
    global costing
    costing = f"🪙 ${totalCost:.4f} -- 🎟️ Tokens {totalTokens}"

async def ask_gemini(message_text, history):
    history.append(message_text)
    print(f"Got textPrompt: {history}")
    response = text_model.generate_content(history)
    if(response._error):
        return "❌" +  str(response._error)
    print(response.text)
    return response.text

#function that takes the user input and sends it off to openai model specified
#and returns the bots response back to where it's called as the 'message' variable 
async def ask_openai(prompt, history):
    global num_tokens
    global prompt_token_count
    global model_max_tokens
    global model
    global aiclient
    # Generate user resp obj
    #system_response_obj = identity
    user_response_obj = {"role": "user", "content": prompt}
    #system_response_obj = identity        
    #history.append(system_response_obj)
    history.append(user_response_obj)
    
    prompt_token_count = num_tokens_from_messages(history)
    # Fire that dirty bastard into the abyss -NR
    #aiclient = OpenAI()
    response = aiclient.chat.completions.create(model=model, messages=history, temperature=modelTemp, stream=False)
    history.append({"role": "assistant", "content": response.choices[0].message.content})
    print(response)
    return str(response.choices[0].message.content)

async def ask_openai_intent(prompt, history):
    global num_tokens
    global prompt_token_count
    global model_max_tokens
    global model
    global intentHistory
    global aiclient
    # Generate user resp obj
    #system_response_obj = identity
    user_response_obj = {"role": "user", "content": prompt}
    #system_response_obj = identity        
    #history.append(system_response_obj)
    intentHistory.append(user_response_obj)
    #prompt_token_count = num_tokens_from_messages(intentHistory)
    # Fire that dirty bastard into the abyss -NR
    #aiclient = OpenAI()
    response = aiclient.chat.completions.create(model=model, messages=intentHistory, temperature=modelTemp, stream=False)
    intentHistory.append({"role": "assistant", "content": response.choices[0].message.content})
    print(f"Response from OpenAI: {response.choices[0].message.content}")
    return str(response.choices[0].message.content)

# streams AND will add a second message if nearing discord character limit per message
# but no support for a third message at this point
async def stream_openai_multi(prompt, history, channel):
    global num_tokens
    global prompt_token_count
    global model
    global model_max_tokens
    global aiclient
    newMessage = 0
    fullMessage = ""
    full_reply_content = ""
    second_reply_content = ""
    collected_messages = []
    # Generate user resp obj
    #system_response_obj = identity
    user_response_obj = {"role": "user", "content": prompt}

    #history.append(system_response_obj)
    history.append(user_response_obj)

    prompt_token_count = num_tokens_from_messages(history)
    #send the first message that will continually be editted
    if (model == "gpt-3.5-turbo-0125"):
        streamedMessage = await channel.send("🤔")   
    elif (model == lmStudioModel):
        streamedMessage = await channel.send("💭")
    elif (model == "gpt-4-0125-preview"):
        streamedMessage = await channel.send("🧠")

    #aiclient = OpenAI()
    response = aiclient.chat.completions.create(model=model, messages=history, temperature=modelTemp, stream=True)

    collected_messages = []
    second_collected_messages = []
    counter = 0
    current_message = ''
    #as long as there are messages comnig back from openai, do the for loop
    
    for data in response:
        for choice in data.choices:
            if choice.delta and choice.delta.content:
                content = choice.delta.content
                if content:
                    if newMessage == 0:
                        collected_messages.append(content)
                        full_reply_content = ''.join(collected_messages)
                        fullMessage = full_reply_content
                        counter += 1 # used to slow down how often chunks are actually printed/edited to discord
                    else: # we must be in the second message now so start adding chunks to the second message vars instead
                        second_collected_messages.append(content)
                        second_reply_content = ''.join(second_collected_messages)
                        counter += 1 # used to slow down how often chunks are actually printed/edited to discord
            
                if counter % 30 == 0: # when the number of chunks is divisible by 10 (so every 10) print to discord
                    if len(fullMessage) >= 1800:  # Check if message length is close to the Discord limit
                        if newMessage == 0: # if this is the first time it's been over...
                            await streamedMessage.edit(content=fullMessage) # complete the first message 
                            streamedMessage2 = await channel.send("...")  # create a blank message for the second message to stream into
                            newMessage = 1 # set the flag saying we're not onto the second message
                        else: # we must now be into the second message going forward now
                            await streamedMessage2.edit(content=second_reply_content) # update second message with the latest chunk
                        
                    else: # we are still in the first message so update first message normally
                        await streamedMessage.edit(content=full_reply_content)
                        # print(len(fullMessage)) # debug so I can watch when it's about to flip over
    if newMessage == 1: # at the very end of the loop, IF there was a second message, fully update it here
        await streamedMessage2.edit(content=second_reply_content)
    else: # second message wasn't needed, so make sure to add the last chunks to the first and only message
        await streamedMessage.edit(content=fullMessage)     
    combinedMessage = fullMessage + " " + second_reply_content# full reply content (first message) + second reply content, appended to eachother to keep our history variable in line
    history.append({"role": "assistant", "content": combinedMessage}) # add full message to history, whether there was one or two messages used
    newMessage = 0 # reset new message variable for next time
    print("got to end of stream function")
    return combinedMessage

#function used for scraping websites, used with the !search command
def get_first_500_words(url, numWords):
    def filter_noise(text):
        # This is a simple example. You can make it as complex as you like!
        noise_phrases = ['Buy Now', 'Advertisement', 'Sponsored', 'Copyright', 'All Rights Reserved']
        for phrase in noise_phrases:
            if phrase in text:
                return False
        return True

    # Set up logging mechanism
    #logging.basicConfig(filename='scraping.log', level=logging.ERROR)

    try:
        #gpt4's cleaner attempt at scraping
        # Set User-Agent and timeout
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        # Create BeautifulSoup object
        soup = BeautifulSoup(response.text, 'html.parser')

        # Step 1: Initial Scrubbing
        tags_to_scrape = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'div', 'span', 'article', 'section', 'meta']

        scraped_text = []

        for tag in tags_to_scrape:
            elements = soup.find_all(tag)
            for element in elements:
                scraped_text.append(element.text)
        
        # Step 2: Filter out noise
        filtered_text = [text for text in scraped_text if filter_noise(text)]

        # Convert to single string and split into words
        all_filtered_words = ' '.join(filtered_text).split()

        # Step 3: Word Count (limiting to 'numWords')
        first_n_words = all_filtered_words[:numWords]
        
        return ' '.join(first_n_words)
        # # Set User-Agent to avoid getting blocked by some websites
        # headers = {'User-Agent': 'Mozilla/5.0'}
        # # Set a timeout to avoid getting stuck on slow sites
        # response = requests.get(url, headers=headers, timeout=10)
        # # Specify the encoding to avoid decoding issues
        # response.encoding = 'utf-8'
        # soup = BeautifulSoup(response.text, 'html.parser')
        # text = soup.get_text()
        # words = text.split()
        # first_500_words = words[:numWords]
        # return ' '.join(first_500_words)
    except requests.exceptions.RequestException as e:
        # Log the error and include the URL that caused the error
        #logging.error(f"Error while scraping URL {url}: {str(e)}")
        return (f"Sorry, scraping {url} errored out.")

#summarize a single url
async def summarize(url,channel):
    scrapedSummaryUrl = get_first_500_words(url,13000)
    try:
        await stream_openai_multi(f"""
            IDENTITY and PURPOSE
            You are an expert content summarizer. You take content in and output a Markdown formatted summary using the format below.

            Take a deep breath and think step by step about how to best accomplish this goal using the following steps.

            OUTPUT SECTIONS
            Combine all of your understanding of the content into a summary paragraph in a section called SUMMARY:.

            Output the 10 most important points of the content as a list with no more than 15 words per point into a section called MAIN POINTS:.

            Output a list of the 5 best takeaways from the content in a section called TAKEAWAYS:.

            OUTPUT INSTRUCTIONS
            Create the output using the formatting above.
            You only output human readable Markdown.
            Output numbered lists, not bullets.
            Do not output warnings or notes—just the requested sections.
            Do not repeat items in the output sections.
            Do not start items with the same opening words.
            
            INPUT: {scrapedSummaryUrl}
            """,history,channel)    
    except Exception as e:
        error_message = str(e)
        print(e)
        await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
        return
    return

#googling function, asks bot to create a search term using the users prompt, then searches google
#for that, pulls the top 3 results, scrapes the first 500 words of those three sites
#feeds all that data back into a prompt to gpt to answer the original question based on the scraped results
async def deepGoogle(query,channel):
    global url1, url2, prompt_token_count, cleanedBotSearchGen, url3
    
    usersQuestion = query
    try:
        # botSearchGen = ask_openai(f"I would like to search Google for {usersQuestion}. Please generate a useful and effective search query and reply ONLY with that updated query. Don't use emoji's here. Remember, answer ONLY with the query that will be sent to Google.",history)
        botSearchGen = await ask_openai(f"You have just been asked the following question: {usersQuestion}. Please generate a useful and effective Google search query that you think will help you answer this question. Reply ONLY with the Google search query. Don't use emoji's here. If you want to use quotes, make sure to put a backslash before the first one. Remember, answer ONLY with the query that will be sent to Google.",history)
    except Exception as e:
        error_message = str(e)
        print(e)
        return(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}")

    service = build("customsearch", "v1", developerKey=googleApiKey)
    if botSearchGen.startswith('"') and botSearchGen.endswith('"'):
        cleanedBotSearchGen = botSearchGen.strip('"')
    else:
        cleanedBotSearchGen = botSearchGen
    print(f"Searching for {cleanedBotSearchGen}")
    await yellowMessage(f"Search string: {cleanedBotSearchGen}",channel)
    result = service.cse().list(
        q=cleanedBotSearchGen,
        cx=googleEngineID
    ).execute()
    print("Processing URLs...")
    try:
        url1 = result['items'][0]['link']
        url2 = result['items'][1]['link']
        url3 = result['items'][2]['link']        
    except (TypeError, KeyError):
        print("No URLs found, try rewording your search.")
        await redMessage("No URLs found.",channel)
        return
    
    print("Scraping...")
    #scrape these results with beautiful soup.. mmmm
    scraped1 = get_first_500_words(url1,1000)
    scraped2 = get_first_500_words(url2,1000)
    scraped3 = get_first_500_words(url3,1000)
    #put them all in one variable
    allScraped = (scraped1 or "") + " " + (scraped2 or "") + " " + (scraped3 or "")

    #prepare results for bot
    user_search_obj = {"role": "user", "content": allScraped}
    #we save it to a variable and feed it back to the bot to give us the search results in a more natural manner
    history.append(user_search_obj)
    #clear var for next time
    allScraped = ""
       
    #print(searchReply)
    print(f"{url1} \n{url2} \n{url3}") 
    #print(searchReply)
    try:
        botReply = await stream_openai_multi(f"You now have a wealth of information on the topic of my question. I will include it below.  Answer my question based on that information if possible. Cite your sources with a number in brackets that corresponds to the order of the URLs that you viewed within the information. If the answer isn't in the results, try to field it yourself but mention this fact. DO use emojis. KEEP YOUR RESPONSE SUCCINCT AND TO THE POINT. My question: {query}",history, channel)
        await yellowMessage(f"1.{url1}\n2.{url2}\n3.{url3}",channel)
        return(botReply)
    except Exception as e:
        error_message = str(e)
        print(e)
        await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
        return
    
#multi google
async def multiGoogle(search1, search2, search3, question, channel):
    #turn search terms into an array for easy looping
    searches = [search1, search2, search3]
    #google search1
    service = build("customsearch", "v1", developerKey=googleApiKey)
    allURLs=[]
    scrapeMessage = await tealMessage("Reading results...🔍💻📄",channel)
    for item in searches:
        result = service.cse().list(
            q=item,
            cx=googleEngineID
        ).execute()
        print(f"Processing URLs... for {item}")
        
        try:
            url1 = result['items'][0]['link']
            url2 = result['items'][1]['link']
            url3 = result['items'][2]['link']
            allURLs.append(url1)
            allURLs.append(url2)
            #allURLs.append(url3) 
        except (TypeError, KeyError):
            print("No URLs found, try rewording your search.")
            await redMessage("No URLs found.",channel)
            return
    
        print("Scraping...")
        #scrape these results with beautiful soup.. mmmm
        scraped1 = get_first_500_words(url1,500)
        scraped2 = get_first_500_words(url2,500)
        scraped3 = get_first_500_words(url3,500)
        #put them all in one variable
        allScraped = (f"\nURL:{url1} -- {scraped1}" or "") + " " + (f"\nURL:{url2} -- {scraped2}" or "") + " " + (scraped3 or "")

        #prepare results for bot
        user_search_obj = {"role": "user", "content": allScraped}
        #we save it to a variable and feed it back to the bot to give us the search results in a more natural manner
        history.append(user_search_obj)
        #clear var for next time
        allScraped = ""
    
    await scrapeMessage.delete()
    #print(searchReply)
    #print(f"{url1} \n{url2} \n{url3}") 
    #print(searchReply)
    formattedURLs = ""
    try:
        botReply = await stream_openai_multi(f"You now have a wealth of information on the topic of my question: ```{question}```. Given the information you have, please answer the question. DO use emojis. KEEP YOUR RESPONSE SUCCINCT AND TO THE POINT.",history, channel)
        #clean up sources
        for url in allURLs:
            formattedURLs += f"🔗 {url}\n"
        await yellowMessage(f"Sources:\n{formattedURLs}",channel)

        return(botReply)
    except Exception as e:
        error_message = str(e)
        print(e)
        await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
        return
    
async def silentMultiGoogle(search1, search2, search3, question, channel):
    #turn search terms into an array for easy looping
    searches = [search1, search2, search3]
    #google search1
    # program in api switcher here

    service = build("customsearch", "v1", developerKey=googleApiKey)
    allURLs=[]
    scrapeMessage = await tealMessage("Researching...🔍🌎📄",channel)
    for item in searches:
        result = service.cse().list(
            q=item,
            cx=googleEngineID
        ).execute()
        print(f"Processing URLs... for {item}")
        
        try:
            url1 = result['items'][0]['link']
            url2 = result['items'][1]['link']
            url3 = result['items'][2]['link']
            allURLs.append(url1)
            allURLs.append(url2)
            #allURLs.append(url3) 
        except (TypeError, KeyError):
            print("No URLs found, try rewording your search.")
            await redMessage("No URLs found.",channel)
            return
    
        print("Scraping...")
        #scrape these results with beautiful soup.. mmmm
        scraped1 = get_first_500_words(url1,500)
        scraped2 = get_first_500_words(url2,500)
        scraped3 = get_first_500_words(url3,500)
        #put them all in one variable
        allScraped = (f"\nURL:{url1} -- {scraped1}" or "") + " " + (f"\nURL:{url2} -- {scraped2}" or "") + " " + (scraped3 or "")

        #prepare results for bot
        user_search_obj = {"role": "user", "content": allScraped}
        #we save it to a variable and feed it back to the bot to give us the search results in a more natural manner
        history.append(user_search_obj)
        #clear var for next time
        allScraped = ""
    
    await scrapeMessage.delete()
    #print(searchReply)
    #print(f"{url1} \n{url2} \n{url3}") 
    #print(searchReply)
    formattedURLs = ""
    try:
        botReply = await stream_openai_multi(f"You now have a wealth of information on the topic of my question: ```{question}```. Given the information you have, please answer the question. DO use emojis. KEEP YOUR RESPONSE SUCCINCT AND TO THE POINT. Provide the URL of the most relevant website you used.",history, channel)
        #clean up sources
        for url in allURLs:
            formattedURLs += f"🔗 {url}\n"
        #await yellowMessage(f"Sources:\n{formattedURLs}",channel)

        return(botReply)
    except Exception as e:
        error_message = str(e)
        print(e)
        await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
        return

async def multiGoogleDump(search1, search2, question, channel):
    #turn search terms into an array for easy looping
    searches = [search1, search2]#, search3]
    #google search1
    service = build("customsearch", "v1", developerKey=googleApiKey)
    allURLs=[]
    allScraped = ""
    scrapeMessage = await tealMessage("Reading results...🔍💻📄",channel)
    for item in searches:
        result = service.cse().list(
            q=item,
            cx=googleEngineID
        ).execute()
        print(f"Processing URLs... for {item}")
        
        try:
            url1 = result['items'][0]['link']
            url2 = result['items'][1]['link']
            #url3 = result['items'][2]['link']
            allURLs.append(url1)
            allURLs.append(url2)
            #allURLs.append(url3) 
        except (TypeError, KeyError):
            print("No URLs found, try rewording your search.")
            await redMessage("No URLs found.",channel)
            return
    
        print("Scraping...")
        #scrape these results with beautiful soup.. mmmm
        scraped1 = get_first_500_words(url1,500)
        scraped2 = get_first_500_words(url2,500)
        #scraped3 = get_first_500_words(url3,500)
        #put them all in one variable
        allScraped += (f"\nURL:{url1} -- {scraped1}" or "") + " " + (f"\nURL:{url2} -- {scraped2}" or "")# + " " + (scraped3 or "") 

    
    await scrapeMessage.delete()
        
    # output all of history array to a text file
    with open('history.txt', 'w') as f:
        f.write(f"The user has asked the question: ```{question}```.\nI have scraped some search results pertaining to the question that should answer the question.\nPlease use only the information provided below to answer the question. If the results are irrelevant, say so, and answer it yourself if you know the answer please.\nScraped data:\n ```{allScraped}```")

    
    
    
    # return the text file to the discord chat as an attachment
    await channel.send(f"Here's what I found!\nSave the file and paste it into my bud, ChatGPT4, for analysis.\n Here are the URLS I used:")
    await channel.send(file=discord.File('history.txt'))
    resetConvoHistory()  
    # Collect all URLs into a single string.
    all_urls_string = "\n".join([f"🔗 {url}" for url in allURLs])
    # Send a single yellow message containing all URLs.
    await yellowMessage(all_urls_string, channel)   
    
    return

#resets conversation history back to just identity and date -- to save on tokens when user says !thanks
def resetConvoHistory():
    global history, totalCost, totalTokens, identity, imgGenNum
    history = []
    intentHistory = []
    setSystemPrompt()
    print(f"History reset to: {str(history)}")
    totalCost = 0
    totalTokens = 0
    imgGenNum = 0
    return
#used to see if my comfyui computer is up and running
def is_port_listening(ip_address, port):
    try:
        s = socket.create_connection((ip_address, port), timeout=1)
        s.close()
        return True
    except ConnectionRefusedError:
        return False
    except socket.timeout:
        return False
    
#---DISCORD SECTION---#
# create a Discord client object with the necessary intents
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)

#message functions to easily print in color boxes
async def blueMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.dark_blue()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message
async def yellowMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.yellow()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message
async def goldMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.dark_gold()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message
async def redMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.red()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message
async def greenMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.dark_green()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message
async def purpleMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.purple()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message
async def blurpleMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.blurple()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message
async def pinkMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.magenta()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message
async def tealMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.dark_teal()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message

# function to generate 1 picture from comfyui
async def comfy(description,channel,model,w,h,num):
    server_address = "192.168.64.123:8188"
    client_id = str(uuid.uuid4())
    randomSeed = random.randint(1,10000000)

    if is_port_listening("192.168.64.123","8188") == True:
        await yellowMessage(f"Painting... 🖌🎨\n",channel) 
        # Generate a unique client ID using UUID
        client_id = str(uuid.uuid4())

        # Function to queue a prompt for execution
        def queue_prompt(prompt):
            # Prepare the data to send in the request body
            p = {"prompt": prompt, "client_id": client_id}
            data = json.dumps(p).encode('utf-8')
            
            # Make an HTTP request to queue the prompt
            req =  urllib.request.Request(f"http://{server_address}/prompt", data=data)
            return json.loads(urllib.request.urlopen(req).read())

        # Function to fetch an image
        def get_image(filename, subfolder, folder_type):
            # Prepare the query parameters
            data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
            url_values = urllib.parse.urlencode(data)
            
            # Make an HTTP request to fetch the image
            with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
                return response.read()

        # Function to fetch the history of a prompt
        def get_history(prompt_id):
            # Make an HTTP request to fetch the history
            with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
                return json.loads(response.read())

        # Function to fetch images after a prompt has been executed
        def get_images(ws, prompt):
            # Queue the prompt and get its ID
            prompt_id = queue_prompt(prompt)['prompt_id']
            output_images = {}
            
            # Keep listening on the websocket
            while True:
                out = ws.recv()
                
                # Check the type of message received
                if isinstance(out, str):
                    message = json.loads(out)
                    
                    # Check if the prompt is still executing
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            break  # Execution is done
                else:
                    continue  # Previews are binary data

            # Fetch the history for this prompt
            history = get_history(prompt_id)[prompt_id]
            
            # Iterate over the outputs to fetch images
            for o in history['outputs']:
                for node_id in history['outputs']:
                    node_output = history['outputs'][node_id]
                    if 'images' in node_output:
                        images_output = []
                        for image in node_output['images']:
                            image_data = get_image(image['filename'], image['subfolder'], image['type'])
                            images_output.append(image_data)
                        output_images[node_id] = images_output

            return output_images

        # Define the prompt to execute

        prompt_text = """
        {
            "1": {
                "inputs": {
                "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                "text": "A cute cup of tea sitting on a wooden table on the porch of a cozy house in the country",
                "clip": [
                    "1",
                    1
                ]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                "text": "city, sky scrapers, industry",
                "clip": [
                    "1",
                    1
                ]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                "seed": 620853316359786,
                "steps": 20,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": [
                    "1",
                    0
                ],
                "positive": [
                    "2",
                    0
                ],
                "negative": [
                    "3",
                    0
                ],
                "latent_image": [
                    "5",
                    0
                ]
                },
                "class_type": "KSampler"
            },
            "5": {
                "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                "samples": [
                    "4",
                    0
                ],
                "vae": [
                    "1",
                    2
                ]
                },
                "class_type": "VAEDecode"
            },
            "7": {
                "inputs": {
                "images": [
                    "6",
                    0
                ]
                },
                "class_type": "PreviewImage"
            }
            
        }
        """

        prompt = json.loads(prompt_text)
        #set the text prompt for our positive CLIPTextEncode
        prompt["2"]["inputs"]["text"] = description

        #set the seed for our KSampler node
        prompt["4"]["inputs"]["seed"] = randomSeed
        prompt["5"]["inputs"]["width"] = w
        prompt["5"]["inputs"]["height"] = h
        prompt["5"]["inputs"]["batch_size"] = num
        prompt["1"]["inputs"]["ckpt_name"] = model

        print("ws://{}/ws?clientId={}".format(server_address, client_id))
        # Connect to the websocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

        # Fetch the images
        images = get_images(ws, prompt)

        #Code to display the output images (commented out)
        for node_id in images:
            run = 0
            for image_data in images[node_id]:
                image = Image.open(io.BytesIO(image_data))
                image.save(f"ComfyImages/comfy_{randomSeed}-{run}.jpg")
                discordImage = discord.File(f"ComfyImages/comfy_{randomSeed}-{run}.jpg", filename=f'image{randomSeed}-{run}.jpg')
                discembed = discord.Embed()
                discembed.set_image(url=f"attachment://image{randomSeed}-{run}.jpg")
                await channel.send(file=discordImage, embed=discembed)
                run += 1
        #debug
        #await channel.send("Done!")
        return
        
    else:
        await redMessage("Sorry, ComfyUI isn't running right now.",channel)
        return
async def comfyRefined(description,batch,channel,w,h):
    server_address = "192.168.64.123:8188"
    client_id = str(uuid.uuid4())
    randomSeed = random.randint(1,10000000)

    if is_port_listening("192.168.64.123","8188") == True: 
        # Generate a unique client ID using UUID
        client_id = str(uuid.uuid4())

        # Function to queue a prompt for execution
        def queue_prompt(prompt):
            # Prepare the data to send in the request body
            p = {"prompt": prompt, "client_id": client_id}
            data = json.dumps(p).encode('utf-8')
            
            # Make an HTTP request to queue the prompt
            req =  urllib.request.Request(f"http://{server_address}/prompt", data=data)
            return json.loads(urllib.request.urlopen(req).read())

        # Function to fetch an image
        def get_image(filename, subfolder, folder_type):
            # Prepare the query parameters
            data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
            url_values = urllib.parse.urlencode(data)
            
            # Make an HTTP request to fetch the image
            with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
                return response.read()

        # Function to fetch the history of a prompt
        def get_history(prompt_id):
            # Make an HTTP request to fetch the history
            with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
                return json.loads(response.read())

        # Function to fetch images after a prompt has been executed
        def get_images(ws, prompt):
            # Queue the prompt and get its ID
            prompt_id = queue_prompt(prompt)['prompt_id']
            output_images = {}
            
            # Keep listening on the websocket
            while True:
                out = ws.recv()
                
                # Check the type of message received
                if isinstance(out, str):
                    message = json.loads(out)
                    
                    # Check if the prompt is still executing
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            break  # Execution is done
                else:
                    continue  # Previews are binary data

            # Fetch the history for this prompt
            history = get_history(prompt_id)[prompt_id]
            
            # Iterate over the outputs to fetch images
            for o in history['outputs']:
                for node_id in history['outputs']:
                    node_output = history['outputs'][node_id]
                    if 'images' in node_output:
                        images_output = []
                        for image in node_output['images']:
                            image_data = get_image(image['filename'], image['subfolder'], image['type'])
                            images_output.append(image_data)
                        output_images[node_id] = images_output

            return output_images

        # Define the prompt to execute

        prompt_text = """
        {
            "4": {
                "inputs": {
                "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                "text": "Misty mountains",
                "clip": [
                    "4",
                    1
                ]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                "text": "",
                "clip": [
                    "4",
                    1
                ]
                },
                "class_type": "CLIPTextEncode"
            },
            "10": {
                "inputs": {
                "add_noise": "enable",
                "noise_seed": 73365373102413,
                "steps": 25,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "normal",
                "start_at_step": 0,
                "end_at_step": 20,
                "return_with_leftover_noise": "enable",
                "model": [
                    "4",
                    0
                ],
                "positive": [
                    "6",
                    0
                ],
                "negative": [
                    "7",
                    0
                ],
                "latent_image": [
                    "5",
                    0
                ]
                },
                "class_type": "KSamplerAdvanced"
            },
            "11": {
                "inputs": {
                "add_noise": "disable",
                "noise_seed": 0,
                "steps": 25,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "normal",
                "start_at_step": 20,
                "end_at_step": 10000,
                "return_with_leftover_noise": "disable",
                "model": [
                    "12",
                    0
                ],
                "positive": [
                    "15",
                    0
                ],
                "negative": [
                    "16",
                    0
                ],
                "latent_image": [
                    "10",
                    0
                ]
                },
                "class_type": "KSamplerAdvanced"
            },
            "12": {
                "inputs": {
                "ckpt_name": "sd_xl_refiner_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "15": {
                "inputs": {
                "text": "Misty mountains",
                "clip": [
                    "12",
                    1
                ]
                },
                "class_type": "CLIPTextEncode"
            },
            "16": {
                "inputs": {
                "text": "",
                "clip": [
                    "12",
                    1
                ]
                },
                "class_type": "CLIPTextEncode"
            },
            "17": {
                "inputs": {
                "samples": [
                    "11",
                    0
                ],
                "vae": [
                    "12",
                    2
                ]
                },
                "class_type": "VAEDecode"
            },
            "50": {
                "inputs": {
                "images": [
                    "17",
                    0
                ]
                },
                "class_type": "PreviewImage"
            }
            }
        """

        prompt = json.loads(prompt_text)
        #set the text prompt for our positive CLIPTextEncode
        prompt["6"]["inputs"]["text"] = description

        #set the seed for our KSampler node
        prompt["10"]["inputs"]["noise_seed"] = randomSeed
        prompt["11"]["inputs"]["noise_seed"] = randomSeed
        prompt["5"]["inputs"]["batch_size"] = batch
        prompt["5"]["inputs"]["width"] = w
        prompt["5"]["inputs"]["height"] = h

        print("ws://{}/ws?clientId={}".format(server_address, client_id))
        # Connect to the websocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

        # Fetch the images
        images = get_images(ws, prompt)

        #Code to display the output images (commented out)
        for node_id in images:
            for image_data in images[node_id]:
                image = Image.open(io.BytesIO(image_data))
                image.save(f"ComfyImages/comfy_{randomSeed}.jpg")
                discordImage = discord.File(f"ComfyImages/comfy_{randomSeed}.jpg", filename='image1.jpg')
                discembed = discord.Embed()
                discembed.set_image(url="attachment://image1.jpg")
                await channel.send(file=discordImage, embed=discembed)
        return
    else:
        await redMessage("Sorry, ComfyUI isn't running right now.",channel)
        return

async def comfyCascade(description,batch,channel,w,h):
    server_address = "192.168.64.123:8188"
    client_id = str(uuid.uuid4())
    randomSeed = random.randint(1,10000000)

    if is_port_listening("192.168.64.123","8188") == True: 
        # Generate a unique client ID using UUID
        client_id = str(uuid.uuid4())

        # Function to queue a prompt for execution
        def queue_prompt(prompt):
            print('inside queue prompt')
            # Prepare the data to send in the request body
            p = {"prompt": prompt, "client_id": client_id}
            print('set p variable')
            data = json.dumps(p).encode('utf-8')
            print('data is set')
            
            # Make an HTTP request to queue the prompt
            req =  urllib.request.Request(f"http://{server_address}/prompt", data=data)
            print('req is set')
            print(f"returning {json.loads(urllib.request.urlopen(req).read())}")
            return json.loads(urllib.request.urlopen(req).read())

        # Function to fetch an image
        def get_image(filename, subfolder, folder_type):
            # Prepare the query parameters
            data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
            url_values = urllib.parse.urlencode(data)
            
            # Make an HTTP request to fetch the image
            with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
                return response.read()

        # Function to fetch the history of a prompt
        def get_history(prompt_id):
            # Make an HTTP request to fetch the history
            with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
                return json.loads(response.read())

        # Function to fetch images after a prompt has been executed
        def get_images(ws, prompt):
            # Queue the prompt and get its ID
            print("inside get_images")
            prompt_id = queue_prompt(prompt)['prompt_id']
            print("setup prompt id")
            output_images = {}
            print("setup output_images")
            
            # Keep listening on the websocket
            while True:
                out = ws.recv()
                
                # Check the type of message received
                if isinstance(out, str):
                    message = json.loads(out)
                    
                    # Check if the prompt is still executing
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            break  # Execution is done
                else:
                    continue  # Previews are binary data

            # Fetch the history for this prompt
            history = get_history(prompt_id)[prompt_id]
            
            # Iterate over the outputs to fetch images
            for o in history['outputs']:
                for node_id in history['outputs']:
                    node_output = history['outputs'][node_id]
                    if 'images' in node_output:
                        images_output = []
                        for image in node_output['images']:
                            image_data = get_image(image['filename'], image['subfolder'], image['type'])
                            images_output.append(image_data)
                        output_images[node_id] = images_output

            return output_images

        # Define the prompt to execute

        prompt_text = """
        {
            "3": {
                "inputs": {
                "seed": 314307448448003,
                "steps": 20,
                "cfg": 4,
                "sampler_name": "euler_ancestral",
                "scheduler": "simple",
                "denoise": 1,
                "model": [
                    "41",
                    0
                ],
                "positive": [
                    "6",
                    0
                ],
                "negative": [
                    "7",
                    0
                ],
                "latent_image": [
                    "34",
                    0
                ]
                },
                "class_type": "KSampler",
                "_meta": {
                "title": "KSampler"
                }
            },
            "6": {
                "inputs": {
                "text": "evening sunset scenery blue sky nature, glass bottle with a fizzy ice cold freezing rainbow liquid in it",
                "clip": [
                    "41",
                    1
                ]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                "title": "CLIP Text Encode (Positive Prompt)"
                }
            },
            "7": {
                "inputs": {
                "text": "",
                "clip": [
                    "41",
                    1
                ]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                "title": "CLIP Text Encode (Negative Prompt)"
                }
            },
            "8": {
                "inputs": {
                "samples": [
                    "33",
                    0
                ],
                "vae": [
                    "42",
                    2
                ]
                },
                "class_type": "VAEDecode",
                "_meta": {
                "title": "VAE Decode"
                }
            },
            "9": {
                "inputs": {
                "filename_prefix": "ComfyUI",
                "images": [
                    "8",
                    0
                ]
                },
                "class_type": "SaveImage",
                "_meta": {
                "title": "Save Image"
                }
            },
            "33": {
                "inputs": {
                "seed": 183495397600639,
                "steps": 10,
                "cfg": 1.1,
                "sampler_name": "euler_ancestral",
                "scheduler": "simple",
                "denoise": 1,
                "model": [
                    "42",
                    0
                ],
                "positive": [
                    "36",
                    0
                ],
                "negative": [
                    "7",
                    0
                ],
                "latent_image": [
                    "34",
                    1
                ]
                },
                "class_type": "KSampler",
                "_meta": {
                "title": "KSampler"
                }
            },
            "34": {
                "inputs": {
                "width": 1024,
                "height": 1024,
                "compression": 42,
                "batch_size": 1
                },
                "class_type": "StableCascade_EmptyLatentImage",
                "_meta": {
                "title": "StableCascade_EmptyLatentImage"
                }
            },
            "36": {
                "inputs": {
                "conditioning": [
                    "6",
                    0
                ],
                "stage_c": [
                    "3",
                    0
                ]
                },
                "class_type": "StableCascade_StageB_Conditioning",
                "_meta": {
                "title": "StableCascade_StageB_Conditioning"
                }
            },
            "41": {
                "inputs": {
                "ckpt_name": "stable_cascade_stage_c.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {
                "title": "Load Checkpoint"
                }
            },
            "42": {
                "inputs": {
                "ckpt_name": "stable_cascade_stage_b.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {
                "title": "Load Checkpoint"
                }
            }
            }
        """

        prompt = json.loads(prompt_text)
        #set the text prompt for our positive CLIPTextEncode

        prompt = json.loads(prompt_text)
        #set the text prompt for our positive CLIPTextEncode
        prompt["6"]["inputs"]["text"] = description

        #set the seed for our KSampler node
        prompt["3"]["inputs"]["seed"] = randomSeed
        prompt["33"]["inputs"]["seed"] = randomSeed
        prompt["34"]["inputs"]["batch_size"] = batch
        prompt["34"]["inputs"]["width"] = w
        prompt["34"]["inputs"]["height"] = h
        
        print("ws://{}/ws?clientId={}".format(server_address, client_id))
        # Connect to the websocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
        print("setup ws.connect")
        # Fetch the images
        images = get_images(ws, prompt)
        #Code to display the output images (commented out)
        for node_id in images:
            for image_data in images[node_id]:
                image = Image.open(io.BytesIO(image_data))
                image.save(f"ComfyImages/comfy_{randomSeed}.jpg")
                discordImage = discord.File(f"ComfyImages/comfy_{randomSeed}.jpg", filename='image1.jpg')
                discembed = discord.Embed()
                discembed.set_image(url="attachment://image1.jpg")
                await channel.send(file=discordImage, embed=discembed)
        return
    else:
        await redMessage("Sorry, ComfyUI isn't running right now.",channel)
        return

async def comfyUpscale(pic,channel):
    server_address = "192.168.64.123:8188"
    client_id = str(uuid.uuid4())
    randomSeed = random.randint(1,10000000)

    if is_port_listening("192.168.64.123","8188") == True:
        await yellowMessage(f"Upscaling attached image 4x🖌🎨\n",channel) 
        # Generate a unique client ID using UUID
        client_id = str(uuid.uuid4())

        # Function to queue a prompt for execution
        def queue_prompt(prompt):
            # Prepare the data to send in the request body
            p = {"prompt": prompt, "client_id": client_id}
            data = json.dumps(p).encode('utf-8')
            
            # Make an HTTP request to queue the prompt
            req =  urllib.request.Request(f"http://{server_address}/prompt", data=data)
            return json.loads(urllib.request.urlopen(req).read())

        # Function to fetch an image
        def get_image(filename, subfolder, folder_type):
            # Prepare the query parameters
            data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
            url_values = urllib.parse.urlencode(data)
            
            # Make an HTTP request to fetch the image
            with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
                return response.read()

        # Function to fetch the history of a prompt
        def get_history(prompt_id):
            # Make an HTTP request to fetch the history
            with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
                return json.loads(response.read())

        # Function to fetch images after a prompt has been executed
        def get_images(ws, prompt):
            # Queue the prompt and get its ID
            prompt_id = queue_prompt(prompt)['prompt_id']
            output_images = {}
            
            # Keep listening on the websocket
            while True:
                out = ws.recv()
                
                # Check the type of message received
                if isinstance(out, str):
                    message = json.loads(out)
                    
                    # Check if the prompt is still executing
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            break  # Execution is done
                else:
                    continue  # Previews are binary data

            # Fetch the history for this prompt
            history = get_history(prompt_id)[prompt_id]
            
            # Iterate over the outputs to fetch images
            for o in history['outputs']:
                for node_id in history['outputs']:
                    node_output = history['outputs'][node_id]
                    if 'images' in node_output:
                        images_output = []
                        for image in node_output['images']:
                            image_data = get_image(image['filename'], image['subfolder'], image['type'])
                            images_output.append(image_data)
                        output_images[node_id] = images_output

            return output_images

        # Define the prompt to execute

        prompt_text = """
        {
            "14": {
                "inputs": {
                "model_name": "4x-UltraSharp.pth"
                },
                "class_type": "UpscaleModelLoader"
            },
            "15": {
                "inputs": {
                "upscale_model": [
                    "14",
                    0
                ],
                "image": [
                    "19",
                    0
                ]
                },
                "class_type": "ImageUpscaleWithModel"
            },
            "19": {
                "inputs": {
                "image": ""
                },
                "class_type": "ETN_LoadImageBase64"
            },
            "21": {
                "inputs": {
                "images": [
                    "15",
                    0
                ]
                },
                "class_type": "PreviewImage"
            }
        }
        """

        prompt = json.loads(prompt_text)
        prompt["19"]["inputs"]["image"] = pic

        print("ws://{}/ws?clientId={}".format(server_address, client_id))
        # Connect to the websocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

        # Fetch the images
        images = get_images(ws, prompt)

        #Code to display the output images (commented out)
        for node_id in images:
            run = 0
            for image_data in images[node_id]:
                image = Image.open(io.BytesIO(image_data))
                image.save(f"ComfyImages/comfy_{randomSeed}-{run}.jpg")
                discordImage = discord.File(f"ComfyImages/comfy_{randomSeed}-{run}.jpg", filename=f'image{randomSeed}-{run}.jpg')
                discembed = discord.Embed()
                discembed.set_image(url=f"attachment://image{randomSeed}-{run}.jpg")
                await channel.send(file=discordImage, embed=discembed)
                run += 1
        #debug
        #await channel.send("Done!")
        return
        
    else:
        await redMessage("Sorry, ComfyUI isn't running right now.",channel)
        return
async def img2img(description,channel,pic,model,denoise):
    server_address = "192.168.64.123:8188"
    client_id = str(uuid.uuid4())
    randomSeed = random.randint(1,10000000)

    if is_port_listening("192.168.64.123","8188") == True:
        await yellowMessage(f"Painting {img2imgPrompt} at a denoise of {denoise} 🖌🎨\n",channel) 
        # Generate a unique client ID using UUID
        client_id = str(uuid.uuid4())

        # Function to queue a prompt for execution
        def queue_prompt(prompt):
            # Prepare the data to send in the request body
            p = {"prompt": prompt, "client_id": client_id}
            data = json.dumps(p).encode('utf-8')
            
            # Make an HTTP request to queue the prompt
            req =  urllib.request.Request(f"http://{server_address}/prompt", data=data)
            return json.loads(urllib.request.urlopen(req).read())

        # Function to fetch an image
        def get_image(filename, subfolder, folder_type):
            # Prepare the query parameters
            data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
            url_values = urllib.parse.urlencode(data)
            
            # Make an HTTP request to fetch the image
            with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
                return response.read()

        # Function to fetch the history of a prompt
        def get_history(prompt_id):
            # Make an HTTP request to fetch the history
            with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
                return json.loads(response.read())

        # Function to fetch images after a prompt has been executed
        def get_images(ws, prompt):
            # Queue the prompt and get its ID
            prompt_id = queue_prompt(prompt)['prompt_id']
            output_images = {}
            
            # Keep listening on the websocket
            while True:
                out = ws.recv()
                
                # Check the type of message received
                if isinstance(out, str):
                    message = json.loads(out)
                    
                    # Check if the prompt is still executing
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            break  # Execution is done
                else:
                    continue  # Previews are binary data

            # Fetch the history for this prompt
            history = get_history(prompt_id)[prompt_id]
            
            # Iterate over the outputs to fetch images
            for o in history['outputs']:
                for node_id in history['outputs']:
                    node_output = history['outputs'][node_id]
                    if 'images' in node_output:
                        images_output = []
                        for image in node_output['images']:
                            image_data = get_image(image['filename'], image['subfolder'], image['type'])
                            images_output.append(image_data)
                        output_images[node_id] = images_output

            return output_images

        # Define the prompt to execute

        prompt_text = """
        {
            "1": {
                "inputs": {
                "ckpt_name": "photon_v1.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                "text": "mortal combat character",
                "clip": [
                    "1",
                    1
                ]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                "text": "",
                "clip": [
                    "1",
                    1
                ]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                "seed": 935332783805433,
                "steps": 20,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 0.7099999999999997,
                "model": [
                    "1",
                    0
                ],
                "positive": [
                    "10",
                    0
                ],
                "negative": [
                    "3",
                    0
                ],
                "latent_image": [
                    "7",
                    0
                ]
                },
                "class_type": "KSampler"
            },
            "5": {
                "inputs": {
                "samples": [
                    "4",
                    0
                ],
                "vae": [
                    "1",
                    2
                ]
                },
                "class_type": "VAEDecode"
            },
            "7": {
                "inputs": {
                "pixels": [
                    "9",
                    0
                ],
                "vae": [
                    "1",
                    2
                ]
                },
                "class_type": "VAEEncode"
            },
            "8": {
                "inputs": {
                "images": [
                    "5",
                    0
                ]
                },
                "class_type": "PreviewImage"
            },
            "9": {
                "inputs": {
                "image": ""
                },
                "class_type": "ETN_LoadImageBase64"
            },
            "10": {
                "inputs": {
                "strength": 1,
                "conditioning": [
                    "2",
                    0
                ],
                "control_net": [
                    "11",
                    0
                ],
                "image": [
                    "9",
                    0
                ]
                },
                "class_type": "ControlNetApply"
            },
            "11": {
                "inputs": {
                "control_net_name": "control_sd15_canny.pth"
                },
                "class_type": "ControlNetLoader"
            }
        }
        """

        prompt = json.loads(prompt_text)
        #set the text prompt for our positive CLIPTextEncode
        prompt["1"]["inputs"]["ckpt_name"] = model
        prompt["2"]["inputs"]["text"] = description
        #set the seed for our KSampler node
        prompt["4"]["inputs"]["seed"] = randomSeed
        prompt["4"]["inputs"]["denoise"] = denoise
        #prompt["5"]["inputs"]["width"] = w
        #prompt["5"]["inputs"]["height"] = h
        #prompt["5"]["inputs"]["batch_size"] = num
        prompt["9"]["inputs"]["image"] = pic

        print("ws://{}/ws?clientId={}".format(server_address, client_id))
        # Connect to the websocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

        # Fetch the images
        images = get_images(ws, prompt)

        #Code to display the output images (commented out)
        for node_id in images:
            run = 0
            for image_data in images[node_id]:
                image = Image.open(io.BytesIO(image_data))
                image.save(f"ComfyImages/comfy_{randomSeed}-{run}.jpg")
                discordImage = discord.File(f"ComfyImages/comfy_{randomSeed}-{run}.jpg", filename=f'image{randomSeed}-{run}.jpg')
                discembed = discord.Embed()
                discembed.set_image(url=f"attachment://image{randomSeed}-{run}.jpg")
                await channel.send(file=discordImage, embed=discembed)
                run += 1
        #debug
        #await channel.send("Done!")
        return
        
    else:
        await redMessage("Sorry, ComfyUI isn't running right now.",channel)
        return

#function to create and return a prompt for use with stable diffusion or dall e
async def promptCreation(prompt,channel):
    try:
        #discordResponse = await ask_openai(f"*{prompt}* is the concept.  Please provide a concise description of the subject for an AI image generator. Include context, perspective, and point of view. Use specific nouns and verbs to make the description lively. Describe the environment in a concise manner, considering the desired tone and mood. Use sensory terms and specific details to bring the scene to life. Describe the mood of the scene using language that conveys the desired emotions and atmosphere. Describe the atmosphere using descriptive adjectives and adverbs, considering the overall tone and mood. Describe the lighting effect, including types, styles, and impact on mood and atmosphere. Use specific adjectives and adverbs to portray the desired lighting effect. Avoid cliches, excess words, and repetitive descriptions. Use figurative language sparingly and include a variety of words. The description should not exceed 300 words. Do not provide preamble or conclusion, simply reply with the requested info only. Do not include emojis",history)
        discordResponse = await ask_openai(f"*{prompt}* is the concept. Please describe this as if you were describing it to an artist. In your own words, separating your ideas by commas instead of describing them conversationally, describe the art piece. start with the main subject(s), any actions that may be happening, describe where the image takes place including foreground and background, and end with the style of the image. Do not use proper sentences, just your describing words separate by commas. make the style completely different than any other you may have made thus far unless told otherwise. remember, don't use sentences, break your thoughts up by commas and that's it. do NOT use emojis",history)
        return(discordResponse)
    except Exception as e:
        error_message = str(e)
        print(e)
        await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
        return

#button testing -- this worked but broke everything else, so I don't know the order of @bot.event and @client.event
#was using this youtube video: https://www.youtube.com/watch?v=82d9s8D6XE4
# bot = commands.Bot(command_prefix='/', intents = discord.Intents.all())
# @bot.event
# async def on_ready():
#     print("bot is online")
# class Menu(discord.ui.View):
#     def __init__(self):
#         super().__init__()
#         self.value = None

#     @discord.ui.button(label="New Convo", style=discord.ButtonStyle.grey)
#     async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.send_message("hello you button clicker")

# @bot.command()
# async def menu(ctx):
#     view = Menu()
#     await ctx.reply(view=view)

# bot.run(discordBotToken)

# set wheatleys mode to Local LLM, 3.5 or 4
async def setModeLLM():
    if is_port_listening("192.168.64.123","1234") == True: # check for running lm-studio
        global aiclient
        aiclient = OpenAI(base_url="http://192.168.64.123:1234/v1", api_key="lm-studio")
        global model_max_tokens
        model_max_tokens = 16000
        global model
        model = lmStudioModel
        system_response_obj = identity        
        history.append(system_response_obj)
        channel = await client.fetch_channel(1079243349237698633)
        await pinkMessage("GPU powered Local LLM - Activated",channel)
    else: #lm studio isn't running
        channel = await client.fetch_channel(1079243349237698633)
        await redMessage("Apologies. Local Language Model is not currently available.",channel)

async def setModeGPT35():
    global aiclient
    aiclient = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    global model_max_tokens
    model_max_tokens = 4096
    global model
    model = "gpt-3.5-turbo-0125"
    system_response_obj = identity        
    history.append(system_response_obj)
    channel = await client.fetch_channel(1079243349237698633)
    await blueMessage("Open AI GPT 3.5 Turbo Model - Activated",channel)

async def setModeGPT4():
    global aiclient
    aiclient = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    global model_max_tokens
    model_max_tokens = 16000
    global model
    model = "gpt-4-0125-preview"
    system_response_obj = identity        
    history.append(system_response_obj)
    channel = await client.fetch_channel(1079243349237698633)
    await yellowMessage("Open AI GPT 4 Turbo Model - Activated",channel)

async def setModeGemini():
    global model
    model = "Gemini"
    system_response_obj = identity        
    history.append(system_response_obj)
    channel = await client.fetch_channel(1079243349237698633)
    await blurpleMessage("Gemini Pro Model - Activated",channel)

async def setModeMistral():
    global model_max_tokens
    model_max_tokens = 16000
    global model
    model = "open-mixtral-8x7b"
    system_response_obj = identity        
    history.append(system_response_obj)
    channel = await client.fetch_channel(1079243349237698633)
    await yellowMessage("Mixtral-8x7b - Activated",channel)


@client.event
async def on_ready():
    global modelTemp
    global w
    global h
    #change this to the channel id where you want reminders to pop up
    main_channel_id = 1079243349237698633
    main_channel_id_object = await client.fetch_channel(main_channel_id)
    reminder_channel_id = 1090120937472540903
    print('Logged in as {0.user}'.format(client))
    print('Setting Date...')
    setSystemPrompt()
    
    #system_response_obj = identity        
    #history.append(system_response_obj)

    #greeting!
    await redMessage("Good day to you. If you want to see what I can do, just type !help\n",main_channel_id_object)
    
    # set 3.5turbo as default
    await setModeGPT35()
    
@client.event
async def on_message(message):
    global identity
    global history
    global intentHistory
    global ghistory
    global totalCost
    global totalTokens
    global pictureTokens
    global imgGenNum
    global inputContent
    global outputFile
    global image
    global img2imgPrompt
    global modelTemp
    global denoise
    global w
    global h
    
    #set name (and soon to be picture) to Wheatley by default
    userName = message.author
    mention = userName.mention
    userMessage = message.content

    # this is the main loop of the program, continuously loops through this section calling functions as
    # the user specifies
    # ignore messages sent by the bot itself to avoid infinite loops
    if message.author == client.user or message.author.id == 1171980563834490890 or message.author.id == 1203744066278400010 : #vega and phi
        return
    #resets conversation history
    elif '!thanks' in message.content:
        member=message.guild.me
        #await member.edit(nick='Wheatley')
        resetConvoHistory()
        if (model == "Gemini"):
            channel =  message.channel
            resetConvoHistory()
            await channel.send("History cleared.")
        else:
            resetConvoHistory()
            await stream_openai_multi("Thank you Wheatley.", history, message.channel)
            resetConvoHistory()
        # identity = wheatley
        #await blueMessage("OK. What's next?",message.channel)
        calculateCost()
        await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
        return
    
    elif '!reset' in message.content:
        member=message.guild.me
        #await member.edit(nick='Wheatley')
        #clear chat history except for starting prompt
        resetConvoHistory()
        # identity = wheatley
        await blueMessage("History Cleared.",message.channel)
        calculateCost()
        await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
        return
    
    elif '!temp' in message.content:
        proposedTemp = float(message.content[5:])
        await yellowMessage(f"Current model temperature is {modelTemp}.\nProposed model temp is {proposedTemp}",message.channel)
        
        if proposedTemp >= 0 and proposedTemp<= 1:
            modelTemp = proposedTemp
            await tealMessage(f"Model temperature set to {modelTemp}.",message.channel)
        else:
            await redMessage(f"{proposedTemp} is out of range. Please select a value from 0-1.",message.channel)
        return

    elif "!rez" in message.content:
        _, resolution = message.content[2:].split()
        w, h = map(int, resolution.split('x'))
        await yellowMessage(f"Image generation resolution set to {w}x{h}.",message.channel)
        return

    #searches top 3 google results and returns answer to the question after the !search
    elif '!1search' in message.content:
        #wipe history as this could get big
        resetConvoHistory()
        channel = message.channel
        #send loading bar message
        try:
            await deepGoogle(message.content[7:],channel)
            #await yellowMessage(f"Searched for: {cleanedBotSearchGen}",message.channel) #this is done in the function now
            #await blueMessage(f"{searchReply}",message.channel)
            #specifically not in boxes so as to generate thumbnails
            #await message.channel.send(f"{url1} \n{url2} \n{url3}")
            #removing thumbnails for cleaner interface
            calculateCost()
            await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
            #search uses so many tokens now, replying would create an error unless you use !16k flag so just to be safe, wiping history by default
            resetConvoHistory() 
            return
        except Exception as e:
            error_message = str(e)
            print(e)            
            await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
            return        

    elif '!search' in message.content:
        #wipe history as this could get big
        resetConvoHistory()
        channel = message.channel
        question = message.content[7:]
        try:
            searchTerms = await ask_openai(f"Come up with 3 different web searches that you think would help you answer this question :```{question}``` Reply with ONLY the search terms, prepended by 1., 2. then 3. Do not use emojis or explain them.",history)
            #strip quotes
            searchTerms = searchTerms.replace('"', '')
            #await yellowMessage(f"Searching:\n{searchTerms}.",channel)
            #split the search terms into three separate variables
            splitSearch=searchTerms.split("\n")
            search1=splitSearch[0]
            search2=splitSearch[1]
            search3=splitSearch[2]
            await silentMultiGoogle(search1, search2, search3, question, channel)
            calculateCost()
            await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
            #search uses so many tokens now, replying would create an error unless you use !16k flag so just to be safe, wiping history by default
            #resetConvoHistory() 
            return
        except Exception as e:
            error_message = str(e)
            print(e)            
            await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
            return
    elif '!freesearch' in message.content:
        #wipe history as this could get big
        resetConvoHistory()
        channel = message.channel
        question = message.content[12:]
        try:
            searchTerms = await ask_openai(f"Come up with 2 different web searches that you think would help you answer this question :```{question}``` Reply with ONLY the search terms, prepended by 1. and 2. Do not use emojis or explain them.",history)
            #strip quotes
            searchTerms = searchTerms.replace('"', '')
            await yellowMessage(f"Searching:\n{searchTerms}.",channel)
            #split the search terms into three separate variables
            splitSearch=searchTerms.split("\n")
            search1=splitSearch[0]
            search2=splitSearch[1]
            #search3=splitSearch[2]
            await multiGoogleDump(search1, search2, question, channel)
            #resetConvoHistory()  this is already handled in the function
            return
        except Exception as e:
            error_message = str(e)
            print(e)            
            await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
            return   
   
    #summarize article OR now Youtube transcript
    elif message.content.startswith('http') or message.content.startswith('www'):
        resetConvoHistory()
        vidID = ""        
        try:
            if 'youtube.com' in message.content:
                try:
                    vidID = message.content.split('=')[1]
                    print(f"Video ID: {vidID}")
                    transcript = YouTubeTranscriptApi.get_transcript(vidID)
                except Exception as e:
                    error_message = str(e)
                    print(e)
                    await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}", message.channel)
                    return
                justText = ' '.join(line['text'] for line in transcript)
                await stream_openai_multi(f"""
                    IDENTITY and PURPOSE
                    You are an expert content summarizer. You take content in and output a Markdown formatted summary using the format below.

                    Take a deep breath and think step by step about how to best accomplish this goal using the following steps.

                    OUTPUT SECTIONS
                    Combine all of your understanding of the content into a summary paragraph in a section called SUMMARY:.

                    Output the 10 most important points of the content as a list with no more than 15 words per point into a section called MAIN POINTS:.

                    Output a list of the 5 best takeaways from the content in a section called TAKEAWAYS:.

                    OUTPUT INSTRUCTIONS
                    Create the output using the formatting above.
                    You only output human readable Markdown.
                    Output numbered lists, not bullets.
                    Do not output warnings or notes—just the requested sections.
                    Do not repeat items in the output sections.
                    Do not start items with the same opening words.
                    
                    INPUT:  {justText}
                    """,history,message.channel)                              
                calculateCost()
                await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
                #no longer wiping history afterward, this way you can talk to the video and ask follow up questions
                #resetConvoHistory()  # Wiping history for efficiency
                return
                
            elif 'youtu.be' in message.content:
                try:
                    vidID = message.content.split('be/')[1]
                    print(f"Video ID: {vidID}")
                    transcript = YouTubeTranscriptApi.get_transcript(vidID)
                except Exception as e:
                    error_message = str(e)
                    print(e)
                    await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}", message.channel)
                    return
                justText = ' '.join(line['text'] for line in transcript)
                await stream_openai_16k_multi(f"""
                    IDENTITY and PURPOSE
                    You are an expert content summarizer. You take content in and output a Markdown formatted summary using the format below.

                    Take a deep breath and think step by step about how to best accomplish this goal using the following steps.

                    OUTPUT SECTIONS
                    Combine all of your understanding of the content into a summary paragraph in a section called SUMMARY:.

                    Output the 10 most important points of the content as a list with no more than 15 words per point into a section called MAIN POINTS:.

                    Output a list of the 5 best takeaways from the content in a section called TAKEAWAYS:.

                    OUTPUT INSTRUCTIONS
                    Create the output using the formatting above.
                    You only output human readable Markdown.
                    Output numbered lists, not bullets.
                    Do not output warnings or notes—just the requested sections.
                    Do not repeat items in the output sections.
                    Do not start items with the same opening words.
                    
                    INPUT:  {justText}
                    """,history,message.channel) 
                calculateCost()
                await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
                #no longer wiping history afterward, this way you can talk to the article and ask follow up questions
                #resetConvoHistory()  # Wiping history for efficiency
                return
            else :
                url = message.content.split()[0]
                await summarize(url, message.channel)            
                calculateCost()
                await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
                #no longer wiping history afterward, this way you can talk to the article and ask follow up questions
                #resetConvoHistory()  # Wiping history for efficiency
                return
        except Exception as e:
            error_message = str(e)
            print(e)            
            await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}", message.channel)
            return
    
    # create an image generation prompt out of whatever you write, to then be used with dall e or stable diffusion or whatever
    elif '!prompt' in message.content:
        channel = message.channel
        resetConvoHistory()
        discordResponse = await promptCreation(message.content[7:],channel)
        await blueMessage(discordResponse,channel)
        calculateCost()
        await goldMessage(costing,channel)
        resetConvoHistory()
        return
    # image creation from your own local stable diffusion box, you need to have set that up first
    elif '!unrefinedimagine' in message.content:
        channel = message.channel
        await comfy(message.content[17:],channel,"sd_xl_base_1.0.safetensors",1024,1024,1)
        return
    elif '!fastimagine' in message.content:
        channel = message.channel
        await comfy(message.content[13:],channel,"photon_v1.safetensors",512,512,4)
        return
    elif '!imagine' in message.content:
        channel = message.channel
        await yellowMessage(f"Painting 4 {w}x{h} images... 🖌🎨\nPlease wait for all of them⌛",channel)
        await comfyRefined(message.content[8:],4,channel,w,h)
        return
    elif '!superimagine' in message.content:
        channel = message.channel
        #modelTemp = 1
        resetConvoHistory()
        member=message.guild.me
        await member.edit(nick='Wheatley with a fancy beret.')
        identity = artist
        await yellowMessage("👩‍🎨Designing the artwork.",channel)
        promptForImagine = await promptCreation(message.content[14:],channel)
        promptForImagine2 = await promptCreation(message.content[14:],channel)
        promptForImagine3 = await promptCreation(message.content[14:],channel)
        promptForImagine4 = await promptCreation(message.content[14:],channel)
        await yellowMessage(f"Painting 4 {w}x{h} images... 🖌🎨\nPlease wait for all of them⌛\n(about 12 seconds per picture⏲️)",channel)
        await comfyRefined(promptForImagine,1,channel,w,h)
        await comfyRefined(promptForImagine2,1,channel,w,h)
        await comfyRefined(promptForImagine3,1,channel,w,h)
        await comfyRefined(promptForImagine4,1,channel,w,h)
        #print(f"History: {str(history)}")
        resetConvoHistory()
        # identity = wheatley
        member=message.guild.me
        await member.edit(nick='Wheatley')
        return
    #bot ignores what's entered completly
    elif '!ignore' in message.content or '!vega' in message.content:
        print("Ignoring input.")
        #await blueMessage("I didn't see nuthin'")
        return
    #process the prompt in an attached txt file and respond in kind
    elif '!style' in message.content:
        img2imgPrompt = message.content[6:]
        await yellowMessage(f"img2img prompt set to '{img2imgPrompt}'.\nNow attach a picture and say !img2img to process it.",message.channel)
        return
    elif '!denoise' in message.content:
        denoise = message.content[8:]
        await yellowMessage(f"img2img denoise set to '{denoise}'.\nNow attach a picture to process it.",message.channel)
        return
    #processes attachments, either text or image, however image isn't working yet
    elif len(message.attachments) == 1 and '!upscale' in message.content:
        inputFile = message.attachments[0]
        for attachment in message.attachments:
            # save image locally to server
            with open("ComfyImages/imgToProcess.jpg", "wb") as f:
                f.write(await attachment.read())
            
            # Open the image using PIL
            pilimage = Image.open('ComfyImages/imgToProcess.jpg')
            if pilimage.mode == 'RGBA':
                # Convert it to RGB
                pilimage = pilimage.convert('RGB')
            pic = pilimage

            # Convert PIL Image to base64
            image_io = BytesIO()
            pic.save(image_io, format='JPEG')
            image_base64 = base64.b64encode(image_io.getvalue()).decode('utf-8')

            # Now pass this base64 string to your function
            await comfyUpscale(image_base64,message.channel)
        return 
    elif len(message.attachments) == 1 and '!img2img' in message.content:

        # await redMessage("img2img not implemented yet", message.channel)
        # return
        for attachment in message.attachments:
            # save image locally to server
            with open("ComfyImages/imgToProcess.jpg", "wb") as f:
                f.write(await attachment.read())
            
            # Open the image using PIL
            pilimage = Image.open('ComfyImages/imgToProcess.jpg')
            
            # Get the dimensions
            width, height = pilimage.size
            
            # Calculate new dimensions
            if width > height:
                new_width = 768
                new_height = int((new_width / width) * height)
            else:
                new_height = 768
                new_width = int((new_height / height) * width)
            
            # Resize the image
            resized_image = pilimage.resize((new_width, new_height), Image.ANTIALIAS)
            
            # Save the resized image
            resized_image.save('ComfyImages/imgToProcess_resized.jpg')
            pic = Image.open('ComfyImages/imgToProcess_resized.jpg')

            # Convert PIL Image to base64
            image_io = BytesIO()
            pic.save(image_io, format='JPEG')
            image_base64 = base64.b64encode(image_io.getvalue()).decode('utf-8')

            # Now pass this base64 string to your function
            await img2img(img2imgPrompt, message.channel, image_base64, "photon_v1.safetensors", denoise)
        return   
    elif len(message.attachments) == 1:
        #get the attached file and read it
        inputFile = message.attachments[0]
        print("Reading File")
        if inputFile.filename.endswith('.txt'):
            print("Processing File...")
            inputContent = await inputFile.read()
            inputContent = inputContent.decode('utf-8')
            #so inputContent is the message to be openai-ified
            try:
                bot_message = await message.channel.send("📑")
                discordResponse = await ask_openai(inputContent,history)
                await bot_message.delete()
                with open(outputFile, "w") as responseFile:
                    responseFile.write(discordResponse)
                await message.channel.send(file=discord.File(outputFile))
                await blueMessage("Please see my response in the attached file.",message.channel)
                calculateCost()
                await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
            except Exception as e:
                error_message = str(e)
                print(e)
                await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",message.channel)
            return
        #img2img use with comfy
    
    # these local commands are specific to my ubuntu box, may not work for you
    # runs a local speedtest if you have speedtest cli installed, these
    elif '!speedtest' in message.content:
        bot_message = await yellowMessage("Speedtesting in progress... 📶⏱️🔥",message.channel)
        speedtest_output = subprocess.check_output(['speedtest'])
        await tealMessage(speedtest_output.decode(),message.channel)
        return
    #runs a nmap scan of the network this bot is on, change to your own ip subnet
    elif '!network' in message.content:
        bot_message = await yellowMessage("Network scan activated... 🛰️🔎📶📡",message.channel)
        nmap_output = subprocess.check_output(['nmap', '-sn', '192.168.64.0/24', '| grep'])
        await tealMessage(nmap_output.decode(),message.channel)
        return
    # shows cpu load percentage and temps of the computer this is running on
    elif '!cpu' in message.content:
        cpu_output = subprocess.check_output("mpstat 1 1 | awk '/Average:/ {print 100 - $NF}'", shell=True)
        # CPU temperature
        cpu_temp1 = subprocess.check_output("sensors |grep 'Core 0' | cut -c16-19", shell=True).decode('utf-8').strip()
        cpu_temp2 = subprocess.check_output("sensors |grep 'Core 1' | cut -c16-19", shell=True).decode('utf-8').strip()
        cpu_temp3 = subprocess.check_output("sensors |grep 'Core 2' | cut -c16-19", shell=True).decode('utf-8').strip()
        cpu_temp4 = subprocess.check_output("sensors |grep 'Core 3' | cut -c16-19", shell=True).decode('utf-8').strip()
        
        # GPU temperature
        gpu_temp = subprocess.check_output("nvidia-smi --query-gpu=temperature.gpu --format=csv | awk 'NR==2'", shell=True).decode('utf-8').strip()
        
        bot_message = (f"💻Percent total usage: {cpu_output.decode()}\n🌡️ CPU Temperature:\n {cpu_temp1}°C -- {cpu_temp2}°C,\n {cpu_temp3}°C -- {cpu_temp4}°C\n\n🎮 GPU Temperature: {gpu_temp} °C")
        await tealMessage(bot_message,message.channel)
        return
    elif '!braintrust' in message.content:
        try:
            #craft a prompt to have wheatley provide a braintrust of advisors given the question asked
            braintrustRequest=f"""
                You have just been asked {message.content[11:]}. 
                Based on that question, come up with 4 characters that would have helpful insight to share regarding this exact topic.
                Name the Characters and put only their profession before their response, like 'Rick - Car Enthusiast:'.

                For an example of the output I'm looking for, if the question was:
                "is it legal to dig a tunnel to my neighbours backyard?"
                You would answer the users question in the way that each character would answer it, prepending the answer with the name and profession/skill
                example:
                Leon - Lawyer: no, that would be trespassing. I'd advise against it.
                Jared - Landscaper: not only that, it would be unsafe, you'd need the proper tools and bracing if you were to do this
                Amie - Criminal: yea don't do it, I tried to break out of jail once this way and got trapped for 36hrs before someone saved me
                Joe - Your Dad: what are you thinking? I raised you better than this!
                Put yourself in their shoes and try really hard to come up with unique insights given their specific set of skills and experiences.
                Do NOT introduce yourself OR them formally, just show their names, professions and responses.
                Give me a TL;DR of what your thoughts are at the bottom.
                """
            #sends users question to openai
            await stream_openai_multi(braintrustRequest,history,message.channel)
            # identity = artist
            # char1 = await ask_openai("describe the first character above in simplistic terms using describing words of their looks separated by commas so that I may generate a picture of them. Include their gender first.",history)
            # char2 = await ask_openai("describe the second character above in simplistic terms using describing words of their looks separated by commas so that I may generate a picture of them. Include their gender first.",history)
            # char3 = await ask_openai("describe the third character above in simplistic terms using describing words of their looks separated by commas so that I may generate a picture of them. Include their gender first.",history)
            # char4 = await ask_openai("describe the fourth character above in simplistic terms using describing words of their looks separated by commas so that I may generate a picture of them. Include their gender first.",history)
            # await comfy(char1,message.channel,"Deliberate_v3 (SFW) beta.safetensors",512,512,1)
            # await comfy(char2,message.channel,"Deliberate_v3 (SFW) beta.safetensors",512,512,1)
            # await comfy(char3,message.channel,"Deliberate_v3 (SFW) beta.safetensors",512,512,1)
            # await comfy(char4,message.channel,"Deliberate_v3 (SFW) beta.safetensors",512,512,1)
            calculateCost()
            await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
            # identity = wheatley
        except Exception as e:
            error_message = str(e)
            print(e)        
            await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",message.channel)
        return
    elif '!zork' in message.content:
        await stream_openai_multi("Let's play a Zork style game! Start by asking me what I'd like it to be about and we'll go from there.",history,message.channel)
        return
    elif '!gemini' in message.content:
        await setModeGemini()
        return
    elif '!gpt3' in message.content:
        await setModeGPT35()
        return
    elif '!gpt4' in message.content:
        await setModeGPT4()
        return
    elif '!llm' in message.content:
        await setModeLLM()
        return
    elif '!mistral' in message.content:
        await setModeMistral()
        return
        
    # displays all commands
    elif '!help' in message.content:
        await tealMessage(f"""The following functions are currently available:\n
            Simply send a message and press enter and wait for a response. No need to @ the bot, or start a thread or anything.\n
            There are many commands as well:\n
            Models:\n
            **!gpt3** - Sets GPT3.5 Turbo as the AI model
            **!gpt4** - Sets GPT4 Turbo as the AI model
            **!llm** - Sets local LLM running off GPU as the AI model (lmstudio and setup required)
            Commands:\n
            **!thanks** - this resets the conversation, as a larger conversation costs more money, just say !thanks when you're done a topic to save money. you'll also get some clever comment about the mind wipe too.\n
            **!temp** - enter a number between 0 and 1 after this command, to set the model to be either more creative or less, more is 1, less is 0, decimals are ok.\n
            **!search** - creates three different search terms, scrapes the top 3 results of each of those (9 pages scraped total) then responds to question. You can then talk to the results by using the !16k flag to ensure you have the tokens to\n
            **!1search** - enter something you want the bot to search google for and comment on, eg !search what will the weather be in new york tomorrow?\n
            it will create it's own search term, scrape the top 3 websites from a google search, then answer your original question based on the info it finds. VERY useful.\n
            **!freesearch** - scrapes less data and provides it as an attachment so that you can paste into chatgpt4 plus if you have it to save on api tokens\n
            """,message.channel)
        await tealMessage(f"""**Summarize an article or youtube video:**\n
            Simply paste the youtube or article url into chat and hit enter. In the case of youtube it will pull the transcript and summarize it. You can then talk to the results by using the !16k flag to ensure you have the tokens to do so\n
            **!prompt** - describe a picture, and the bot will create a massive prompt to be used in image gen software, or with the !image prompt (2cents per pic!)\n
            **!imagine** - generates a 1024x1024 sdxl image, unrefined, 11 second wait\n
            **!fastimagine** - generates a 512x512 photon image, 7second wait~\n
            **!refinedimagine** - generates a 1024x1024 sdxl and refined image, 16second wait~\n
            **!superimagine** - uses prompt creation and then 4x image creation based on that\n
            **!ignore** - the bot won't react at all, so just in case you want to save yourself a message for later or something\n
            **!style set an image to image style\n
            **!denoise stregth of img2img style between 0 and 1, .4 is default\n
            **!img2img AND attach an image to process the picture as described in the two lines above this\n
            **!upscale AND attach an image. the image will be upscaled x4 on all dimensions and sent back
            **File management:**\n
            There is no command here, just drop a text file in as an attachment, include a prompt within that file. The bot will respond within an attachment that it sends back to you.\n
            In this manner you can get around the 2000 word limit of discord. Especially useful when you want a massive prompt/response from GPT4.\n
            **Local commands:**\n
            These are specific to my Ubuntu box, probably won't work without editting for you.\n
            **!speedtest** - requires speedtestcli be installed first, then runs a speedtest on the computer this bot is on, then returns the results.\n
            **!network** - scans your home network (requires nmap installed) and reports on IPs of hosts that are up.\n
            **!cpu** - reports on CPU usage percent, followed by temps. hardcoded to 4 cores as that's all my server has""",message.channel)
        return
    

    #Streaming by default - with intent
    try:            
        if (model != "Gemini" and model != "open-mixtral-8x7b"): #took out local to test    model != lmStudioModel and 
            #add user message to history so that main memory has access to it
            #history.append(user_response_obj)
            #ask the non-history keeping openai to discern intent
            intent = await ask_openai_intent(f"""
                Given the user's recent input '{message.content}', please discern the intent of this message based on the following guidelines:
                1 - Choose 1 by default unless the user is asking for an image or specifically asks for a search or the weather
                2 - Choose 2 if the user's message is specifically asking to create an image of some sort.
                3 - Only choose this option if the user's message contains clear and explicit requests for an online search using phrases like 'search for', 'look up on the internet', 'find online information about', or 'Google for me'.
                
                IMPORTANT: Avoid option 3 unless specifically asked to search. EVEN if you don't know the answer or can't know the answer without a google search.
                Never use option 3 two times in a row.
                
                Based on these guidelines, reply with ONLY the digit 1, 2, or 3.
                """, history)
            # intent = await ask_openai_intent(f"""
            #     Given the users recent input '{message.content}'. Please discern the intent of this message.:
            #     1 - User is looking for a standard response from you
            #     2 - User is specifically requesting creation of an image
            #     3 - User is specifically requesting an online search
            #     Reply with ONLY the digit 1, 2 or 3.
            #     """, history)
            if "1" in intent: #respond normally
                await stream_openai_multi(message.content,history,message.channel)
                calculateCost()
                await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
                print(f"Convo History\n{history}")
                print(f"IntentHistory\n{intentHistory}")
                return
            elif "2" in intent: #generate a pic
                channel = message.channel
                numImages = await ask_openai_intent("How many pictures does it sound like they wanted? Answer with only the number, and nothing higher than 4.", history)
                numImages = int(numImages)
                if (numImages > 4):
                    await channel.send("Sorry that's too many, but I'll make you 4.")
                    numImages = 4
                await yellowMessage(f"Painting {numImages} {w}x{h} images... 🖌🎨\nPlease wait for all of them⌛\n(about 12 seconds per picture⏲️)",channel)
                for i in range(1, numImages + 1):
                    #basis = await ask_openai("Describe this image in detail as instructed previously.", history)
                    promptForImagine = await promptCreation(message.content,channel)
                    await comfyRefined(promptForImagine,1,channel,w,h)
                # member=message.guild.me
                # await member.edit(nick='Wheatley')
                calculateCost()
                await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
                print(f"Convo History\n{history}")
                print(f"IntentHistory\n{intentHistory}")
                return
            elif "3" in intent: # search
                #wipe history as this could get big
                # resetConvoHistory()
                channel = message.channel
                # question = message.content
                #print(history[-3:])
                question = message.content
                streamedMessage = await channel.send("🔎")
                try:
                    searchTerms = await ask_openai(f"Come up with 3 different web searches that you think would help you answer this question :```{question}``` Reply with ONLY the search terms, prepended by 1., 2. then 3. Do not use emojis or explain them.",history)
                    await streamedMessage.delete()
                    #strip quotes
                    searchTerms = searchTerms.replace('"', '')
                    #await yellowMessage(f"Searching:\n{searchTerms}.",channel)
                    #split the search terms into three separate variables
                    splitSearch=searchTerms.split("\n")
                    search1=splitSearch[0]
                    search2=splitSearch[1]
                    search3=splitSearch[2]
                    await silentMultiGoogle(search1, search2, search3, question, channel)
                    calculateCost()
                    await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
                    print(f"Convo History\n{history}")
                    print(f"IntentHistory\n{intentHistory}")
                    #search uses so many tokens now, replying would create an error unless you use !16k flag so just to be safe, wiping history by default
                    #resetConvoHistory() 
                    return
                except Exception as e:
                    error_message = str(e)
                    print(e)            
                    await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
                    return
            else:
                await blurpleMessage(intent,message.channel)
                return
        elif(model==lmStudioModel):
            #sends users question to openai
            await stream_openai_multi(message.content,history,message.channel)
            calculateCost()
            await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
        elif(model=="Gemini"):
            channel = message.channel
            googleMessage = await ask_gemini(message.content[7:],ghistory)
            await channel.send(googleMessage)
            await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
        elif(model=="open-mixtral-8x7b"):
            await stream_mistral_multi(message.content,history,message.channel)
            calculateCost()
            await tealMessage(f"{model} 🎟️ Tokens {totalTokens} ",message.channel)
    except Exception as e:
        error_message = str(e)
        print(e)        
        await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",message.channel)
        return

client.run(discordBotToken)
#---/DISCORD SECTION---#