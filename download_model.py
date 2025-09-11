#!/usr/bin/env python3
"""
Script to download the sentiment analysis model
"""

import requests
import os
import sys

MODEL_URL = "https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl"
MODEL_PATH = "sentimentanalysismodel.pkl"

def download_model():
    """Download the sentiment analysis model"""
    print("Downloading sentiment analysis model...")
    
    try:
        # Check if model already exists
        if os.path.exists(MODEL_PATH):
            print(f"Model {MODEL_PATH} already exists. Skipping download.")
            return True
        
        # Download the model
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()
        
        # Save the model
        with open(MODEL_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Model downloaded successfully: {MODEL_PATH}")
        print(f"File size: {os.path.getsize(MODEL_PATH)} bytes")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading model: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)