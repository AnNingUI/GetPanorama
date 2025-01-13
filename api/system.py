#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
vue-pywebview-pyinstaller:
    Author: 潘高
'''

import getpass
import json
import os
import subprocess
from matplotlib import pyplot as plt
import skimage
import webview # type: ignore
from pathlib import Path
from api.sandbox.utils.img import img_as_base64
from pyapp.config.config import Config
from pyapp.update.update import AppUpdate


class System():
    '''系统类'''

    _window = None

    # ==========================================================================================================
    def system_py2js(self, func, info):
        '''调用js中挂载到window的函数'''
        infoJson = json.dumps(info)
        System._window.evaluate_js(f"{func}('{infoJson}')") # type: ignore

    def system_getAppInfo(self):
        '''程序基础配置信息'''
        return {
            'appName': Config.appName,  # 应用名称
            'appVersion': Config.appVersion  # 应用版本号
        }

    def system_checkNewVersion(self):
        '''检查更新'''
        appUpdate = AppUpdate()    # 程序更新类
        res = appUpdate.check()
        return res

    def system_downloadNewVersion(self):
        '''下载新版本'''
        appUpdate = AppUpdate()    # 程序更新类
        res = appUpdate.run()
        return res

    def system_cancelDownloadNewVersion(self):
        '''取消下载新版本'''
        appUpdate = AppUpdate()    # 程序更新类
        res = appUpdate.cancel()
        return res

    def system_getOwner(self):
        # 获取本机用户名
        return getpass.getuser()

    def system_pyOpenFile(self, path):
        '''用电脑默认软件打开本地文件'''
        # 判断以下当前系统类型
        if Config.appIsMacOS:
            path = path.replace("\\", "/")
            subprocess.call(["open", path])
        else:
            path = path.replace("/", "\\")
            os.startfile(path)

    def system_pyCreateFileDialog(self, fileTypes=['全部文件 (*.*)'], directory=''):
        '''打开文件对话框'''
        # 可选文件类型
        # fileTypes = ['Excel表格 (*.xlsx;*.xls)']
        fileTypes = tuple(fileTypes)    # 要求必须是元组
        result = System._window.create_file_dialog(dialog_type=webview.OPEN_DIALOG, directory=directory, allow_multiple=True, file_types=fileTypes) # type: ignore
        resList = list()
        if result is not None:
            for res in result:
                filePathList = os.path.split(res)
                dir = filePathList[0]
                filename = filePathList[1]
                ext = os.path.splitext(res)[-1]
                resList.append({
                    'filename': filename,
                    'ext': ext,
                    'dir': dir,
                    'path': res
                })
        return resList

    def panorama_stitching(self, input_dir, output_dir):
        """重点运行全景拼接函数"""
        try:
            import api.sandbox.panorama_stitching.Panorama as ps
            panorama = ps.Panorama(input_dir, output_dir)
            encoded_image = panorama.run()
            return encoded_image
        except Exception as e:
            print(e)
            return f"error,{e}"
    # ==========================================================================================================
    
    def get_no_black_bar_image(self, base64Image, output_dir):
        """重点运行去除黑边"""
        try:
            import api.sandbox.panorama_stitching.NoBlackBar as nb
            from api.sandbox.utils.img import base64_as_img
            image = base64_as_img(base64Image)
            no_black_bar = nb.NoBlackBar(image)
            no_black_bar_image = no_black_bar.process()
            no_black_bar_image_base64 = img_as_base64(image=no_black_bar_image) # type: ignore
            output = Path(output_dir) / "panorama_result_noblack.png"
            skimage.io.imsave(output, no_black_bar_image)
            return no_black_bar_image_base64
        except Exception as e:
            return f"error,{e}"
        
    def get_no_black_bar_image_by_file(self, input_file, output_dir):
        try:
            import api.sandbox.panorama_stitching.NoBlackBar as nb
            image = skimage.io.imread(input_file)
            no_black_bar = nb.NoBlackBar(image)
            no_black_bar_image = no_black_bar.process()
            no_black_bar_image_base64 = img_as_base64(image=no_black_bar_image) # type: ignore
            output = Path(output_dir) / "panorama_result_noblack.png"
            skimage.io.imsave(output, no_black_bar_image)
            return no_black_bar_image_base64
        except Exception as e:
            return f"error,{e}"
    def base64_show_in_plt(self, base64Image):
        try:
            import api.sandbox.utils.img as iu
            image = iu.base64_as_img(base64Image)
            plt.imshow(image)
            plt.show()
            return "matplotlib 展示全景图"
        except Exception as e:
            return str(e)
        