import time
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from . import models
from . import serializers
from .utils import call_azure_openai_gpt4o # Azure_openai_got4o大模型调用封装
from django.core.paginator import Paginator # 分页模块

# GPT-4O模型测试调用视图
class ChatView(APIView):
    def post(self, request):
        # 从请求中获取问题
        question = request.data.get("question")
        if not question:
            return Response({"error":"问题不能为空!"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 调用封装的 API 函数并处理返回结果
        answer, error = call_azure_openai_gpt4o(question)
        if error:
            return Response({"error":error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 正常返回流式响应
        # 通过 StreamingHttpResponse 逐字返回响应(前端逐字接收 显示并生成内容)
        # Content-Type 设置为标准流式数据传输类型 text/event-stream
        return StreamingHttpResponse(self.stream_response(answer), content_type='text/event-stream')
    
    # 定义一个流式生成器函数
    # 逐字流式发送数据到前端,模拟逐字输效果
    def stream_response(self, text):
        for char in text:
            # for循环 遍历传入的字符串 text 中的每一个字符 char
            # text 为大模型或其他来源生成的完整回答
            # for 循环逐一获取该字符串中的每个字符
            yield f"data: {char}\n\n" # 格式化字符串 构造 Server-Sent Events (SSE) 数据格式
            # yield 是一个 Python 生成器的关键字, 作用是逐次返回每个字符的处理结果
            time.sleep(0.05) # 控制输出速度


# 定义前端会话分类接口视图
def generate_unique_code(): # 定义一个函数用于生成唯一的code
    while True:
        code = "t" + str(random.randint(100000, 999999))  # 生成6位随机数
        if not models.CatesModel.objects.filter(code=code).exists():
            return code  # 如果数据库中不存在该code，则返回

# 会话分类接口视图
class CatesView(APIView):
    
    # POST 方法：新建会话分类
    def post(self, request):
        # 查询是否有未命名的会话分类
        cates = models.CatesModel.objects.filter(title__isnull=True).first()
        if not cates:  # 如果没有未命名的会话分类
            code = generate_unique_code()  # 生成唯一的 code
            cates = models.CatesModel.objects.create(code=code)  # 创建新分类
        return Response({"code": 200, "cateid": cates.code})

    # GET 方法：获取所有会话分类的标题
    def get(self, request):
        # 获取搜索名称
        stitle = request.GET.get('title')
        if stitle:
            # 如果有搜索条件，进行过滤
            cates = models.CatesModel.objects.exclude(title__isnull=True).filter(title__startswith=stitle).order_by('-creation_time').all()
        else:
            # 获取所有已命名的会话分类，并按时间排序，最新的在前
            cates = models.CatesModel.objects.exclude(title__isnull=True).order_by('-creation_time').all()

        # 序列化数据
        ser = serializers.CatesSerializers(cates, many=True)
        return Response({
            "code": 200,
            "clist": ser.data
        }, status=status.HTTP_200_OK)
    
# 定义前端会话内容接口视图
class QuestionsView(APIView):
    def post(self, request):
        # 接收参数
        # 使用get方法获取参数, 避免抛出keyerror异常
        ask = request.data.get('ask')
        cateid = request.data.get('cateid')
        
        # 参数校验
        if not ask:
            return Response({"error":"问题不能为空!"}, status=status.HTTP_400_BAD_REQUEST)
        if not cateid:
            return Response({"error":"分类ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查分类是否存在
        cates = models.CatesModel.objects.filter(code=cateid).first()
        if not cates:
            # 如果分类不存在, 则创建新的分类并生成唯一code
            code = generate_unique_code()
            cates = models.CatesModel.objects.create(code=code)
            
        # 调用GPT-4O模型获取答案
        answer, error = call_azure_openai_gpt4o(ask)
        if error:
            return Response({"error":error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 更新分类名称(如果分类名为空)
        cname = ''
        if not cates.title:
            cname = ask[:10] # 使用问题的前10个字符作为分类名称
            cates.title = cname
            cates.save()
            
        # 写入问答表
        # 将会话问题及答案存入数据库
        models.QuestionModel.objects.create(ask=ask, answer=answer, cid=cates)
        return Response({"code":200, "catename":cname, "answer":answer})
    
    def get(self, request):
        # 获取参数 cateid
        cid = request.GET.get('cateid')
        
        # 参数校验
        if not cid:
            return Response({"error":"分类ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查分类是否存在
        if not models.CatesModel.objects.filter(code=cid).exists():
            return Response({"error":"分类不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取该分类下的所有问题
        ques = models.QuestionModel.objects.filter(cid_id=cid).order_by('-response_time')
        
        # 获取页码并进行校验
        page_number = request.GET.get('page', 1)
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1
        # 添加分页模块
        paginator = Paginator(ques, 10) # 每页显示10条数据
        page_obj = paginator.get_page(page_number)
        
        # 调用序列化器处理
        ser = serializers.QuestionSerializes(page_obj, many=True)
        
        # 返回分页后的数据
        return Response({
            "code":200,
            "qlist":ser.data,
            "current_page":page_obj.number,
            "total_pages": paginator.num_pages,
        })