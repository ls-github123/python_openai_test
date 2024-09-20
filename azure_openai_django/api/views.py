import requests
import time
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decouple import config

# 定义大模型API请求调用模块
class ChatView(APIView):
    def post(self, request):
        # 从请求中获取问题
        question = request.data.get("question") # 获取问题内容
        
        if not question:
            return Response({"error": "问题不能为空!"}, status=status.HTTP_400_BAD_REQUEST)

        # 从环境变量.env文件中读取 API 密钥和终结点
        api_key = config("AZURE_API_KEY") # 密钥
        endpoint = config("AZURE_ENDPOINT") # 终结点
        
        # 准备请求的消息内容
        messages = [
            {
                "role": "user", # 定义消息发送者角色
                "content": question # 消息的文本内容
            }
        ]
        
        # 定义请求头
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }
        
        # 定义请求体
        payload = {
            "messages": messages, # 列表 包含对话的历史内容, 包含用户发送的问题
            # temperature 控制模型生成文本的随机性(取值0-1) 
            # 值越接近 0，模型的输出会更确定和一致 用于需要严格、精确回答的场景
            # 值越接近 1，输出会更具随机性和创造性，适合生成更具创意的内容
            # 0.7 表示输出有一定程度的随机性，但不会过于发散，适合对话生成
            "temperature": 0.7,
            # top_p 核采样参数 限制模型考虑的词汇范围 (范围0-1)
            # top_p = 1 时，模型会考虑所有可能的词汇
            # top_p 值较小时，模型会限制输出为可能性最高的几个词汇
            "top_p": 0.95,
            # max_toknes 限制生成最大的token数量
            #（即单词或符号的基本单位，包含字母、标点符号等）
            # 800个token约等于 600-800 个单词
            "max_tokens": 800 # 目前Microsoft_Azure API限制最大为1000
        }

        # 发送请求并处理响应
        try:
            # 使用request库向Microsoft_Azure服务器发送一个调用API的http_post请求
            # endpoint - API请求地址(终结点)
            # headers 包含HTTP请求头信息的字典
            # json=payload 将请求体发送为JSON格式
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()  # 检查请求是否成功
            
            # answer
            # response.json() 将response对象转换为JSON格式
            # .get("choices", [{}]) 从 JSON 对象中获取键为 "choices" 的数据
            # get() 方法用于从字典中安全地获取键值对，如果 "choices" 不存在，则返回默认值 [{}]
            # choices 通常是一个包含多个选项的列表，其中每个选项都代表模型生成的不同响应
            # [0] 用来从 choices 列表中提取第一个元素。在多数情况下，choices 列表中只有一个选项，所以我们直接访问第一个（索引为 0）响应
            answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            # 通过 StreamingHttpResponse 逐字返回响应(前端逐字接收 显示并生成内容)
            # Content-Type 设置为标准流式数据传输类型 text/event-stream
            return StreamingHttpResponse(self.stream_response(answer), content_type='text/event-stream')
        # 处理请求错误
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # 定义流式响应生成器
    def stream_response(self, text):
        for char in text:
            yield f"data: {char}\n\n" # # SSE (Server-Sent Events) 格式
            time.sleep(0.1)  # 控制字符输出的速度，模拟流式效果