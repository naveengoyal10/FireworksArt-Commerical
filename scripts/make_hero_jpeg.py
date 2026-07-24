from PIL import Image
import os
BASE=os.path.join('static','sample_images')
os.makedirs(BASE, exist_ok=True)
img=Image.new('RGB',(1600,600),(255,232,214))
img.save(os.path.join(BASE,'hero1.jpeg'),'JPEG',quality=85)
print('written', os.path.join(BASE,'hero1.jpeg'))
