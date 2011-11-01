from django.db import models
from bodhi.choices import *

class Device(models.Model):
    """ Represent a network device """
    name = models.CharField(max_length=200)
    IP = models.IPAddressField(blank=True)
    MAC = models.CharField(max_length=18, blank=True)
    wakeup = models.BooleanField()
    shutdown = models.BooleanField()
    platform = models.CharField(max_length=10, blank=True)
    watt = models.IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class History(models.Model):
    """ History of a device """
    device = models.ForeignKey(Device)
    date = models.DateField(auto_now=True, db_index=True)
    timestamp = models.DateTimeField(auto_now=True, db_index=True)
    action = models.IntegerField(choices=ACTION_TYPES_CHOICES)
    user = models.TextField(max_length=20)
    result = models.IntegerField(choices=RESULTS_CODE, blank=True)
    comment = models.TextField()

    def __unicode__(self):
        return self.device.name + ' ' + str(self.timestamp)

    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "timestamp"
        verbose_name_plural = "History"
