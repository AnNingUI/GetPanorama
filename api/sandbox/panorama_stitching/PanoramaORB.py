import matplotlib.pyplot as plt
import numpy as np
from sys import exit
from pathlib import Path
from skimage.feature import ORB
from skimage.transform import warp
from skimage.measure import ransac
from skimage.color import rgb2gray
from skimage.io import ImageCollection
from skimage.io import imsave
from skimage.feature import match_descriptors
from skimage.transform import SimilarityTransform
from skimage.transform import ProjectiveTransform
from skimage.util import img_as_ubyte


class Panorama:
    '''自动全景拼接

    参数
    ----------
    in_dir : str
        存储用于创建全景图的图像的目录。
    out_dir : str
        保存输出全景图的目录。
    '''

    def __init__(self, in_dir, out_dir):
        self.extension = ['jpg', 'png', 'JPG', 'PNG']

        if not Path(out_dir).is_dir():
            exit("[错误] 输出目录不存在。")

        self.out = out_dir
        self.load(in_dir)

    def load(self, in_dir):
        '''加载 in_dir 中的图像'''

        # 加载图像
        if not Path(in_dir).is_dir():
            exit("[错误] 输入目录不存在。")

        p = [f'{str(Path(in_dir))}/*.{ex}' for ex in self.extension]
        self.images = ImageCollection(p)
        self.num_imgs = len(self.images)

        if self.num_imgs < 2:
            exit("[错误] 没有图像。")

        # 将图像转换为灰度图像
        self.grays = [rgb2gray(img) for img in self.images]

    def extract_features(self):
        '''提取兴趣点及其特征向量（描述符）'''

        self.keypoints, self.descriptors, self.corners = [
        ], [], np.empty((self.num_imgs, 4, 2))
        orb = ORB(n_keypoints=1000, fast_threshold=0.05)

        for idx, img in enumerate(self.grays):
            # 提取兴趣点及其特征
            orb.detect_and_extract(img)
            self.keypoints.append(orb.keypoints)
            self.descriptors.append(orb.descriptors)

            # 获取图像的四个角
            r, c = img.shape
            self.corners[idx] = np.array([[0, 0], [0, r], [c, 0], [c, r]])

    def match_features(self):
        self.tforms = [ProjectiveTransform()]
        self.new_corners = np.copy(self.corners)

        for i in range(1, self.num_imgs):
            # 找到 I(n) 和 I(n-1) 之间的对应关系。
            matches = match_descriptors(
                self.descriptors[i-1], self.descriptors[i], cross_check=True)

            # 估计 I(n) 和 I(n-1) 之间的变换。
            src = self.keypoints[i][matches[:, 1]][:, ::-1]
            dst = self.keypoints[i-1][matches[:, 0]][:, ::-1]

            model, _ = ransac((src, dst), ProjectiveTransform,
                              4, residual_threshold=2, max_trials=2000)
            self.tforms.append(ProjectiveTransform(
                model.params @ self.tforms[-1].params)) # type: ignore

            # 计算由模型变换后的新角点
            self.new_corners[i] = self.tforms[-1](self.corners[i])

        corners_min = np.min(self.new_corners, axis=1)
        corners_max = np.max(self.new_corners, axis=1)

        self.xLim = corners_max[:, 0] - corners_min[:, 0]
        self.yLim = corners_max[:, 1] - corners_min[:, 1]

    def adjust_center(self):
        '''反转中心图像的变换并将该变换应用于所有其他图像以创建更美观的全景图。'''

        # 找到中心图像，假设场景总是水平的
        xCenterIdx = np.argsort(self.xLim)[self.num_imgs//2]
        centerTform = np.copy(self.tforms[xCenterIdx].params)
        invCenterTform = np.linalg.inv(centerTform)

        for i in range(self.num_imgs):
            self.tforms[i].params = self.tforms[i].params @ invCenterTform
            self.new_corners[i] = self.tforms[i](self.corners[i])

        # 重新计算调整中心后的图像角点。
        corners_min = np.min(self.new_corners, axis=1)
        corners_max = np.max(self.new_corners, axis=1)

        self.corner_min = np.min(corners_min, axis=0)
        self.corner_max = np.max(corners_max, axis=0)

        self.output_shape = self.corner_max - self.corner_min
        self.output_shape = np.ceil(self.output_shape[::-1]).astype(int)

    def stitch(self):
        pano_warped, pano_mask = [], []
        # 将图像平移到正确位置以便完整显示。
        offset = SimilarityTransform(translation=-self.corner_min)

        for i in range(self.num_imgs):
            # 对所有变换应用偏移
            self.tforms[i] += offset
            # 对图像应用变换
            pano_warped.append(warp(self.images[i], self.tforms[i].inverse, order=0,
                                    output_shape=self.output_shape, cval=-1))

            # 找到掩码以去除重叠区域
            # 掩码在图像内为 1
            pano_mask.append((pano_warped[-1] != -1)*1)

            # 从之前的掩码中移除重叠区域
            if i > 0:
                overlap = pano_mask[-1] - pano_mask[-2]
                plt.show()
                pano_mask[-2] = np.where(overlap < 0, 0, pano_mask[-2])

        # 将它们拼接在一起
        self.panorama = np.zeros_like(pano_warped[0]).astype(np.uint8)
        for i in range(self.num_imgs):
            k = (pano_warped[i].astype(np.float64) * pano_mask[i].astype(np.float64)).astype(np.uint8)
            self.panorama[self.panorama == 0] = k[self.panorama == 0]
        
        # 归一化
        # self.panorama[self.panorama > 1] = 1
        self.panorama[self.panorama < 0] = 0

        return img_as_ubyte(self.panorama)

    def save(self):
        imsave(Path(self.out).joinpath('panorama_out.png'), self.panorama)

    def run(self):
        self.extract_features()
        self.match_features()
        self.adjust_center()
        panorama = self.stitch()
        self.save()
        from api.sandbox.utils.img import img_as_base64
        encoded_image = img_as_base64(panorama)
        return encoded_image