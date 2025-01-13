import numpy as np
from skimage import io, color, feature
from skimage.feature import match_descriptors
from skimage.measure import ransac
from skimage.transform import ProjectiveTransform, SimilarityTransform, warp
from skimage.util import img_as_ubyte
from pathlib import Path

class Panorama:
    """自动全景拼接"""

    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.extensions = ['jpg', 'png', 'jpeg']
        self.images = []
        self.grayscale_images = []
        self.keypoints = []
        self.descriptors = []
        self.transforms = [ProjectiveTransform()]

        if not self.input_dir.is_dir():
            raise FileNotFoundError("[错误] 输入目录不存在。")
        if not self.output_dir.is_dir():
            raise FileNotFoundError("[错误] 输出目录不存在。")

    def load_images(self):
        """加载图像并转换为灰度"""
        for ext in self.extensions:
            self.images.extend(self.input_dir.glob(f"*.{ext}"))
        if len(self.images) < 2:
            raise ValueError("[错误] 至少需要两张图像进行拼接。")
        self.images = [io.imread(img) for img in self.images]
        self.grayscale_images = [
            color.rgb2gray(img) if img.ndim == 3 else img for img in self.images
        ]

    def extract_features(self):
        """提取特征点和描述符"""
        for img in self.grayscale_images:
            sift = feature.SIFT()
            sift.detect_and_extract(img)
            self.keypoints.append(sift.keypoints)
            self.descriptors.append(sift.descriptors)

    def match_features(self, desc1, desc2):
        """匹配两个图像的特征点"""
        matches = match_descriptors(desc1, desc2, cross_check=True)
        return matches

    def compute_transforms(self):
        """计算投影变换矩阵"""
        for i in range(1, len(self.grayscale_images)):
            matches = self.match_features(
                self.descriptors[i - 1], self.descriptors[i]
            )
            src = self.keypoints[i][matches[:, 1]][:, ::-1]
            dst = self.keypoints[i - 1][matches[:, 0]][:, ::-1]
            model, inliers = ransac(
                (src, dst),
                ProjectiveTransform,
                min_samples=4,
                residual_threshold=2,
                max_trials=500,
            )
            self.transforms.append(
                ProjectiveTransform(model.params @ self.transforms[-1].params) # type: ignore
            )

    def stitch_images(self):
        """拼接图像"""
        # 计算图像变换后的角点范围
        corners = []
        for img, transform in zip(self.images, self.transforms):
            r, c = img.shape[:2]
            corners.append(
                transform([[0, 0], [0, r], [c, 0], [c, r]])
            )
        corners = np.vstack(corners)
        min_coords = corners.min(axis=0)
        max_coords = corners.max(axis=0)
        output_shape = (np.ceil(max_coords - min_coords)[::-1]).astype(int)

        # 创建全景图和权重矩阵
        panorama = np.zeros((output_shape[0], output_shape[1], 3), dtype=np.float32)
        weights = np.zeros((output_shape[0], output_shape[1]), dtype=np.float32)

        offset = SimilarityTransform(translation=-min_coords)
        for img, transform in zip(self.images, self.transforms): # type: ignore
            warp_img = warp(
                img, (transform + offset).inverse, output_shape=output_shape[:2]
            )
            mask = (warp_img > 0).astype(np.float32)
            mask = mask.mean(axis=-1)  # 将三通道的 mask 转换为单通道
            weights += mask
            k = warp_img * mask[..., np.newaxis]
            if not np.all(panorama == 0):
                overlap_mask = panorama[:, :, 0] != 0
                for c in range(panorama.shape[2]):  # 遍历每个颜色通道
                    panorama[overlap_mask, c] = (panorama[overlap_mask, c] * (1 - mask[overlap_mask]) + 
                                     k[overlap_mask, c] * mask[overlap_mask])
                panorama[panorama == 0] += k[panorama == 0]
            else:
                panorama += k
        return img_as_ubyte(panorama)

    def save_panorama(self, panorama: np.ndarray):
        """保存拼接结果"""
        output_path = self.output_dir / "panorama_result.jpg"
        io.imsave(output_path, panorama)
        from api.sandbox.utils.img import img_as_base64
        encoded_image = img_as_base64(panorama)
        print(f"[INFO] 全景图保存到 {output_path}")
        return encoded_image

    def run(self):
        """运行全景拼接流程"""
        print("[INFO] 加载图像...")
        self.load_images()
        print("[INFO] 提取特征点...")
        self.extract_features()
        print("[INFO] 计算变换矩阵...")
        self.compute_transforms()
        print("[INFO] 拼接图像...")
        panorama = self.stitch_images()
        print("[INFO] 保存拼接结果...")
        encoded_image = self.save_panorama(panorama)
        print("[INFO] 全景拼接完成！")
        
        return encoded_image


