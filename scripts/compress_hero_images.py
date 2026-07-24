from PIL import Image
import glob, os

def compress(path, size=(1600,600), quality=75):
    try:
        im = Image.open(path)
        im = im.convert('RGB')
        im = im.resize(size, Image.LANCZOS)
        im.save(path, 'JPEG', quality=quality, optimize=True)
        print('saved', path, os.path.getsize(path))
    except Exception as e:
        print('err', path, e)

# static location
static_path = os.path.join('static','sample_images','hero1Krishna.jpeg')
if os.path.exists(static_path):
    compress(static_path)
else:
    print('static not found', static_path)

# any media copies
for p in glob.glob(os.path.join('media','hero','hero1Krishna*.jpeg')):
    compress(p)

print('done')
