from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from . import models

# 会话内容序列化
class QuestionSerializes(ModelSerializer):
    class Meta:
        model = models.QuestionModel
        fields = ('ask', 'answer')
        
# 会话分组序列化
class CatesSerializers(ModelSerializer):
    class Meta:
        model = models.CatesModel
        fields = ('code', 'title')