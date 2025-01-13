import base64
from io import BytesIO
import numpy as np
from PIL import Image

def img_as_base64(image: np.ndarray, format='PNG'):
    """
    将图像文件转换为 Base64 字符串。

    :param image_path: 图像文件路径。
    :param format: 输出的图像格式，默认是 'PNG'。
    :return: 图像的 Base64 编码字符串。
    """
    # 使用 skimage 读取图像
    
    # 将图像转换为 Pillow 图像对象
    image_pillow = Image.fromarray(image)
    
    # 使用 BytesIO 保存图像为字节流
    buffered = BytesIO()
    image_pillow.save(buffered, format=format)
    img_bytes = buffered.getvalue()
    
    # 转换为 Base64 字符串
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64

def base64_as_img(img_base64):
    # 将 Base64 字符串解码为字节流
    img_bytes = base64.b64decode(img_base64)
    image = Image.open(BytesIO(img_bytes))
    return np.array(image)