from django.db import models

# Create your models here.
class sunbak_Crawl_DataModel(models.Model):
    imgsrc = models.URLField(max_length=200)
    title = models.CharField(max_length=100)
    price = models.CharField(max_length=15)
    boardType = models.CharField(max_length=10)
    detailURL = models.CharField(max_length=255, unique=True)
    updated_at = models.DateField(null=True)
    siteName = models.CharField(max_length=12, null=True)
    price_int = models.PositiveIntegerField(default=0)
    regNumber = models.PositiveIntegerField(default=0)
    boardURL = models.CharField(max_length=255)
    thumb_image = models.ImageField(upload_to='thumbs/', null=True)
    tons = models.FloatField()

    class Meta:
        unique_together = ('siteName', 'regNumber')

    def __str__(self):
        return self.title

class connectionTimeModel(models.Model):
    action_time = models.DateTimeField(auto_now=True)
    boardType = models.CharField(max_length=12)