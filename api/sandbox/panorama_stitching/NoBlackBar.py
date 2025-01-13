import numpy as np
from skimage import restoration, color, filters
from PIL import ImageFile
from PIL import Image

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 150000000  # 根据需要调整限制

class NoBlackBar:
    def __init__(self, image):
        # 初始化类，加载图像并创建灰度图像的二值副本
        self.image = image
        self.image_cp = self.image.copy()  # 备份原始图像
        self.gray_img = color.rgb2gray(self.image_cp)  # 转换为灰度图像

        # 对灰度图像进行高斯模糊，消除拼接线
        self.blurred_img = filters.gaussian(self.gray_img, sigma=2)

        # 二值化模糊图像，非零值置为1
        self.binary_img = (self.blurred_img > 0.001).astype(np.uint8)

    def max_inner_rectangle(self):
        """
        使用最大内接矩形算法找到二值图像中包含非黑色像素的最大矩形区域。
        思路:
        1. 构建一个高度矩阵，其中每个位置的值表示以该位置为底部的连续非黑像素列的高度。
        2. 对于高度矩阵的每一行，利用单调栈计算最大矩形面积。
        3. 记录最大的矩形面积及其坐标。
        """
        rows, cols = self.binary_img.shape

        # 计算高度矩阵
        height = np.zeros_like(self.binary_img, dtype=np.int32)
        height[0, :] = self.binary_img[0, :]
        for i in range(1, rows):
            height[i, :] = (height[i - 1, :] + 1) * self.binary_img[i, :]

        # 计算最大内接矩形
        max_area = 0
        best_rect = None

        for i in range(rows):
            stack = []
            for j in range(cols + 1):
                current_height = height[i, j] if j < cols else 0

                while stack and current_height < height[i, stack[-1]]:
                    h = height[i, stack.pop()]
                    w = j if not stack else j - stack[-1] - 1
                    area = h * w
                    if area > max_area:
                        max_area = area
                        best_rect = (i - h + 1, stack[-1] + 1 if stack else 0, i + 1, j)

                stack.append(j)

        return best_rect

    def crop_to_rectangle(self):
        """
        根据最大内接矩形裁剪图像。
        """
        rect = self.max_inner_rectangle()
        if rect:
            top, left, bottom, right = rect
            self.image = self.image[top:bottom, left:right]
            self.binary_img = self.binary_img[top:bottom, left:right]

    def process(self):
        """
        执行完整的裁剪和修复逻辑。
        思路:
        1. 调用 `crop_to_rectangle` 方法裁剪图像到最大内接矩形。
        2. 识别裁剪后图像中的黑色像素位置，创建修复掩膜。
        3. 使用 `inpaint_biharmonic` 修复黑色区域，生成无黑边图像。
        4. 将修复后的图像转换为 `uint8` 格式以便保存。
        """
        self.crop_to_rectangle()

        # 修复剩余小部分黑边
        mask = np.all(self.image == [0, 0, 0], axis=-1)
        inpainted_image = restoration.inpaint.inpaint_biharmonic(self.image, mask, channel_axis=-1)

        # 将图像值归一化到 [0, 1]，然后转换为 uint8 类型
        inpainted_image = (np.clip(inpainted_image, 0, 1) * 255).astype(np.uint8)
        return inpainted_image