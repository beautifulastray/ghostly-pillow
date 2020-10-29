from PIL import Image, ImageChops, ImageCms, ImageColor, ImageOps
from glob import glob
import io
import os

sizes = [[2500, 2500]]
 
os.chdir(r"/Users/Katie/resizes/raw")

files = [x for x in glob('*.jpeg') + glob('*.jpg') + glob('*.png') if not x.endswith('resized.jpg')]

def convert_to_srgb(img):
    '''Конвертирует PIL-изображение в цветовое пространство sRGB (если возможно)'''
    icc = img.info.get('icc_profile')
    #Смотрит какой цветовой профиль имеет изображение
    if icc:
        io_handle = io.BytesIO(icc)
        #Virtual file - записывает данные ICC в буфер
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

def trim(img):
    '''Обрезает пустые поля у изображения (если возможно)'''
    bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
    #Принимает за фон новое изображение, созданное по образу и подобию исходного, залитое цветом пикселя (0,0)
    diff = ImageChops.difference(img, bg)
    #Вычисляет разницу между исходным изображением и созданным
    diff = ImageChops.add(diff, diff, 1.0, -17)
    #Какая-то магия
    bbox = diff.getbbox()
    #Вычисляет рамку ненулевых значений
    if bbox:
        return img.crop(bbox)
        #Возвращает обрезанное по рамке изображение
    else:
        return img

def ski_rotate(img):
    '''Поворачивает изображение, если оно соответствует заданной пророрции'''
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
        img.thumbnail((w, h))
        #Подгоняет размер img под рамку заданную в sizes, уменьшает img, если необходимо
        img = ski_rotate(img)
        img = ski_double(img)

        if img.mode == 'RGBA': 
            background = Image.new('RGBA', (img.size), (255, 255, 255, 255))
            #Создает белое фоновое изображение в RGBA
            img = Image.alpha_composite(background, img)
            #Накладывет исходный img на созданный фон
            img = img.convert('RGB')
            #Конвертирует png в jpg (RGBA в RGB)

        if img.mode == 'P':
            img = img.convert('RGBA')
            #Конвертирует индексированную палитру в RGBA
            background = Image.new('RGBA', (img.size), (255, 255, 255, 255))
            #Создает белое фоновое изображение в RGBA
            img = Image.alpha_composite(background, img)
            #Накладывет исходный img на созданный фон
            img = img.convert('RGB')
            #Конвертирует png в jpg (RGBA в RGB)

        path = infile
        root_ext = os.path.splitext(path)
        #Разбивает имя файла на две части: до точки(root или [1]) и после(ext или [0])
        img.save((os.path.join(r'/Users/Katie/resizes/result', root_ext[0])) + '-resized.jpg', 'JPEG', quality = 100)
        #Cохраняет изображение с новым именем и качеством 100 в формате JPEG
print("Succsess!")
