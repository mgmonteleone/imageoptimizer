from mongoengine import *
connect("test")
from classes import Fileinfo

class Animal(Document):
    genus = StringField()
    family = StringField()
    photo = FileField()

marmot = Animal(genus='Marmota', family='Sciuridae')

marmot_photo = open('test.jpg', 'rb')
marmot.photo.put(marmot_photo, content_type = 'image/jpeg')
marmot.save()

marmotout = Animal.objects(genus="Marmota").first()
photo = marmotout.photo.read()
file = open("test2.jpg","wb")
file.write(photo)
file.close()