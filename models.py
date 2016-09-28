from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class OfficeSupplies(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    image = models.ImageField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Category(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class MyUser(AbstractUser):
    mobile = models.CharField(unique=True, max_length=11)

    REQUIRED_FIELDS = ['email', 'mobile']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class Histroy(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    supply = models.ForeignKey(OfficeSupplies, on_delete=models.CASCADE)
    count = models.IntegerField()
    status = models.BooleanField(default=True)
    createtime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} : {}'.format(self.userid, self.supplyid)

    class Meta:
        ordering = ['user']


