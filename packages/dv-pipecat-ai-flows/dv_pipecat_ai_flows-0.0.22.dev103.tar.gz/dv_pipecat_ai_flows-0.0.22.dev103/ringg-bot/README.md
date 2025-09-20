# Twilio Chatbot

This project is a FastAPI-based chatbot that integrates with Twilio to handle WebSocket connections and provide real-time communication. The project includes endpoints for starting a call and handling WebSocket connections.

#To deploy on remote Dv machine
On the root folder. run the following commands:

1. sudo docker build -t ringg-chatbot -f examples/ringg-chatbot/Dockerfile .
   (or) sudo docker build --no-cache -t ringg-chatbot -f examples/ringg-chatbot/Dockerfile .
2. sudo docker ps -a
3. sudo docker stop <Id of the running contianer>
4. sudo docker run -p 8765:8765 -d ringg-chatbot

## Table of Contents

- [Twilio Chatbot](#twilio-chatbot)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configure Twilio URLs](#configure-twilio-urls)
  - [Running the Application](#running-the-application)
    - [Using Python](#using-python)
    - [Using Docker](#using-docker)
  - [Usage](#usage)

## Features

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+.
- **WebSocket Support**: Real-time communication using WebSockets.
- **CORS Middleware**: Allowing cross-origin requests for testing.
- **Dockerized**: Easily deployable using Docker.

## Requirements

- Python 3.12 (managed via pyenv recommended)
- Docker (for containerized deployment)
- ngrok (for tunneling)
- Twilio Account
- dv-pipecat source code (located at `../dv-pipecat` relative to this project)

## Installation

### Local Development Setup (Recommended for Development)

1. **Create Python 3.12 virtual environment using pyenv**:

   ```sh
   # Navigate to the project root (dv-pipecat-flows)
   cd /path/to/dv-pipecat-flows

   # Set local Python version to 3.12
   pyenv local 3.12.0

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   source venv/bin/activate
   ```

2. **Install dv-pipecat in editable mode** (for development with live code changes):

   ```sh
   # Install dv-pipecat from local source with all required extras
   # This allows you to make changes to dv-pipecat code and see them immediately
   pip install -e "../dv-pipecat[daily,cartesia,openai,silero,deepgram,azure,elevenlabs,noisereduce,soundfile,speechmatics,gladia,google,groq,sentry,local-smart-turn,remote-smart-turn,anthropic]"
   ```

3. **Install dv-pipecat-flows in editable mode** (for development with live code changes):

   ```sh
   # Install the pipecat_flows package from the project root
   pip install -e .
   ```

4. **Install ringg-bot dependencies**:

   ```sh
   pip install -r ringg-bot/requirements.txt
   ```

5. **Create .env**:

   ```sh
   # Navigate to ringg-bot directory
   cd ringg-bot

   # Create .env file based on env.example
   cp env.example .env
   # Edit .env with your actual configuration values
   ```

6. **Setup GCP credentials** (required for transcripts and recordings):
   ```sh
   # Create creds.json file in ringg-bot directory with your GCP service account credentials
   # This file is used for authenticating with Google Cloud Storage to upload transcripts and recordings
   # Download the service account key from Google Cloud Console and save it as creds.json
   ```

### Alternative: Using Pre-built Wheel

If you prefer to use a pre-built wheel instead of editable installation:

1. **Set up a virtual environment**:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

2. **Install local Pipecat build**:

   ```sh
   # Set the path to your local pipecat dist directory
   export PIPECAT_DIST_PATH="../dv-pipecat/dist"

   # Install the latest pipecat wheel with all required extras
   pip install "$(ls -1t ${PIPECAT_DIST_PATH}/*.whl | head -1)[daily,cartesia,openai,silero,deepgram,azure,elevenlabs,noisereduce,gladia,google,groq,sentry,soundfile,local-smart-turn,speechmatics,remote-smart-turn]"
   ```

3. **Install dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Create .env**:
   create .env based on env.example

5. **Setup GCP credentials**:
   Create creds.json file in ringg-bot directory with your GCP service account credentials

6. **Install ngrok**:
   Follow the instructions on the [ngrok website](https://ngrok.com/download) to download and install ngrok.

## Configure Twilio URLs

1. **Start ngrok**:
   In a new terminal, start ngrok to tunnel the local server:

   ```sh
   ngrok http 8765
   ```

2. **Update the Twilio Webhook**:
   Copy the ngrok URL and update your Twilio phone number webhook URL to `http://<ngrok_url>/start_call`.

3. **Update streams.xml**:
   Copy the ngrok URL and update templates/streams.xml with `wss://<ngrok_url>/ws`.

## Running the Application

### Using Python

1. **Run the FastAPI application**:
   ```sh
   python server.py
   ```

### Using Docker

1. **Build the Docker image**:

   ```sh
   docker build -t twilio-chatbot .
   ```

2. **Run the Docker container**:
   ```sh
   docker run -it --rm -p 8765:8765 twilio-chatbot
   ```

## Usage

To start a call, simply make a call to your Twilio phone number. The webhook URL will direct the call to your FastAPI application, which will handle it accordingly.

## Development Notes

### Quick Start Commands (for experienced developers)

```sh
# From project root (dv-pipecat-flows)
pyenv local 3.12.0
python -m venv venv
source venv/bin/activate
pip install -e "../dv-pipecat[daily,cartesia,openai,silero,deepgram,azure,elevenlabs,noisereduce,soundfile,speechmatics,gladia,google,groq,sentry,local-smart-turn,remote-smart-turn,anthropic]"
pip install -e .
pip install -r ringg-bot/requirements.txt
cd ringg-bot
python server.py
```

### Troubleshooting

**Dependency Conflicts with pipecat-ai:**
If you encounter import errors related to pipecat-ai versions, ensure that:

1. The `pipecat-ai-whisker` package is commented out in `requirements.txt` (it pulls in PyPI pipecat-ai)
2. Only your local editable dv-pipecat installation is active:
   ```sh
   pip uninstall pipecat-ai pipecat-ai-whisker -y
   pip install -e "../dv-pipecat[...]"  # Reinstall local version
   ```

**Missing GCP Credentials:**
If you encounter errors related to Google Cloud Storage or transcript/recording uploads:

1. Ensure `creds.json` exists in the `ringg-bot` directory
2. The file should contain valid GCP service account credentials with appropriate permissions
3. Download the service account key from Google Cloud Console and save it as `creds.json`

### Filler Words Configuration

For filler words to be powered from local files, create a directory with the voice name (voice key in the call_config) and copy the mp3 files to that directory with the filler phrase name as the filename. Replace spaces with underscores in the file names.

### Audio Format Conversion (if needed)

To convert mp3 to pcm for fillers:

```sh
ffmpeg -i examples/ringg-chatbot/fillers/en-IN-RehaanNeural/en_got_it.mp3 -acodec pcm_s16le -ar 8000 -ac 1 -f s16le examples/ringg-chatbot/fillers/en-IN-RehaanNeural/en_got_it.pcm
```

### Deploying New Version of Pipecat

To deploy a new version of pipecat:

```sh
rm -rf dist/
python -m build
twine upload dist/*
```

_Note: Ensure you have access to the PyPI dv account before deploying._
