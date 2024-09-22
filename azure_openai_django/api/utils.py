# 定义大模型API请求调用模块
import requests
from django.conf import settings

# 发送问题到 Azure OpenAI GPT-4o 模型并返回响应结果
def call_azure_openai_gpt4o(question):
    # question 获取问题内容
    # messages 请求体中的消息内容
    messages = [
        {
            "role": "user", # 定义消息发送者角色
            "content": question, # 消息的文本内容
        }
    ]

    # 定义请求头
    headers = {
        "Content-Type": "application/json",
        "api-key": settings.AZURE_API_KEY, # 从 settings 中读取配置信息
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
            "max_tokens": 800, # 目前Microsoft_Azure API限制最大为1000
        }
    
    # 发送请求并处理响应
    try:
        # 使用requests库向Microsoft_Azure服务器发送一个调用API的http_post请求
        # AZURE_ENDPOINT - API请求地址(终结点)
        # headers 包含HTTP请求头信息的字典
        # json=payload 将请求体发送为JSON格式 timeout设置30秒超时
        response = requests.post(settings.AZURE_ENDPOINT, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析JSON响应
        json_response = response.json()
        choices = json_response.get("choices")
        if not choices:
            return None # API响应格式不正确
        
        # 提取返回的数据
        # choices[0] 从 API 响应的 JSON 数据列表中获取列表的第一个生成结果
        # .get("message", {}) get方法安全的获取字典中键的值,如果键不存在 则返回默认值 {}
        # .get("content", "") get 方法从上一步中提取到的 "message" 字典中获取 "content" 字段
        # 如果content字段不存在,则返回默认值 ("")
        answer = choices[0].get("message", {}).get("content", "")
        return answer, None # 正常返回 answer 和 None 表示无错误
    except requests.RequestException as e:
        return None, f"API 请求失败: {str(e)}"  # 返回 None 和 错误消息