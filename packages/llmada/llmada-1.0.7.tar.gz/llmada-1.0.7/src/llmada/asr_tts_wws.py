
#!/usr/bin/env python3
import argparse
import json
import logging
import uuid
import websockets
from protocols import MsgType, full_client_request, receive_message


def get_cluster(voice: str) -> str:
    if voice.startswith("S_"):
        return "volcano_icl"
    return "volcano_tts"


class Args():
    def __init__(self, text:str, encoding = "wav", voice_type = None, appid = None, access_token = None, endpoint = None):
        self.appid = appid or "9370139706"
        self.access_token = access_token or "rPnirNKqj-jYwic1yTYpVOUU0xx2g8uj"
        self.voice_type = voice_type or "zh_female_yuanqinvyou_moon_bigtts"
        self.cluster = ""
        self.text = text
        self.encoding = encoding
        self.endpoint = endpoint or "wss://openspeech.bytedance.com/api/v1/tts/ws_binary"

async def main(text:str, encoding = "wav"):

    args = Args(text = text,encoding =encoding)
    # Determine cluster
    cluster = args.cluster if args.cluster else get_cluster(args.voice_type)

    # Connect to server
    headers = {
        "Authorization": f"Bearer;{args.access_token}",
    }

    print(f"Connecting to {args.endpoint} with headers: {headers}")
    websocket = await websockets.connect(
        args.endpoint, additional_headers=headers, max_size=10 * 1024 * 1024
    )
    print(
        f"Connected to WebSocket server, Logid: {websocket.response.headers['x-tt-logid']}",
    )

    try:
        # Prepare request payload
        request = {
            "app": {
                "appid": args.appid,
                "token": args.access_token,
                "cluster": cluster,
            },
            "user": {
                "uid": str(uuid.uuid4()),
            },
            "audio": {
                "voice_type": args.voice_type,
                "encoding": args.encoding,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": args.text,
                "operation": "submit",
                "with_timestamp": "1",
                "extra_param": json.dumps(
                    {
                        "disable_markdown_filter": False,
                    }
                ),
            },
        }

        # Send request
        await full_client_request(websocket, json.dumps(request).encode())

        # Receive audio data
        audio_data = bytearray()
        while True:
            msg = await receive_message(websocket)

            if msg.type == MsgType.FrontEndResultServer:
                continue
            elif msg.type == MsgType.AudioOnlyServer:
                audio_data.extend(msg.payload)
                if msg.sequence < 0:  # Last message
                    break
            else:
                raise RuntimeError(f"TTS conversion failed: {msg}")

        # Check if we received any audio data
        if not audio_data:
            raise RuntimeError("No audio data received")

        # Save audio file
        filename = f"tests/resources/{args.voice_type}.{args.encoding}"
        with open(filename, "wb") as f:
            f.write(audio_data)
        print(f"Audio received: {len(audio_data)}, saved to {filename}")

    finally:
        await websocket.close()
        print("Connection closed")

if __name__ == "__main__":
    import asyncio

    asyncio.run(main(text = "你好，我是琐琐碎碎火山引擎的语音合成服务。这是一个美好的旅程。"))

