FROM python:3.8.16-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
COPY .env .env
RUN apt-get update && apt-get install git -y
RUN apt-get install -y nodejs
RUN apt-get install -y npm
RUN npm install pm2 -g
RUN pip3 install -r requirements.txt
RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN apt-get install -y ffmpeg
COPY rabbit-v2.py .
CMD ["pm2-runtime", "start", "rabbit-v2.py", "--name=whisper"]
