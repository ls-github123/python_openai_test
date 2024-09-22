from django.urls import path
from api.views import ChatView, CatesView, QuestionsView

urlpatterns = [
    # GPT-4O模型测试接口
    path('chat/', ChatView.as_view(), name='chat'),
    
    # 会话分类模块接口
    path('cates/', CatesView.as_view(), name='cates'), # 获取或创建会话分类
    path('cates/<str:code>/', CatesView.as_view(), name='cates-detail'), # 根据code获取分类详情
    
    # 会话内容模块接口
    path('questions/', QuestionsView.as_view(), name='questions'), # 获取或创建会话内容
    path('questions/<str:cateid>/', QuestionsView.as_view(), name='questions-detail'), # 根据分类 ID 获取问题列表
]