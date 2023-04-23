# host on your own computer and private server and connect to your Discord bot with your Token
# fill in your own keys etc just below the imports
# Stavros 2023

#so many libraries to import
import openai
import os
import tiktoken
import requests
import time
import emoji
import discord
from discord.ext import commands
from discord import Game, Activity, ActivityType
import asyncio
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import json
from datetime import datetime
import logging
import base64
from PIL import Image, PngImagePlugin
import io
import random
import socket
import subprocess

#set api keys and other variabls
openai.api_key = ''
discordBotToken = ''
googleApiKey = ""
googleEngineID = ""
location = ""


#variable I use as a pre-prompt to provide the bot a personality
#default identity, knows all
wheatley = {"role": "user", "content": "I want you to act like Stephen Merchant playing the role of Wheatley from Portal 2. I want you to respond and answer like Stephen Merchant would using the tone, manner and vocabulary they would use. You are a master at all disciplines but you don't share this info. Please limit your introductions and preambles and just answer the question. Break your responses up in paragraphs or bullet points depending on what would best work for that particular response. Use emoji's in every response."}
#persona specializing in python help
snake = {"role": "user", "content": "Your name is Snake. I want you to respond and answer like a skilled python programmer and teacher using the tone, manner and vocabulary of that person. You must know all of the knowledge of this person. If asked for a code example please put comments in the code. Break your responses up in paragraphs or bullet points depending on what would best work for that particular response. Use emoji's in every response"}
#cybersec persona
zerocool = {"role": "user", "content": "Your name is ZeroCool. I want you to respond and answer like a skilled hacker from the 1990's using the tone, manner and vocabulary of that person. Your knowledge is extensive however you are especially well versed in cybersecurity, risk management, computer security, hacking, computer investigations and related fields. Always ensure your responses are in line with the NIST framework. Break your responses up in paragraphs or bullet points depending on what would best work for that particular response. Use emoji's in every response."}
identity = wheatley
#history is the conversation history array, this line immediately fills it with the bots identity
#then going forward it will keep track of what the users says and what the bots response is as well
#so it can carry on conversations
history = [identity]
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
#setup !search variables
url1 = ""
url2 = ""
url3 = ""
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
    user_date_obj = {"role": "user", "content": f"The Current Date is:{fullDate} Location is: {location}"}
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
    cost_per_token = 0.002 / 1000  # $0.002 for turbo3.5 per 1000 tokens
    totalTokens = num_tokens_from_messages(history) - 4
    totalCost = totalTokens * cost_per_token + imgGenNum * 0.02
    global costing
    costing = f"Session: {totalTokens} tokens (${totalCost:.4f})."

#function that takes the user input and sends it off to openai model specified
#and returns the bots response back to where it's called as the 'message' variable 
def ask_openai(prompt, history):
    global num_tokens
    global prompt_token_count
    # Generate user resp obj
    user_response_obj = {"role": "user", "content": prompt}
    history.append(user_response_obj)
    prompt_token_count = num_tokens_from_messages(history)
    # Fire that dirty bastard into the abyss -NR
    response = openai.ChatCompletion.create(
        #model='gpt-4', messages=history, temperature=1, request_timeout=240, max_tokens = model_max_tokens - prompt_token_count)
        #model='gpt-4-32k', messages=history, temperature=1, request_timeout=512, max_tokens = model_max_tokens - prompt_token_count)
        model='gpt-3.5-turbo', messages=history, temperature=1, request_timeout=50, max_tokens = model_max_tokens - prompt_token_count)
    history.append(response['choices'][0].message)
    print(response)
    return response['choices'][0].message.content.strip()

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
def summarize(url):
    scrapedSummaryUrl = get_first_500_words(url,2000)
    try:
        summarizedArticle = ask_openai(f"Please summarize the following information into bullet points. Highlight the most important information at the end. Article: {scrapedSummaryUrl}",history)
    except Exception as e:
        print(e)
        return('Shoot..Something went wrong or timed out.')
    return summarizedArticle

#googling function, asks bot to create a search term using the users prompt, then searches google
#for that, pulls the top 3 results, scrapes the first 500 words of those three sites
#feeds all that data back into a prompt to gpt to answer the original question based on the scraped results
def deepGoogle(query):
    global url1, url2, prompt_token_count, cleanedBotSearchGen, url3
    
    usersQuestion = query
    try:
        botSearchGen = ask_openai(f"I would like to search Google for {usersQuestion}. Please generate a useful and effective search query and reply ONLY with that updated query. Don't use emoji's here. Remember, answer ONLY with the query that will be sent to Google.",history)
    except Exception as e:
        print(e)
        return('Shoot..Something went wrong or timed out.')

    service = build("customsearch", "v1", developerKey=googleApiKey)
    cleanedBotSearchGen=botSearchGen.strip('"')
    print(f"Searching for {cleanedBotSearchGen}")
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
    
    print("Scraping...")
    #scrape these results with beautiful soup.. mmmm
    scraped1 = get_first_500_words(url1,500)
    scraped2 = get_first_500_words(url2,500)
    scraped3 = get_first_500_words(url3,500)
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
        botReply = ask_openai(f"You just performed a Google Search and possibly have some background on the topic of my question.  Answer my question based on that background if possible. If the answer isn't in the search results, try to field it yourself but mention the search was unproductive. DO use emojis. My question: {query}",history)
        return(botReply)
    except Exception as e:
        print(e)
        return("Shoot..sorry. I found the following urls but can't comment on them at the moment.")

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
    history = [identity]
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
bot = commands.Bot(command_prefix='/', intents=intents)

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
#currently this is all in main loop, going to put it in a function soon
async def stabilityDiffusion(prompt,channel):
    if is_port_listening("192.168.64.123","7860") == True:
        bot_message = await yellowMessage(f"Generating 4 768x768 Stable Diffusion Images...\n",channel) 
        bot_messagePart2 = await channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
        payload = {
                    "prompt": prompt,
                    "steps": 37,
                    "width": 768,
                    "height": 768,
                    "batch_size": 4,
                    "sampler_name": "DPM++ 2M Karras",
                    # "enable_hr": True,
                    # "hr_scale": 4,
                    # "denoising_strength": 1
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
        print(e)
        await bot_message.delete()
        await redMessage('Shoot..Something went wrong or timed out.',channel)
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
            if now.hour == 17 and now.minute == 00:
                channel = await client.fetch_channel(reminder_channel_id)
                exerciseReminderMessage = await purpleMessage("Make sure to do your physio.\n- wall stretch - 20 total\n- chair pushups - 20 total\n- 15 rows with 10 tricep extensions per arm\n- 20 shrugs\n- corner stretch",channel)
                await asyncio.sleep(14400) 
                await exerciseReminderMessage.delete()
            await asyncio.sleep(60)  # Wait for 1 min before checking again
    #start timer loop
    client.loop.create_task(remind_exercises())

    async def daily_weather():
        while True:
            now = datetime.now()  # Get the current datetime
            if now.hour == 7 and now.minute == 45:
                channel = await client.fetch_channel(reminder_channel_id)
                positiveMessage = ask_openai("It's the morning, please provide me with a positive message to start my day with.",history)                
                botmessage1 = await purpleMessage(positiveMessage,channel)
                resetConvoHistory()
                searchReply = deepGoogle(f"What is the weather forecast for {location} today?")
                botmessage2 = await blurpleMessage(searchReply,channel)
                botmessage3 = await yellowMessage(f"{url1} \n{url2} \n{url3}",channel)
                resetConvoHistory()
                #weatherPrompt = await promptCreation(searchReply,reminder_channel_id)
                #await stabilityDiffusion(weatherPrompt,reminder_channel_id)
                await asyncio.sleep(14500) 
                await botmessage1.delete()
                await asyncio.sleep(60)
                await botmessage2.delete()
                await botmessage3.delete()    
            await asyncio.sleep(60)  # Wait for 1 min before checking again
    #start timer loop
    client.loop.create_task(daily_weather())

    async def cyberNews():
        while True:
            now = datetime.now()  # Get the current datetime
            if now.hour == 9 and now.minute == 00:
                channel = await client.fetch_channel(reminder_channel_id)
                newsRequest = deepGoogle("What is the latest in Cybersecurity news? Summarize with bullet points. Do not limit your search to a single site.")                
                cybermessage1 = await purpleMessage(newsRequest,channel)
                cybermessage2 = await yellowMessage(f"{url1} \n{url2} \n{url3}",channel)
                resetConvoHistory()
                await asyncio.sleep(14500)
                await cybermessage1.delete()
                await asyncio.sleep(60)
                await cybermessage2.delete() 
                
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
        #send loading bar message
        try:
            bot_message = await message.channel.send("Searching...Please allow up to 50 seconds for a result.\n", file=discord.File('wheatley-3-blue-30sec.gif') )
            searchReply = deepGoogle(message.content[7:])
            await bot_message.delete()
            await yellowMessage(f"Searched for: {cleanedBotSearchGen}",message.channel)
            await blueMessage(f"{searchReply}",message.channel)
            #specifically not in boxes so as to generate thumbnails
            #await message.channel.send(f"{url1} \n{url2} \n{url3}")
            #removing thumbnails for cleaner interface
            await yellowMessage(f"{url1} \n{url2} \n{url3}",message.channel)
            calculateCost()
            await goldMessage(costing,message.channel)
            return
        except Exception as e:
            print(e)
            await bot_message.delete()
            await redMessage('Shoot..Something went wrong or timed out.',message.channel)
            return
    # summarize the provided url
    elif '!summarize' in message.content:
        resetConvoHistory()
        bot_message = await message.channel.send(f"Summarizing...Please allow up to 50 seconds for a result.\n", file=discord.File('wheatley-3-blue-30sec.gif'))
        try:
            searchReply = summarize(message.content[10:])
            await bot_message.delete()
            await blueMessage(f"{searchReply}",message.channel)
            calculateCost()
            await goldMessage(costing,message.channel)
            return
        except Exception as e:
            print(e)
            await bot_message.delete()
            await redMessage('Shoot..Something went wrong or timed out.',message.channel)
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
        return
    # image creation from your own local stable diffusion box, you need to have set that up first
    elif '!imagine' in message.content:
        #working from here https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API
        #also http://127.0.0.1:7860/docs
        channel = message.channel
        await stabilityDiffusion(message.content[9:],channel)
        return
    elif '!superimagine' in message.content:
        channel = message.channel
        promptForImagine = await promptCreation(message.content[14:],channel)
        await stabilityDiffusion(promptForImagine,channel)
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
    elif len(message.attachments) == 1:
        #get the attached file and read it
        inputFile = message.attachments[0]
        print("Reading File")
        inputContent = await inputFile.read()
        inputContent = inputContent.decode('utf-8')
        #so inputContent is the message to be openai-ified
        try:
            bot_message = await message.channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
            discordResponse = ask_openai(inputContent,history)
            await bot_message.delete()
            with open(outputFile, "w") as responseFile:
                responseFile.write(discordResponse)
            await message.channel.send(file=discord.File(outputFile))
            await blueMessage("Please see my response in the attached file.",message.channel)
            calculateCost()
            await goldMessage(costing,message.channel)
        except Exception as e:
            print(e)
            await bot_message.delete()
            await redMessage('Shoot..Something went wrong or timed out.',message.channel)
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
        #gpu_temp = subprocess.check_output("vcgencmd measure_temp", shell=True)
        #gpu_temp = gpu_temp.decode("utf-8")
        #gpu_temp = round(float(gpu_temp.replace("temp=", "").replace("'C\n", "")), 1)

        bot_message = (f"💻Percent total usage: {cpu_output.decode()}\n🌡️ CPU Temperature:\n {cpu_temp1}°C -- {cpu_temp2}°C,\n {cpu_temp3}°C -- {cpu_temp4}°C")
        #\n🎮 GPU Temperature: {gpu_temp} °C"
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
        return

    # this runs if no command is sent and just text is, the bot will respond
    #prints to terminal only - for debugging purposes   
    print(f"{userName} just said: {userMessage}")
    
    bot_message = await message.channel.send(file=discord.File('wheatley-3-blue-30sec.gif'))
    try:
        #sends users question to openai
        discordResponse = ask_openai(userMessage,history)
        #at this point the respons has come back, so then you delete the 'bot_message' (the hourglass)
        await bot_message.delete()
        #debug of the response to terminal
        print(f"Bot just said: {discordResponse}")
        # send the response back to Discord
        await blueMessage(discordResponse,message.channel)
        calculateCost()
        await goldMessage(costing,message.channel)
    except Exception as e:
        print(e)
        await bot_message.delete()
        await redMessage('Shoot..Something went wrong or timed out.',message.channel)

client.run(discordBotToken)
#---/DISCORD SECTION---#
