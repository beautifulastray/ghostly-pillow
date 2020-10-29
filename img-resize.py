from PIL import Image, ImageChops, ImageCms, ImageColor, ImageOps
from glob import glob
import io
import os

sizes = [[2500, 2500]]
 
os.chdir(r"/Users/Katie/resizes/raw")

files = [x for x in glob('*.jpeg') + glob('*.jpg') + glob('*.png') if not x.endswith('resized.jpg')]

def convert_to_srgb(img):
    '''Конвертирует PIL-изображение в цветовое пространство sRGB (если возможно)'''
    #Смотрит какой цветовой профиль имеет изображение
    icc = img.info.get('icc_profile')
    if icc:
        #Virtual file - записывает данные ICC в буфер
        io_handle = io.BytesIO(icc)
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

def trim(img):
    '''Обрезает пустые поля у изображения (если возможно)'''
    #Принимает за фон новое изображение, созданное по образу и подобию исходного, залитое цветом пикселя (0,0)
    bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
    #Вычисляет разницу между исходным изображением и созданным
    diff = ImageChops.difference(img, bg)
    #Какая-то магия
    diff = ImageChops.add(diff, diff, 1.0, -17)
    #Вычисляет рамку ненулевых значений
    bbox = diff.getbbox()
    if bbox:
        #Возвращает обрезанное по рамке изображение
        return img.crop(bbox)
    else:
        return img

def ski_rotate(img):
    '''Поворачивает изображение, если оно соответствует заданной пропорции'''
    if img.height / img.width >= 4.8:
        img = img.rotate(270, resample=Image.BICUBIC, expand=1)
    return img

def ski_double(img):
    '''Создает копию изображения и размещает на холсте оригинал и копию с заданным отступом'''
    if img.width / img.height >= 10:
        background = Image.new('RGBA', (img.width, img.height*2+50), (255, 255, 255, 255))
        background.paste(img)
        img_copy = img.copy()
        background.paste(img_copy, (0, img.height+50))
        img = background
    return img

for infile in files:
    print(infile + "...")
    for w, h in sizes:
        img = Image.open(infile)

        try:
            img = convert_to_srgb(img)
        except ImageCms.PyCMSError:
            continue

        img = trim(img)
        #Подгоняет размер img под рамку заданную в sizes, уменьшает img, если необходимо
        img.thumbnail((w, h))
        img = ski_rotate(img)
        img = ski_double(img)

        if img.mode == 'RGBA': 
            #Создает белое фоновое изображение в RGBA
            background = Image.new('RGBA', (img.size), (255, 255, 255, 255))
            #Накладывет исходный img на созданный фон
            img = Image.alpha_composite(background, img)
            #Конвертирует png в jpg (RGBA в RGB)
            img = img.convert('RGB')

        if img.mode == 'P':
            #Конвертирует индексированную палитру в RGBA
            img = img.convert('RGBA')
            #Создает белое фоновое изображение в RGBA
            background = Image.new('RGBA', (img.size), (255, 255, 255, 255))
            #Накладывет исходный img на созданный фон
            img = Image.alpha_composite(background, img)
            #Конвертирует png в jpg (RGBA в RGB)
            img = img.convert('RGB')

        path = infile
        #Разбивает имя файла на две части: до точки(root или [1]) и после(ext или [0])
        root_ext = os.path.splitext(path)
        #Cохраняет изображение с новым именем и качеством 100 в формате JPEG
        img.save((os.path.join(r'/Users/Katie/resizes/result', root_ext[0])) + '-resized.jpg', 'JPEG', quality = 100)
print("Succsess!")
