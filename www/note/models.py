from django.db import models

# Create your models here.

class Note(models.Model):
    rid = models.IntegerField()
    lid = models.IntegerField(null=True)
    type = models.CharField(max_length=64)
    data = models.CharField(max_length=1024, null=True)

    def __str__(self):
        return "{}, {}, {}, '{}', '{}'".format(self.id, self.rid, self.lid, self.type, self.data)

