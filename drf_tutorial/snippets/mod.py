#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.db import models

class SkuCode(models.Model):
    code = models.CharField(verbose_name='SkuCode标识', max_length=2)
    pid = models.IntegerField(verbose_name='父级SkuCode')
    name = models.CharField(verbose_name='SKuCode名称', max_length=32)
    level = models.IntegerField(verbose_name='SkuCode级别')
    type = models.IntegerField(verbose_name='SkuCode类型')
    status = models.IntegerField(verbose_name='SkuCode状态', default=1)
    createtime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        verbose_name = "SKU代码表"
        verbose_name_plural = "SKU代码表"

class SKU(models.Model):
    kom_id = models.IntegerField(verbose_name='KOM_ID')
    levell = models.IntegerField()
    level2 = models.IntegerField()
    level3 = models.IntegerField()
    level4 = models.IntegerField()
    level5 = models.CharField()
    sku = models.CharField()
    type = models.IntegerField()
    name = models.CharField()
    createtime = models.DateTimeField()
    status = models.IntegerField()
