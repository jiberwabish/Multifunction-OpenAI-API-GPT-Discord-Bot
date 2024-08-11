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

     
    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
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
        "6": {
            "inputs": {
                "text": [
                    "37",
                    0
                ],
                "clip": [
                    "30",
                    1
                ]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
                "title": "CLIP Text Encode (Positive Prompt)"
            }
        },
        "8": {
            "inputs": {
                "samples": [
                    "31",
                    0
                ],
                "vae": [
                    "30",
                    2
                ]
            },
            "class_type": "VAEDecode",
            "_meta": {
                "title": "VAE Decode"
            }
        },
        "27": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptySD3LatentImage",
            "_meta": {
                "title": "EmptySD3LatentImage"
            }
        },
        "30": {
            "inputs": {
                "ckpt_name": "flux1-schnell-fp8.safetensors"
            },
            "class_type": "CheckpointLoaderSimple",
            "_meta": {
                "title": "Load Checkpoint"
            }
        },
        "31": {
            "inputs": {
                "seed": 923371567189677,
                "steps": 4,
                "cfg": 1,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": [
                    "30",
                    0
                ],
                "positive": [
                    "35",
                    0
                ],
                "negative": [
                    "33",
                    0
                ],
                "latent_image": [
                    "27",
                    0
                ]
            },
            "class_type": "KSampler",
            "_meta": {
                "title": "KSampler"
            }
        },
        "33": {
            "inputs": {
                "text": "",
                "clip": [
                    "30",
                    1
                ]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
                "title": "CLIP Text Encode (Negative Prompt)"
            }
        },
        "35": {
            "inputs": {
                "guidance": 4,
                "conditioning": [
                    "6",
                    0
                ]
            },
            "class_type": "FluxGuidance",
            "_meta": {
                "title": "FluxGuidance"
            }
        },
        "37": {
            "inputs": {
                "text": "prompt goes here",
                "seed": 654,
                "autorefresh": "No"
            },
            "class_type": "DPCombinatorialGenerator",
            "_meta": {
                "title": "Combinatorial Prompts"
            }
        },
        "47": {
            "inputs": {
                "images": [
                    "8",
                    0
                ]
            },
            "class_type": "PreviewImage",
            "_meta": {
                "title": "Preview Image"
            }
        }
    }
    """

    prompt = json.loads(prompt_text)
    #set the text prompt for our positive CLIPTextEncode
    prompt["37"]["inputs"]["text"] = description

    #set the seed for our KSampler node
    prompt["31"]["inputs"]["seed"] = randomSeed
    prompt["27"]["inputs"]["batch_size"] = batch
    prompt["27"]["inputs"]["width"] = w
    prompt["27"]["inputs"]["height"] = h

    #print("ws://{}/ws?clientId={}".format(server_address, client_id))
    # Connect to the websocket
    ws = None
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))

        # Fetch the images
        images = get_images(ws, prompt)
    except websocket.WebSocketException as e:
        print (f"WebSocketException occurred: {e}")
    finally:
        if ws is not None:
            ws.close()
            
    if images: # ensure images aren't empty
        try:
            for node_id in images:
                for image_data in images[node_id]:
                    image = Image.open(io.BytesIO(image_data))
                    print("About to save image locally")
                    image.save(f"ComfyImages/comfy_{randomSeed}.jpg")
                    print("Saved!")
                    discordImage = discord.File(f"ComfyImages/comfy_{randomSeed}.jpg", filename='image1.jpg')
                    discembed = discord.Embed()
                    discembed.set_image(url="attachment://image1.jpg")
                    await channel.send(file=discordImage, embed=discembed)
                    image.close()
        except Exception as e:
            print(f"An error occurred: {e}")
    return

# comfy upscale tool - 4x's the attached picture
async def comfyUpscale(pic,channel):
    server_address = f"{comfyIP}:{comfyPort}"
    client_id = str(uuid.uuid4())
    randomSeed = random.randint(1,10000000)

     
    def queue_prompt(prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
            return response.read()

    def get_history(prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(ws, prompt):
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = get_history(prompt_id)[prompt_id]
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

    ws = None
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))

        # Fetch the images
        images = get_images(ws, prompt)
    except websocket.WebSocketException as e:
        print (f"WebSocketException occurred: {e}")
    finally:
        if ws is not None:
            ws.close()

    if images: # ensure images aren't empty
        try:
            for node_id in images:
                for image_data in images[node_id]:
                    image = Image.open(io.BytesIO(image_data))
                    print("About to save image locally")
                    image.save(f"ComfyImages/comfy_{randomSeed}.jpg")
                    print("Saved!")
                    discordImage = discord.File(f"ComfyImages/comfy_{randomSeed}.jpg", filename='image1.jpg')
                    discembed = discord.Embed()
                    discembed.set_image(url="attachment://image1.jpg")
                    await channel.send(file=discordImage, embed=discembed)
                    image.close()
        except Exception as e:
            print(f"An error occurred: {e}")
    return
