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

- Automated searches with Google power
- Responsive image generation
- Memory management with !thanks, !reset, or !forget commands
- Token Cost Tracking so you can see how much your chats cost (not much!)
- can process txt attachments and respond via txt attachment (get around Discord word limit)

## Getting Started

This is not a public bot. You are to copy the code and input your own API keys.

Once you have invited your version of Wheatley to your server, you can start using commands such as:
- !help - lists ALL commands currently available
- !search - Use this command to search Google and provide you with the top two search results. He then extracts info from the two pages: 250 words from each, to simulate doing the pages for you in case you don't want to read the whole page by yourself.
- !image - Generate a response image related to your search term
- !snake - set bot to a python coding teacher identity
- !wheatley !thanks, !reset, and !forget - Use these commands to wipe conversation history and set identity back to Wheatley
- !prompt - describe an image you would like generator and Wheatley will return a Stable Diffusion prompt to make it (stable diffusion required and is completely separate from this, see automatic1111's stable diffusion github, beefy gpu required: https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- !summarize - this accepts a url then summarizes it based on the first 2000 words scraped from the page
- just attach a file to have the bot reply via file (gets around Discord word limits)

By default, the bot is named Wheatley with the same identity. However, you are free to change his identity by creating a new persona (just copy the formatting of Wheatley or Snake, and then set identity to that instead.

## Usage

With Wheatley, you can have ongoing conversations that become smarter and more personalized to you over the course of the conversation--but keep in mind that this learning process comes at a cost. Wheatley remembers your previous interactions, so be sure to use the !thanks command once you're done with the conversation to clear memory and avoid accruing extra costs.

Wheatley responds to any message posted in your server, he's currently designed for personal server use only because of this fact. It makes him much easier to talk to versus needing to make a thread everytime or mention him.
