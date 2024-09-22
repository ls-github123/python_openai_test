from django.db import models

# 会话分组模型
class CatesModel(models.Model):
    code = models.CharField('会话编码', max_length=10,primary_key=True, unique=True)
    title = models.CharField('会话标题', max_length=50, null=True, blank=True)
    creation_time = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'cates_model'
        managed = True
        verbose_name = '会话分组'
        verbose_name_plural = '会话分组'
    
    def __str__(self):
        return self.title

# 会话内容模型
class QuestionModel(models.Model):
    ask = models.CharField('会话提问', max_length=100, null=True, blank=True)
    answer = models.TextField('回复内容', blank=True)
    response_time = models.DateTimeField('回复时间', auto_now_add=True)
    cid = models.ForeignKey(CatesModel, on_delete=models.CASCADE, related_name='questions', verbose_name='对应分组')
    
    class Meta:
        db_table = 'question_model'
        managed = True
        verbose_name = '会话内容'
        verbose_name_plural = '会话内容'
        
    def __str__(self):
        return self.ask