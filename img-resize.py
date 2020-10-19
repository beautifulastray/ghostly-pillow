from PIL import Image, ImageChops, ImageCms, ImageColor, ImageOps
from glob import glob
import io
import os

sizes = [[2800, 3000]]
 
os.chdir(r"/Users/Katie/resizes/raw")

files = [x for x in glob('*.jpeg') + glob('*.jpg') + glob('*.png') if not x.endswith('resized.jpg')]

def convert_to_srgb(img):
    '''Конвертирует PIL-изображение в цветовое пространство sRGB (если возможно)'''
    icc = img.info.get('icc_profile', b'')     # смотрит какой цветовой профиль
    if b'Adobe RGB' in icc:     # если профиль Adobe RGB, то конвертирует
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    if b'Adobe RGB (1998)' in icc:
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

def convert_to_srgb2(img):
    '''Конвертирует PIL-изображение в цветовое пространство sRGB (если возможно)'''
    icc = img.info.get('icc_profile')     # смотрит какой цветовой профиль
    if icc:
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

def trim(img):
    '''Обрезает пустые поля у изображения (если возможно)'''
    bg = Image.new(img.mode, img.size, img.getpixel((0,0)))     # принимает за фон новое изображение, созданное по образу и подобию исходного, залитое цветом пикселя (0,0)
    diff = ImageChops.difference(img, bg)     # вычисляет разницу между исходным изображением и созданным
    diff = ImageChops.add(diff, diff, 2.0, -17)    # какая-то магия
    bbox = diff.getbbox()     # вычисляет рамку ненулевых значений
    if bbox:
        return img.crop(bbox)     # возвращает обрезанное по рамке изображение
    else:
        return img

def ski_rotate(img):
    if img.height / img.width >= 4:
        img = img.rotate(270, resample=Image.BICUBIC, expand=1)
    return img

def ski_double(img):
    if img.width / img.height >= 10: 
        background = Image.new('RGBA', (img.width, img.height*2+80), (255, 255, 255, 255))
        background.paste(img)
        img_copy = img.copy()
        background.paste(img_copy, (0, img.height+80))
        img = background
    return img

for infile in files:
    print (infile + "...")
    for w, h in sizes:
        img = Image.open(infile).convert('RGBA')
        try:
            img = convert_to_srgb2(img)
        except ImageCms.PyCMSError:
            continue
        img = trim(img)
        img.thumbnail ((w, h))     # подгоняет размер img в рамку заданную в size
        #img = ski_rotate(img)
        #img = ski_double(img)
        #img = img.rotate(180, resample=Image.BICUBIC, expand=1)
        if img.mode == 'RGBA': 
            background = Image.new('RGBA', (img.size), (255, 255, 255, 255))     # создает белое фоновое изображение в RGBA
            img = Image.alpha_composite(background, img)     # накладывет исходный img на созданный фон        
        img_jpg = img.convert('RGB')     # конвертирует png в jpg (RGBA в RGB)
        path = infile
        root_ext = os.path.splitext(path)
        img_jpg.save((os.path.join(r'/Users/Katie/resizes/result', root_ext[0])) + '-resized.jpg', 'JPEG', quality = 100)     # сохраняет с новым именем и качеством 100
print("Succsess!")
