# 基于SIFT算法的全景拼接软件

---

## 介绍
本软件分为命令行版本以及图形用户界面版本。

- 命令行版本

- 图形用户界面版本
  - 基于vue-pywebview-pyinstaller二次开发
  - 我们的源码部分

```
VUE-PYWEBVIEW-PYINSTALLER
├─api
│  ├─sandbox
│  │  └─* 
│  │    (*表示所有文件) // 所有处理图像的逻辑层
│  ├─utils
│  │   └─*
│  └─[system.py] // 对逻辑层的封装以及给vue使用的接口
│    (被[]包裹表示是在原框架代码上的扩展修改)
├─gui
│  ├─public
│  │   └─*
│  ├─src
│  │  ├─components
│  │  │   └─Main.vue
│  │  ├utils
│  │  │   └─*
│  │  ├App.vue
```


---

<div class="annotation-container">
  <span class="text">注：</span>
  <div class="box">图片集所需图片尽量小于等于三张【<span class="text-important">可以尝试多次拼接</span>】</div>
  <div class="box">尺寸尽量小于1920*1080【<span class="text-important">使用压缩工具或项目脚本(minisize.py)</span>】</div>
  <div class="box code">python minisize.py -i path -wh 1920,1080</div>
  <div class="box">第二次拼接不要存在上一次路径【<span class="text-important">未开发hash命名功能</span>】</div>
</div>

<style>
.annotation-container {
  background-color: rgba(255, 255, 255, 0.8); /* 半透明白色背景 */
  border: 2px solid rgba(0, 0, 0, 0.1); /* 柔和的边框 */
  border-radius: 10px; /* 圆角 */
  padding: 20px; /* 内边距 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* 添加阴影 */
  max-width: 600px; /* 最大宽度 */
  margin: 10px auto; /* 居中对齐并上下留空隙 */
  font-family: Arial, sans-serif; /* 更加清晰的字体 */
}

.annotation-container .text {
  display: block;
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 5px;
  color: #333; /* 深灰色字体 */
}

.annotation-container .box {
  font-size: 14px;
  line-height: 1.6;
  color: #555; /* 中灰色字体 */
  padding-left: 16px; /* 为列表留出内边距 */
  position: relative;
}

.annotation-container .box::before {
  content: "\2022"; /* 添加圆点符号 */
  color: #007bff; /* 蓝色强调颜色 */
  font-size: 16px;
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%); /* 垂直居中 */
}

.text-important {
  color: #409eff;
  font-weight: bold;
}

.code {
  font-family: Consolas, monospace;
  font-size: 14px;
  background-color: #f5f5f5;
  border: 2px solid rgba(0, 0, 0, 0.1); /* 柔和的
}
</style>

---

## 致谢
[vue-pywebview-pyinstaller](https://github.com/pangao1990/PPX)
[skimae](https://github.com/scikit-image/scikit-image)
[vue](https://cn.vuejs.org/)