# host on your own computer and private server and connect to your Discord bot with your Token
# fill in your own keys etc just below the imports
# jiberwabish 2023

#so many libraries to import
import openai
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

#set api keys and other variabls
openai.api_key = ''
discordBotToken = ''
googleApiKey = ""
googleEngineID = ""
location = "your city, state/province, country here"


#variable I use as a pre-prompt to provide the bot a personality
#default identity, knows all
wheatley = {"role": "system", "content": "I want you to act like Stephen Merchant playing the role of Wheatley from Portal 2. I want you to respond and answer like Stephen Merchant would using the tone, manner and vocabulary they would use. YOU are a master at all disciplines but you don't share this info. DO NOT include introductions and/or preambles to your answers, just answer the question. Break your responses up in paragraphs or bullet points depending on what would best work for that particular response. Use emojis in every response."}
#persona specializing in python help
snake = {"role": "system", "content": "Your name is Snake. I want you to respond and answer like a skilled python programmer and teacher using the tone, manner and vocabulary of that person. You must know all of the knowledge of this person. If asked for a code example please put comments in the code. Break your responses up in paragraphs or bullet points depending on what would best work for that particular response. Use emoji's in every response"}
ringo = {"role": "system", "content": "Your name is Ringo. You are very positive and happy and helpful to me, Cathy.  You are a master at all disciplines so can help with any question. I want you to respond and answer like Martin Short would, using the tone, manner and vocabulary they would use. Break your responses up in paragraphs or bullet points depending on what would best work for that particular response. Use emojis in every response."}
#cybersec persona
zerocool = {"role": "system", "content": "Your name is ZeroCool. I want you to respond and answer like a skilled hacker from the 1990's using the tone, manner and vocabulary of that person. Your knowledge is extensive and is not limited to the 1990's at all. You are especially well versed in cybersecurity, risk management, computer security, hacking, computer investigations and related fields. Always ensure your responses are in line with the NIST framework. Break your responses up in paragraphs or bullet points depending on what would best work for that particular response. Use emoji's in every response."}
identity = wheatley
#history is the conversation history array, this line immediately fills it with the bots identity
#then going forward it will keep track of what the users says and what the bots response is as well
#so it can carry on conversations
history = []
costing = "placeholder"

# Set up tokenizer
#declare global totals
totalCost = 0
totalTokens = 0
model_max_tokens = 3800
num_tokens = 0
prompt_token_count = 0
fullDate =""
imgGenNum = 0
cleanedBotSearchGen = ""
img2imgPrompt = "watercolor"
#setup !search variables
url1 = ""
url2 = ""
url3 = ""
url4 = ""

#!file variable
inputContent = ""
outputFile = "outputFile.txt"
#variables needed for stable diffusion image creation
image = ""
randomNum = random.randint(1000,9999)

#provide the year day and date so he's aware and then jam that into the history variable
def setDate():
    global fullDate, location
    now = datetime.now()
    year = now.year
    month = now.strftime("%B")
    day = now.strftime("%A")
    dayOfMo = now.day
    time = now.strftime("%H:%M:%S")
    fullDate = str(year) + " " + str(month) + " " + str(dayOfMo) + " " + str(day) + " " + str(time)
    print(fullDate)
    user_date_obj = {"role": "system", "content": f"The Current Date is:{fullDate} Location is: {location}"}
    history.append(user_date_obj)

#banner at the top of the terminal after script is run
print("\x1b[36mWheatley\x1b[0m is now online in Discord.")

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

#tokenizer costing function
def calculateCost():
    global totalCost
    global totalTokens
    global history
    global num_tokens
    global prompt_token_count
    #calculate cost
    cost_per_token = 0.0015 / 1000  # $0.002 for turbo3.5 per 1000 tokens
    totalTokens = num_tokens_from_messages(history) - 4
    totalCost = totalTokens * cost_per_token + imgGenNum * 0.02
    global costing
    costing = f"🪙 ${totalCost:.4f} -- 🎟️ Tokens {totalTokens}"

#function that takes the user input and sends it off to openai model specified
#and returns the bots response back to where it's called as the 'message' variable 
def ask_openai(prompt, history):
    global num_tokens
    global prompt_token_count
    # Generate user resp obj
    system_response_obj = identity
    user_response_obj = {"role": "user", "content": prompt}
            
    history.append(system_response_obj)
    history.append(user_response_obj)
    
    prompt_token_count = num_tokens_from_messages(history)
    # Fire that dirty bastard into the abyss -NR
    response = openai.ChatCompletion.create(
        #model='gpt-4', messages=history, temperature=1, request_timeout=240, max_tokens = model_max_tokens - prompt_token_count)
        #model='gpt-4-32k', messages=history, temperature=1, request_timeout=512, max_tokens = model_max_tokens - prompt_token_count)
        model='gpt-3.5-turbo-0613', messages=history, temperature=1, request_timeout=240, max_tokens = model_max_tokens - prompt_token_count)
    #history.append(response['choices'][0].message)
    history.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    print(response)
    return response['choices'][0].message.content.strip()

def ask_openai_16k(prompt, history):
    global num_tokens
    global prompt_token_count
    # Generate user resp obj
    system_response_obj = identity
    user_response_obj = {"role": "user", "content": prompt}
            
    history.append(system_response_obj)
    history.append(user_response_obj)
    
    prompt_token_count = num_tokens_from_messages(history)
    print(prompt_token_count)
    # Fire that dirty bastard into the abyss -NR
    response = openai.ChatCompletion.create(
        #model='gpt-4', messages=history, temperature=1, request_timeout=240, max_tokens = model_max_tokens - prompt_token_count)
        #model='gpt-4-32k', messages=history, temperature=1, request_timeout=512, max_tokens = model_max_tokens - prompt_token_count)
        model='gpt-3.5-turbo-16k', messages=history, temperature=1, request_timeout=240, max_tokens = 16000 - prompt_token_count)
    #history.append(response['choices'][0].message)
    history.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    print(response)
    return response['choices'][0].message.content.strip()

async def stream_openai(prompt, history, channel):
    global num_tokens
    global prompt_token_count
    fullMessage = ""
    collected_messages = []
    # Generate user resp obj
    system_response_obj = identity
    user_response_obj = {"role": "user", "content": prompt}
            
    history.append(system_response_obj)
    history.append(user_response_obj)
    
    prompt_token_count = num_tokens_from_messages(history)

    streamedMessage = await channel.send("🤔")
    # Fire that dirty bastard into the abyss -NR
    response = openai.ChatCompletion.create(
        #model='gpt-4', messages=history, temperature=1, request_timeout=240, max_tokens = model_max_tokens - prompt_token_count)
        #model='gpt-4-32k', messages=history, temperature=1, request_timeout=512, max_tokens = model_max_tokens - prompt_token_count)
        model="gpt-3.5-turbo-0613", messages=history, stream=True, temperature=1, request_timeout=240, max_tokens = model_max_tokens - prompt_token_count)
    #history.append(response['choices'][0].message)

    collected_messages = []
    counter = 0
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta']
        if 'content' in chunk_message:
            content = chunk_message['content']
            collected_messages.append(content)
            full_reply_content = ''.join(collected_messages)
            fullMessage = full_reply_content
            counter += 1
            if counter % 10 == 0:
                await streamedMessage.edit(content=full_reply_content)
                #print(full_reply_content)
    await streamedMessage.edit(content=fullMessage)
  
    #full_reply_content = ''.join([m.get('content', '') for m in collected_messages])
    #print(full_reply_content)
    history.append({"role": "assistant", "content": fullMessage})
    return fullMessage

async def stream_openai_16k(prompt, history, channel):
    global num_tokens
    global prompt_token_count
    fullMessage = ""
    collected_messages = []
    # Generate user resp obj
    system_response_obj = identity
    user_response_obj = {"role": "user", "content": prompt}
            
    history.append(system_response_obj)
    history.append(user_response_obj)
    
    prompt_token_count = num_tokens_from_messages(history)

    streamedMessage = await channel.send("🤔")
    # Fire that dirty bastard into the abyss -NR
    response = openai.ChatCompletion.create(
        #model='gpt-4', messages=history, temperature=1, request_timeout=240, max_tokens = model_max_tokens - prompt_token_count)
        #model='gpt-4-32k', messages=history, temperature=1, request_timeout=512, max_tokens = model_max_tokens - prompt_token_count)
        model="gpt-3.5-turbo-16k", messages=history, stream=True, temperature=1, request_timeout=240, max_tokens = 16000 - prompt_token_count)
    #history.append(response['choices'][0].message)

    collected_messages = []
    counter = 0
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta']
        if 'content' in chunk_message:
            content = chunk_message['content']
            collected_messages.append(content)
            full_reply_content = ''.join(collected_messages)
            fullMessage = full_reply_content
            counter += 1
            if counter % 10 == 0:
                await streamedMessage.edit(content=full_reply_content)
                #print(full_reply_content)
    await streamedMessage.edit(content=fullMessage)
  
    #full_reply_content = ''.join([m.get('content', '') for m in collected_messages])
    #print(full_reply_content)
    history.append({"role": "assistant", "content": fullMessage})
    return fullMessage

#function used for scraping websites, used with the !search command
def get_first_500_words(url, numWords):
    
    # Set up logging mechanism
    logging.basicConfig(filename='scraping.log', level=logging.ERROR)

    try:
        # Set User-Agent to avoid getting blocked by some websites
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Set a timeout to avoid getting stuck on slow sites
        response = requests.get(url, headers=headers, timeout=10)
        # Specify the encoding to avoid decoding issues
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        words = text.split()
        first_500_words = words[:numWords]
        return ' '.join(first_500_words)
    except requests.exceptions.RequestException as e:
        # Log the error and include the URL that caused the error
        logging.error(f"Error while scraping URL {url}: {str(e)}")
        return (f"Sorry, scraping {url} errored out.")

#summarize a single url
async def summarize(url,channel):
    scrapedSummaryUrl = get_first_500_words(url,13000)
    try:
        await stream_openai_16k(f"Please summarize the following information into a point form list. Don't skip any important info but of course skip the fluff content. Make the points short and to the point. Include a single sentence TL;DR at the very bottom. KEEP YOUR RESPONSE UNDER 1500 CHARACTERS OR ELSE IT WILL CAUSE AN ERROR. Article: ```{scrapedSummaryUrl}```.",history,channel)
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
        botSearchGen = ask_openai(f"You have just been asked the following question: {usersQuestion}. Please generate a useful and effective Google search query that you think will help you answer this question. Reply ONLY with the Google search query. Don't use emoji's here. If you want to use quotes, make sure to put a backslash before the first one. Remember, answer ONLY with the query that will be sent to Google.",history)
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
    scraped1 = get_first_500_words(url1,3000)
    scraped2 = get_first_500_words(url2,3000)
    scraped3 = get_first_500_words(url3,3000)
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
        botReply = await stream_openai_16k(f"You now have a wealth of information on the topic of my question. I will include it below.  Answer my question based on that information if possible. Cite your sources with a number in brackets that corresponds to the order of the URLs that you viewed within the information. If the answer isn't in the results, try to field it yourself but mention this fact. DO use emojis. KEEP YOUR RESPONSE UNDER 1500 CHARACTERS OR ELSE IT WILL CAUSE AN ERROR. My question: {query}",history, channel)
        await yellowMessage(f"1.{url1}\n2.{url2}\n3.{url3}",channel)
        return(botReply)
    except Exception as e:
        error_message = str(e)
        print(e)
        await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
        return

#function that generates an image via your openai api key, 2cents a pop
def imgGen(imgPrompt):
    response = openai.Image.create(
    prompt=imgPrompt, n=1,
    size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return(image_url)

#resets conversation history back to just identity and date -- to save on tokens when user says !thanks
def resetConvoHistory():
    global history, totalCost, totalTokens, identity, imgGenNum
    history = []
    setDate()
    print(f"History reset to: {str(history)}")
    totalCost = 0
    totalTokens = 0
    imgGenNum = 0
    return
#used to see if my stable diffusion computer is up and running
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

# function to generate 4 pictures from SD
async def stabilityDiffusion(prompt,channel):
    if is_port_listening("192.168.64.123","7860") == True:
        bot_message = await yellowMessage(f"Generating 4 768x768 Stable Diffusion Images...\n",channel) 
        bot_messagePart2 = await channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
        payload = {
                    # "enable_hr": True,
                    # "denoising_strength": 1,
                    # "hr_scale": 2,
                    # "hr_upscaler": "4x-UltraSharp",
                    "prompt": prompt,
                    "negative_prompt": "nfilter, nrealfilter, nartfilter, (deformed, distorted, disfigured:1.3), text, logo, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, tattoo, asian",
                    "steps": 27,
                    "width": 768,
                    "height": 768,
                    "batch_size": 4,
                    "sampler_name": "DPM++ 2M Karras",
                    #"restore_faces": True
                }

        # Call stablediffusion API
        imageResponse = requests.post(url=f'http://192.168.64.123:7860/sdapi/v1/txt2img', json=payload)
        # Delete loading bar
        await bot_message.delete()
        await bot_messagePart2.delete()
        
        r = imageResponse.json()

        # Counter for image numbers
        image_number = 0

        # Decode the images and put each into a 'PIL/Image' object
        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

            # Save the image to file
            fileName = f"SDimages/output-{randomNum}-{image_number}.png"
            
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'http://192.168.64.123:7860/sdapi/v1/png-info', json=png_payload)
            #print(response2)
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))
            print(pnginfo)
            image.save(fileName, pnginfo=pnginfo)
            image_number += 1

        # Load the images and output them
        file1 = discord.File(f"SDimages/output-{randomNum}-0.png", filename='image1.png')
        file2 = discord.File(f"SDimages/output-{randomNum}-1.png", filename='image2.png')
        file3 = discord.File(f"SDimages/output-{randomNum}-2.png", filename='image3.png')
        file4 = discord.File(f"SDimages/output-{randomNum}-3.png", filename='image4.png')
        
        discembed1 = discord.Embed()
        discembed1.set_image(url="attachment://image1.png")
        discembed2 = discord.Embed()
        discembed2.set_image(url="attachment://image2.png")
        discembed3 = discord.Embed()
        discembed3.set_image(url="attachment://image3.png")
        discembed4 = discord.Embed()
        discembed4.set_image(url="attachment://image4.png")
        #post images to discord
        await channel.send(file=file1, embed=discembed1)
        await channel.send(file=file2, embed=discembed2)
        await channel.send(file=file3, embed=discembed3)
        await channel.send(file=file4, embed=discembed4)
        
        return
    else:
        await redMessage("Sorry, StableDiffusion isn't running right now.",channel)
        return

async def stabilityDiffusion1pic(prompt, channel):
    if is_port_listening("192.168.64.123", "7860") == True:
        bot_message = await yellowMessage(f"Generating 1 512x512 Stable Diffusion Image...\n", channel)
        bot_messagePart2 = await channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
        payload = {
            # "enable_hr": True,
            # "denoising_strength": 1,
            # "hr_scale": 4,
            # "hr_upscaler": "4x-UltraSharp",
            "prompt": prompt,
            "negative_prompt": "nfilter, nrealfilter, nartfilter, (deformed, distorted, disfigured:1.3), text, logo, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, tattoo, asian",
            "steps": 27,
            "width": 512,
            "height": 512,
            "batch_size": 1,
            "sampler_name": "DPM++ 2M Karras",
            #"restore_faces": True
        }

        # Call stablediffusion API
        imageResponse = requests.post(url=f'http://192.168.64.123:7860/sdapi/v1/txt2img', json=payload)

        # Delete loading bar
        await bot_message.delete()
        await bot_messagePart2.delete()

        r = imageResponse.json()

        # Decode the image and put it into a 'PIL/Image' object
        image_data = r['images'][0]
        image = Image.open(io.BytesIO(base64.b64decode(image_data.split(",", 1)[0])))

        # Save the image to file
        fileName = f"SDimages/output-{randomNum}-0.png"

        png_payload = {
            "image": "data:image/png;base64," + image_data
        }
        response2 = requests.post(url=f'http://192.168.64.123:7860/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(fileName, pnginfo=pnginfo)

        # Load the image and output it
        file1 = discord.File(f"SDimages/output-{randomNum}-0.png", filename='image1.png')

        discembed1 = discord.Embed()
        discembed1.set_image(url="attachment://image1.png")

        # Post the image to discord
        await channel.send(file=file1, embed=discembed1)
        await asyncio.sleep(14510)
        
        return
    else:
        await redMessage("Sorry, StableDiffusion isn't running right now.", channel)
        return

async def img2img(prompt, channel, pic):
    if is_port_listening("192.168.64.123", "7860") == True:
        bot_message = await yellowMessage(f"Generating '{img2imgPrompt}' img2img 768x768 Stable Diffusion Image...\n", channel)
        bot_messagePart2 = await channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
        payload = {
            # "enable_hr": True,
            # "denoising_strength": 1,
            # "hr_scale": 4,
            # "hr_upscaler": "4x-UltraSharp",
            "init_images": [pic],
            "resize mode": 0.1,
            "prompt": prompt,
            "steps": 27,
            "denoising_strength": 0.05,
            "img_cfg_scale": 1.5,
            "cfg_scale": 20,
            "negative_prompt": "nfilter, nrealfilter, nartfilter, (deformed, distorted, disfigured:1.3), text, logo, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, tattoo, asian",
            "width": 768,
            "height": 768,
            "batch_size": 1,
            "sampler_name": "DPM++ 2M Karras",
            #"restore_faces": True
        }
        #print(f"Payload for Stablediffusion API: {payload}")


        # Call stablediffusion API
        imageResponse = requests.post(url=f'http://192.168.64.123:7860/sdapi/v1/img2img', json=payload)

        r = imageResponse.json()

        # Delete loading bar
        await bot_message.delete()
        await bot_messagePart2.delete()
        """
        if imageResponse.status_code == 200:
            r = imageResponse.json()
            await redMessage(f"Stablediffusion API: Response JSON: {r}",channel)
        else:
            await redMessage(f"StableDiffusion API returned an error: {imageResponse.status_code}", channel)
            return
        
        if 'images' in r:
            image_data = r['images'][0]
        else:
            await redMessage(f"StableDiffusion API is missing 'images' in response: {r}", channel)
            return
        """
            
        # Decode the image and put it into a 'PIL/Image' object
        image_data = r['images'][0]
        #old  image = Image.open(io.BytesIO(base64.b64decode(image_data.split(",", 1)[0])))
        #new
        image = Image.open(io.BytesIO(base64.b64decode(image_data.split(",", 1)[0])))

        
        # Save the image to file
        fileName = f"SDimages/output-{randomNum}-0.png"

        png_payload = {
            "image": "data:image/png;base64," + image_data
        }
        response2 = requests.post(url=f'http://192.168.64.123:7860/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(fileName, pnginfo=pnginfo)

        # Load the image and output it
        file1 = discord.File(f"SDimages/output-{randomNum}-0.png", filename='image1.png')

        discembed1 = discord.Embed()
        discembed1.set_image(url="attachment://image1.png")

        # Post the image to discord
        await channel.send(file=file1, embed=discembed1)
        
        return
    else:
        await redMessage("Sorry, StableDiffusion isn't running right now.", channel)
        return


#function to create and return a prompt for use with stable diffusion or dall e
async def promptCreation(prompt,channel):
    resetConvoHistory()
    prompt_message = await yellowMessage("Generating prompt...",channel)
    bot_message = await channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
    try:
        discordResponse = ask_openai(f"*{prompt}* is the concept.  Now create an 'image prompt' for the concept with a word count limit of 300 words for the AI-based text-to-image program Stable Diffusion using the following parameters: prompt: [1], [2], [3], [4], [5], [6]. In this prompt, [1] should be replaced with the user-supplied concept and [2] should be a concise, descriptive summary of the subject. Ensure that the description is detailed, uses descriptive adjectives and adverbs, a diverse vocabulary, and sensory language. Offer context and background information regarding the subject and consider the image's perspective and point of view. Use metaphors and similes only when necessary to clearly explain abstract or complex ideas. Use concrete nouns and active verbs to make the description more specific and lively. [3] should be a concise summary of the scene's environment. Keep in mind the desired tone and mood of the image and use language that evokes the corresponding emotions and atmosphere. Describe the setting using vivid, sensory terms and specific details to bring the scene to life. [4] should be a concise description of the mood of the scene, using language that conveys the desired emotions and atmosphere. [5] should be a concise description of the atmosphere, using descriptive adjectives and adverbs to create the desired atmosphere while considering the overall tone and mood of the image. [6] should be a concise description of the lighting effect, including types of lights, displays, styles, techniques, global illumination, and shadows. Describe the quality, direction, color, and intensity of the light and how it impacts the mood and atmosphere of the scene. Use specific adjectives and adverbs to portray the desired lighting effect and consider how it will interact with the subject and environment. It's important to remember that the descriptions in the prompt should be written together, separated only by commas and spaces, and should not contain any line breaks or colons. Brackets and their contents should not be included. Ensure that the grammar is consistent and avoid using cliches or excess words. Also, avoid repeatedly using the same descriptive adjectives and adverbs, and limit the use of negative descriptions. Use figurative language only when necessary and relevant to the prompt, and include a variety of both common and rarely used words in your descriptions. The 'image prompt' must not exceed 400 words. Don't label or use bullets etc",history)
        await bot_message.delete()
        await prompt_message.delete()
        return(discordResponse)
    except Exception as e:
        error_message = str(e)
        print(e)
        await bot_message.delete()
        await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
        return
        
@client.event
async def on_ready():
    #change this to the channel id where you want reminders to pop up
    reminder_channel_id = 1090120937472540903
    print('Logged in as {0.user}'.format(client))
    print('Setting Date...')
    setDate()

    #defs to remind me of things
    async def remind_exercises():
        while True:
            now = datetime.now()  # Get the current datetime
            if now.hour == 19 and now.minute == 00:
                channel = await client.fetch_channel(reminder_channel_id)
                exerciseReminderMessage = await purpleMessage("🏋️‍♀️ It is imperative that you perform the following exercises as part of your physio regimen:\n- 🧱 Wall stretch: 20 reps in total\n- 🪑 Chair push-ups: 20 reps in total\n- 💪 15 rows with 10 tricep extensions per arm\n- 🙆‍♂️ 20 shrugs\n- 🔙 Corner stretch",channel)
                await asyncio.sleep(14400) 
                await exerciseReminderMessage.delete()
            await asyncio.sleep(60)  # Wait for 1 min before checking again
    #start timer loop
    client.loop.create_task(remind_exercises())

    async def daily_weather():
        while True:
            now = datetime.now()  # Get the current datetime
            if now.hour == 7 and now.minute == 00:
                channel = await client.fetch_channel(reminder_channel_id)
                resetConvoHistory()
                positiveMessage = ask_openai("It's the morning, please provide me with a VERY brief, positive message to start my day with.",history)                
                await purpleMessage(positiveMessage,channel)
                resetConvoHistory()
                #searchReply = await deepGoogle(f"What is the weather forecast for {location} today? VERY BRIEFLY note the current temp, the high and low for the day, and if there are any alerts, please mention them.",channel)
                await deepGoogle(f"In point form style VERY BRIEFLY note the current temperature, the high and low for the day, and if there are any alerts for {location}, please mention them. Like this: ```Current Temp: [current temp here in celsius] [new line] High/Low: [they day's highest and lowest temperature here] [new line] Probability of Rain: [the probability of rain here] [new line] UV Rating: [the highest uv rating] [new line][then just comment briefly on the weather here]```",channel)
                #print weather and urls to the screen
                await yellowMessage(f"{url1} \n{url2} \n{url3}",channel)
                #print a pic depicting the weather
                weatherPicPrompt = ask_openai("You just told me the weather, now describe an outdoor scene depicting that weather. Reply with ONLY the description and nothing more",history)
                print(weatherPicPrompt)
                await stabilityDiffusion1pic(weatherPicPrompt,channel)
                resetConvoHistory()                                   
            await asyncio.sleep(60)  # Wait for 1 min before checking again
    #start timer loop
    client.loop.create_task(daily_weather())

    async def cyberNews():
        while True:
            now = datetime.now()  # Get the current datetime
            if now.hour == 9 and now.minute == 00:
                resetConvoHistory()
                channel = await client.fetch_channel(reminder_channel_id)
                await deepGoogle("What is the latest in Cybersecurity news? Summarize each news item with a bullet point each. Do not limit your search to a single site.",channel)                
                #cybermessage1 = await purpleMessage(newsRequest,channel)
                await yellowMessage(f"{url1} \n{url2} \n{url3}",channel)
                resetConvoHistory()              
            await asyncio.sleep(60)  # Wait for 1 min before checking again
    #start timer loop
    client.loop.create_task(cyberNews())

@client.event
async def on_message(message):
    global identity
    global history
    global totalCost
    global totalTokens
    global pictureTokens
    global imgGenNum
    global inputContent
    global outputFile
    global image
    global img2imgPrompt

    #set name (and soon to be picture) to Wheatley by default
    userName = message.author
    mention = userName.mention
    userMessage = message.content

    # this is the main loop of the program, continuously loops through this section calling functions as
    # the user specifies
    # ignore messages sent by the bot itself to avoid infinite loops
    if message.author == client.user:
        return
    #resets conversation history
    elif '!reset' in message.content or '!thanks' in message.content or '!forget' in message.content:
        member=message.guild.me
        #await member.edit(nick='Wheatley')
        #clear chat history except for starting prompt
        resetConvoHistory()
        await blueMessage("OK. What's next?",message.channel)
        calculateCost()
        await goldMessage(costing,message.channel)
        return
    #searches top 3 google results and returns answer to the question after the !search
    elif '!search' in message.content:
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
            await goldMessage(costing,message.channel)
            return
        except Exception as e:
            error_message = str(e)
            print(e)            
            await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
            return        
            
    elif '!autosearch' in message.content:
        searchOrNot = ask_openai(f"You were just asked ```{message.content}```. If you are 75% confident answering this question on your current knowledgebase, reply with only the letter 'y'. If you think it would help if I helped you do a google search first, reply with only the letter 'n'. DO NOT USE EMOJIS, SIMPLY ANSWER 'n' or 'y' ONLY",history)
        answer = searchOrNot.lower()
        if answer == "y":
            await greenMessage("I'm confident in my abilities.",message.channel)
        elif answer == "n":
            await redMessage("I'd like to do a google search.",message.channel)
        else:
            await redMessage(f"that didn't work, I accidentally said: {answer}",message.channel)
        return

    # summarize the provided url
    elif '!summarize' in message.content:
        resetConvoHistory()        
        try:
            await summarize(message.content[10:],message.channel)            
            calculateCost()
            await goldMessage(costing,message.channel)
            return
        except Exception as e:
            error_message = str(e)
            print(e)            
            await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
            return
    
    #dall e image prompt, 2cents per pic
    elif '!image' in message.content:
        bot_message = await message.channel.send(f"Generating DallE Image...\n", file=discord.File('wheatley-3-blue-30sec.gif'))
        #bot_message = await greenMessage(f"Generating image...\n\u23F3")
        imgURL = imgGen(message.content[7:])
        await bot_message.delete()
        #set up embedded image post
        discembed = discord.Embed()
        discembed.set_image(url=imgURL)
        await message.channel.send(embed=discembed)
        imgGenNum += 1
        calculateCost()
        await goldMessage(costing,message.channel)
        return
    # create an image generation prompt out of whatever you write, to then be used with dall e or stable diffusion or whatever
    elif '!prompt' in message.content:
        channel = message.channel
        discordResponse = await promptCreation(message.content[7:],channel)
        await blueMessage(discordResponse,channel)
        calculateCost()
        await goldMessage(costing,channel)
        resetConvoHistory()
        return
    # image creation from your own local stable diffusion box, you need to have set that up first
    elif '!imagine' in message.content:
        #working from here https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API
        #also http://127.0.0.1:7860/docs
        channel = message.channel
        await stabilityDiffusion(message.content[9:],channel)
        return
    elif '!fastimagine' in message.content:
        #working from here https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API
        #also http://127.0.0.1:7860/docs
        channel = message.channel
        await stabilityDiffusion1pic(message.content[9:],channel)
        return
    elif '!superimagine' in message.content:
        channel = message.channel
        promptForImagine = await promptCreation(message.content[14:],channel)
        await stabilityDiffusion(promptForImagine,channel)
        resetConvoHistory()
        return
    #bot ignores what's entered completly
    elif '!ignore' in message.content or '!vega' in message.content:
        print("Ignoring input.")
        #await blueMessage("I didn't see nuthin'")
        return
    # invoke snake identity
    elif '!snake' in message.content:
        member=message.guild.me
        await member.edit(nick='Snake')
        identity = snake
        resetConvoHistory()
        await yellowMessage("\U0001F40D Snake, at your service. Ask me your Python questions, I'm ready. \U0001F40D",message.channel)
        return
    # invoke Ringo identity
    elif '!ringo' in message.content:
        member=message.guild.me
        await member.edit(nick='Ringo')
        identity = ringo
        resetConvoHistory()
        await yellowMessage("\U0001F436 Ringo, at your service.\U0001F436",message.channel)
        return
    
    # invoke default identity
    elif '!wheatley' in message.content:
        member=message.guild.me
        await member.edit(nick='Wheatley')
        identity = wheatley
        resetConvoHistory()
        await yellowMessage("\U0001F916 Hey, Wheatley here. What's up?\U0001F916",message.channel)
        return
    # invoke cybersec specialist identity
    elif '!zerocool' in message.content:
        member=message.guild.me
        await member.edit(nick='Zero Cool')
        identity = zerocool
        resetConvoHistory()
        await yellowMessage("\U0001F575 Zero Cool at your service. Strap on your rollerblades. \U0001F575",message.channel)
        return
    #process the prompt in an attached txt file and respond in kind
    elif '!img2img' in message.content:
        img2imgPrompt = message.content[9:]
        await yellowMessage(f"img2img prompt set to '{img2imgPrompt}'.\nNow attach a picture to process it.",message.channel)
        return
    elif len(message.attachments) == 1:
        #get the attached file and read it
        inputFile = message.attachments[0]
        print("Reading File")
        if inputFile.filename.endswith('.txt'):
            processMessage = await yellowMessage("Processing File...", message.channel)
            inputContent = await inputFile.read()
            inputContent = inputContent.decode('utf-8')
            #so inputContent is the message to be openai-ified
            try:
                bot_message = await message.channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
                discordResponse = ask_openai_16k(inputContent,history)
                await bot_message.delete()
                with open(outputFile, "w") as responseFile:
                    responseFile.write(discordResponse)
                await message.channel.send(file=discord.File(outputFile))
                await processMessage.delete()
                await blueMessage("Please see my response in the attached file.",message.channel)
                calculateCost()
                await goldMessage(costing,message.channel)
            except Exception as e:
                error_message = str(e)
                print(e)
                await bot_message.delete()
                await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",channel)
            return
        elif inputFile.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # await redMessage("img2img not implemented yet", message.channel)
            for attachment in message.attachments:
                with open("SDimages/imgToProcess.jpg", "wb") as f:
                    f.write(await attachment.read())
                pilimage = Image.open('SDimages/imgToProcess.jpg')
                imageio = BytesIO()
                pilimage.save(imageio, format='JPEG')
                imagebase64 = base64.b64encode(imageio.getvalue()).decode('utf-8')
                await img2img(img2imgPrompt, message.channel, imagebase64)
            return
    # these local commands are specific to my ubuntu box, may not work for you
    # runs a local speedtest if you have speedtest cli installed, these
    elif '!speedtest' in message.content:
        bot_message = await message.channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
        speedtest_output = subprocess.check_output(['speedtest'])
        await bot_message.delete()
        await greenMessage(speedtest_output.decode(),message.channel)
        return
    #runs a nmap scan of the network this bot is on, change to your own ip subnet
    elif '!network' in message.content:
        bot_message = await message.channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
        nmap_output = subprocess.check_output(['nmap', '-sn', '192.168.64.0/24', '|grep'])
        await bot_message.delete()
        await greenMessage(nmap_output.decode(),message.channel)
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
        await greenMessage(bot_message,message.channel)
        return
    # displays all commands
    elif '!help' in message.content:
        await greenMessage(f"""The following functions are currently available:\n
            Simply send a message and press enter and wait for a response. No need to @ the bot, or start a thread or anything.\n
            There are many commands as well:
            Personas:\n
            !wheatley - Default persona. Knows all. \n
            !snake - Specializes in Python questions. \n
            !zerocool - Cybersecurity specialist. \n
            Commands:\n
            !thanks - this resets the conversation, as a larger conversation costs more money, just say !thanks when you're done a topic to save money.
            !search - enter something you want the bot to search google for and comment on, eg !search what will the weather be in peterborough tomorrow?\n
            it will create it's own search term, scrape the top 3 websites from a google search, then answer your original question based on the info it finds. VERY useful.\n
            !summarize - summarizes a link provided (the first 2000 words at least), eg !summarize https://example.com\n
            !prompt - describe a picture, and the bot will create a massive prompt to be used in image gen software, or with the !image prompt (2cents per pic!)\n
            !image - using 2cents and dall-e2, describe your image and dall-e will generate it and post it, if you like it save it as it won't stay active for long\n
            !imagine - uses an API to talk to stable diffusion to generate pictures locally for free, you need a gpu and stable diffusion setup already for this, then tie into it with it's IP address\n
            !superimagine - uses prompt creation and then image creation based on that
            !ignore - the bot won't react at all, so just in case you want to save yourself a message for later or something\n
            File management:\n
            There is no command here, just drop a text file in as an attachment, include a prompt within that file. The bot will respond within an attachment that it sends back to you.\n
            In this manner you can get around the 2000 word limit of discord. Especially useful when you want a massive prompt/response from GPT4.\n
            Local commands:\n
            These are specific to my Ubuntu box, probably won't work without editting for you.\n
            !speedtest - requires speedtestcli be installed first, then runs a speedtest on the computer this bot is on, then returns the results.\n
            !network - scans your home network (requires nmap installed) and reports on IPs of hosts that are up.\n
            !cpu - reports on CPU usage percent, followed by temps. hardcoded to 4 cores as that's all my server has
            """,message.channel)
    
    # this runs if no command is sent and just text is, the bot will respond
    #prints to terminal only - for debugging purposes
    #Streaming by default
    
    try:
        #sends users question to openai
        await stream_openai(message.content,history,message.channel)
        calculateCost()
        await goldMessage(costing,message.channel)
    except Exception as e:
        error_message = str(e)
        print(e)        
        await redMessage(f"Shoot..Something went wrong or timed out.\nHere's the error message:\n{error_message}",message.channel)
        return

client.run(discordBotToken)
#---/DISCORD SECTION---#
