# Wheatley Discord Bot (ChatGPT backed OpenAI API bot to be precise, gpt3.5)

Welcome to the Wheatley Discord Bot! This bot is designed to provide you and your server with informative results from the web within the comfort of the Discord interface. With Wheatley, you can search Google, generate images based on your prompt, and so much more!

Bring ChatGPT with you everywhere, and when others complain that the website is down, you can say 'yea well MY chatgpt still works' while you bust open discord and get answers in no time.

I have a persona for Wheatly but you are free to easily just change the variable to whatever persona you want!

## Disclaimer - I am not a programmer by trade! 
- I am learning as I go. I've used chatgpt to help me write this bot and now I just use this bot to help me write this bot.
- my code is probably a garbled mess though I do try to comment it nicely. chatgpt has helped me get to a working bot much faster than I should have so I'm sure I've skipped basic training as it were.
- I'm not using env files or breaking my code into files and stuff like I probably should
- I'm aware this is not pristine, but it works and it's fun and is an incredible learning experience for me
- feel free to give me pointers if you are just so appaled you can't stay quiet :) constructive criticism is always welcome, I may or may not have time to act on it.

## github file explanation

- glados.py - Discord bot configured for GPT4. You can manually edit Wheatley which is GPT3.5 to be gpt4 by uncommenting out a line in his code, but I find it easier to just make 2 separate bots and have separate channels for them in Discord.
- wheatley-3-blue-30sec.gif - used as a loading bar, just have it in the same folder you run the bots from
- wheatleyDiscord.py - the main bot, gpt3.5, lots of functions, !help once he's up explains them all
- wheatleyTerminal.py - if you wanted to run from terminal instead of Discord for whatever reason
- requirements.txt - list of librarys, can be installed once you have python up and running with pip install -r requirements.txt

## Requirements

- free Google API Search key and engine ID code - optional but highly recommended to use the !search feature, https://developers.google.com/webmaster-tools/search-console-api/v1/configure
- OpenAI API key - get an account from beta.openai.com/playground ensure billing is setup to increase your rate limits, generate an api key in settings
- python 3.10 at least
- then once python is installed, run pip install -r requirements.txt to install all the libraries needed
- a Discord Bot's token - created from the Discord Developer Portal, see below

## Discord Bot setup How To
- log in to Discord client and make yourself a server with just you in it
- log in to the Discord Developer Portal: [Discord Developer Portal](https://discord.com/developers)
- click Application at the left, and click New Application button on the right
- Name it, check the box, click create
- on the left hand side click 'Bot', then on the right 'Add Bot'
- click the 'copy' button to copy your token somewhere save, or directly into the variable at the top of the script
- uncheck 'public bot'
- check all three intents
- under OAuth2 check bot
- under bot permissions check all text permissions, (the whole middle row), then in the General column, select change nickname, read messages/ view channels
- now you'll see a link along the bottom has been generated, copy this link in a new tab and click it to add your bot to your server
- fill in all the api keys etc at the top of the script and start your bot on your local computer
- once started your bot will come online in your channel and you can start talking to it!

## Features

The following functions are currently available:

- Simply send a message and press enter and wait for a response. No need to @ the bot, or start a thread or anything.

There are many commands as well:
Personas:

- !wheatley - Default persona. Knows all.
- !snake - Specializes in Python questions.
- !zerocool - Cybersecurity specialist.

Commands:

- !thanks - this resets the conversation, as a larger conversation costs more money, just say !thanks when you're done a topic to save money.
- !search - enter something you want the bot to search google for and comment on, eg '!search what will the weather be in chicago tomorrow?' it will create it's own search term, scrape the top 3 websites from a google search, then answer your original question based on the info it finds. VERY useful.
- !summarize - summarizes a link provided (the first 2000 words at least), eg !summarize https://example.com/
- !prompt - describe a picture, and the bot will create a massive prompt to be used in image gen software, or with the !image prompt (2cents per pic!)
- !image - using 2cents and dall-e2, describe your image and dall-e will generate it and post it, if you like it save it as it won't stay active for long
- !imagine - uses an API to talk to stable diffusion to generate pictures locally for free, you need a gpu and stable diffusion setup already for this, then tie into it with it's IP address
- !ignore - the bot won't react at all, so just in case you want to save yourself a message for later or something

File management:

- There is no command here, just drop a text file in as an attachment, include a prompt within that file. The bot will respond within an attachment that it sends back to you. In this manner you can get around the 2000 word limit of discord. Especially useful when you want a massive prompt/response from GPT4.

Local commands:

These are specific to my Ubuntu box, probably won't work without editting for you.

- !speedtest - requires speedtestcli be installed first, then runs a speedtest on the computer this bot is on, then returns the results.
- !network - scans your home network (requires nmap installed) and reports on IPs of hosts that are up.
- !cpu - reports on CPU usage percent, followed by temps. hardcoded to 4 cores as that's all my server has

Time Triggered events:
- by default you will get a morning message and weather report at 745am (just change this in the code if it's unwanted)
- a reminder to do your physio at 7pm ;)
- cybersecurity new roundup at 9am
- These are just placeholders, change them to things that work for you or delete/comment them out

## Getting Started

This is not a public bot. You are to copy the code and input your own API keys and pull it into a private discord server.

Once you have invited your version of Wheatley to your server, you can start using commands mentioned above, or just talk to it.

By default, the bot is named Wheatley with the same identity. However, you are free to change his identity by creating a new persona (just copy the formatting of Wheatley or Snake, and then set identity to that instead.

## Usage

Make liberal use of the !thanks command to keep wiping history to save you api $$. You'll note there is a running cost after every message just so you're aware.

Wheatley responds to any message posted in your server, he's currently designed for personal server use only because of this fact. It makes him much easier to talk to versus needing to make a thread everytime or mention him.
