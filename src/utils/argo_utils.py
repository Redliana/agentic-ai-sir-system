# src/utils/argo_utils.py

"""
Utility file for Argo and Milvus API Endpoints.
To be used by the RAG agent for:
1. Retrieving embeddings based on user prompts.
2. Performing searches based on Milvus collection.
3. Interacting with chat based on user prompts.
"""

# Import libraries
import json
import os
import requests


def run_embeddings(model, prompts):
    """Sends a POST request to the Argo API and retrieves embeddings based on the provided model and prompts."""
    
    # Argo Embedding API
    url = "https://apps.inside.anl.gov/argoapi/api/v1/resource/embed/"
    
    # Data to be sent as a POST in JSON format
    data = {
        "user": (os.getenv("USERNAME") or os.getenv("USER")),
        "model": model,
        "prompt": prompts,
    }
    
    # Convert the dict to JSON
    payload = json.dumps(data)
    # Add a header stating that the content type is JSON
    headers = {"Content-Type": "application/json"}
    output = None
    
    try:
        # Send POST request
        response = requests.post(url, data=payload, headers=headers)
        # Receive and save the response data
        if response.status_code == 200:
            output = response.json()
    except requests.exceptions.HTTPError as e:
        print(e)

    return output # parsed response data

def run_search(collection, data, output_fields, limit: int):
    """Performs a vector search query on a specific collection using a Milvus database API endpoint."""
    
    # Milvus database endpoint 
    url = "http://titanv.gss.anl.gov:19530/v1/vector/search"

    # Data to be sent as a POST in JSON format
    data = {
        "collectionName": collection,
        "vector": data[0],
        "annsField": "text_vector",
        "outputFields": output_fields,
        "limit": limit,
    }

    # Convert the dict to JSON
    payload = json.dumps(data)
    # Add a header stating that the content type is JSON
    headers = {
        "Authorization-Token": "Bearer root:Milvus",
        "Content-Type": "application/json",
    }

    output = None
    try:
        # Send POST request
        response = requests.post(url, data=payload, headers=headers)
        # Receive and save the response data
        if response.status_code == 200:
            output = response.json()
        else:
            print(response.status_code)
    except requests.exceptions.HTTPError as e:
        print(e)

    return output # parsed response data


def run_chat(instructions, model, prompt):
    """Interacts with chat-based API endpoint for generating responses from LLM."""
    
    # Argo Chat API
    url = "https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/chat/"

    # Data to be sent as a POST in JSON format
    data = {
        "user": (os.getenv("USERNAME") or os.getenv("USER")),
        "model": model,
        "system": instructions,
        "prompt": [prompt],
        "stop": [],
        "temperature": 0.1,
        "top_p": 0.9,
    }
    # Convert the dict to JSON
    payload = json.dumps(data)
    # Add a header stating that the content type is JSON
    headers = {"Content-Type": "application/json"}
    output = None
    
    try:
        # Send POST request
        response = requests.post(url, data=payload, headers=headers)
        # Receive and save the response data
        if response.status_code == 200:
            output = response.json()["response"]
    except requests.exceptions.HTTPError as e:
        print(e)

    return output # chat's model response

