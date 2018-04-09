from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    """
    用户信息
    """

    # 因为用户是用手机号注册，所以这里name,birthday,email字段可以为空
    name = models.CharField(verbose_name='姓名', max_length=32, null=True, blank=True)
    birthday = models.DateField(verbose_name='出生日期', null=True, blank=True)
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女')
    )
    gender = models.CharField(verbose_name='性别', max_length=10, choices=GENDER_CHOICES, default='male')
    mobile = models.CharField(verbose_name='手机号', max_length=11)
    email = models.EmailField(verbose_name='邮箱', max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class VerifyCode(models.Model):
    """
    短信验证码
    """

    code = models.CharField(verbose_name='验证码', max_length=10)
    mobile = models.CharField(verbose_name='手机号', max_length=11)
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)

    class Meta:
        verbose_name = '短信验证码'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code
