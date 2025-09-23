# 测试 client 部分

'''
Author: 823042332@qq.com 823042332@qq.com
Date: 2025-09-01 17:39:41
LastEditors: 823042332@qq.com 823042332@qq.com
LastEditTime: 2025-09-03 11:43:22
FilePath: /llmada/tests/test_asr.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import requests
import os
from llmada.client import OpenAIClient
import pytest


def test_client_request():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    params = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
        }
    response = client.request(params = params)
    print(response)


async def test_client_arequest():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    params = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
        }
    response = await client.arequest(params = params)
    print(response)

def test_client_request_tts():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    data = {
            "model": "tts-1",
            "input": "你好 世界",
            "voice": "alloy",
            "file_path": 'tests/resources/speech2.mp3',
        }
    response = client.request_tts(data)
    print(response)

async def test_client_arequest_tts():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    params = {
            "model": "tts-1",
            "input": "你好 世界 天气不错",
            "voice": "alloy",
            "file_path": 'tests/resources/speech.mp3',
        }
    response = await client.arequest_tts(params = params)
    print(response)

def test_client_request_asr():
    # 未通过
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))
    params = {
            "model": "whisper-1",
            "file_path": 'tests/resources/speech2.mp3',
        }
    response = client.request_asr(params = params)
    print(response)



def test_client_request_stream():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    data = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
            "stream": True,
        }
    response = client.request_stream(data)
    for i in response:
        print(i)

async def test_client_request_stream():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    data = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
            "stream": True,
        }
    response = client.arequest_stream(data)
    async for i in response:
        print(i)


def test_client_request_stream():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    params = {
            'model': 'gemini-2.5-flash-image-preview',
            'messages': [{'role': 'user', 'content': '绘制两个小孩的照片'}],
            "temperature": 0.7,
            'stream': True
        }
    response = client.request_image_stream(params,filename_prefix ="tests/resources/gemini_output" )
    for i in response:
        print(i)

def test_request_modal():
    pass
