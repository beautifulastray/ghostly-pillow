from PIL import Image, ImageChops, ImageCms
from glob import glob
import io
import os

sizes = [[2000, 3000]]

os.chdir(r"C:\Users\Katie\Desktop\resizes\raw")

files = [x for x in glob('*.png') if not x.endswith('resized.png')]

def convert_to_srgb(img):
    '''Конвертирует PIL-изображение в цветовое пространство sRGB (если возможно)'''
    icc = img.info.get('icc_profile', b'')     # смотрит какой цветовой профиль
    if b'Adobe RGB' in icc:     # если профиль Adobe RGB, то конвертирует
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

def trim(img):
    '''Обрезает пустые поля у изображения (если возможно)'''
    bg = Image.new(img.mode, img.size, img.getpixel((0,0)))     # принимает за фон новое изображение, созданное по образу и подобию исходного, залитое цветом пикселя (0,0)
    diff = ImageChops.difference(img, bg)     # вычисляет разницу между исходным изображением и созданным
    #diff = ImageChops.add(diff, diff, 2.0, -10)    # какая-то магия
    bbox = diff.getbbox()     # вычисляет рамку ненулевых значений
    if bbox:
        return img.crop(bbox)     # возвращает обрезанное по рамке изображение

for infile in files:
    print (infile + "...")
    for w, h in sizes:
        img = Image.open(infile)
        img = convert_to_srgb(img)
        img = trim(img)
        img.thumbnail((w, h))     # подгоняет размер под заданные параметры в size
        if img.mode == 'RGBA':
            background = Image.new('RGBA', (img.size), (255, 255, 255, 255))     # создает белое фоновое изображение в RGBA
            img = Image.alpha_composite(background, img)     # накладывет исходный img на созданный фон
        img_jpg = img.convert('RGB')     # конвертирует png в jpg (RGBA в RGB)
        img_jpg.save((os.path.join(r'C:\Users\Katie\Desktop\resizes\result', infile[:-4])) + '-resized.jpg', 'JPEG', quality = 100)     # сохраняет с новым именем и качеством 100
print("Succsess!")
