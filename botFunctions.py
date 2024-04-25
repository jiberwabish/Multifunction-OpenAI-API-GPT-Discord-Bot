# Some functions for OpenAI API bot
# Still a work in progress
# Author: Jiberwabish
# Date: Apr 12 2024

import discord
import json
from PIL import Image
import io
import random
# Import required libraries for comfy
import websocket # NOTE: websocket-client library from GitHub (https://github.com/websocket-client/websocket-client)
import uuid      # For generating unique client IDs
import json      # For JSON handling
import urllib.request  # For making HTTP requests
import urllib.parse    # For URL encoding
import os
from dotenv import load_dotenv
load_dotenv() #pull .env variables in

comfyIP = os.environ['comfyIP']
comfyPort = os.environ['comfyPort']

#message functions to easily print in color boxes
async def blackMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.darker_grey()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message
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
async def redMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.red()
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
async def tealMessage(messageToSend,channel):
    discembed = discord.Embed(
        description=f"{messageToSend}",
        color=discord.colour.Colour.dark_teal()
    )
    bot_message = await channel.send(embed=discembed)
    return bot_message

# function to generate comfy picture, number and rez is changable depending on how you call the function
async def comfyRefined(description,batch,channel,w,h):
    server_address = f"{comfyIP}:{comfyPort}"
    client_id = str(uuid.uuid4())
    randomSeed = random.randint(1,10000000)

     
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

    #print("ws://{}/ws?clientId={}".format(server_address, client_id))
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

# comfy upscale tool - 4x's the attached picture
async def comfyUpscale(pic,channel):
    server_address = f"{comfyIP}:{comfyPort}"
    client_id = str(uuid.uuid4())
    randomSeed = random.randint(1,10000000)

    
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

    #print("ws://{}/ws?clientId={}".format(server_address, client_id))
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
