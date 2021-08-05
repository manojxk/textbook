from django.db import models
from storages.backends.gcloud import GoogleCloudStorage
from multiselectfield import MultiSelectField
# Create your models here.
# from django.core.files.storage import DEFAULT_FILE_STORAGE
storage = GoogleCloudStorage()
# DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

class Upload(models.Model):
    @staticmethod
    def upload_image(file, filename):
        try:
            target_path = '/images/' + filename
            path = storage.save(target_path, file)
            return storage.url(path)
        except Exception as e:
            print("Failed to upload!")

class Matching(models.Model):
    name = models.CharField(max_length = 100)
    sell_topics = models.CharField(max_length = 100)
    buy_topics = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100)
    study_topics = models.CharField(max_length = 100)
    email = models.EmailField(max_length = 254, default = 'None')
    sell_price = models.DecimalField(decimal_places = 2, max_digits=100, default=10.00)

    #books to sell, books to buy, topics to study together, location of residence



