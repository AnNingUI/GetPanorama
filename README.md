# 基于SIFT算法的全景拼接软件

---

## 介绍
本软件分为命令行版本以及图形用户界面版本。

- 命令行版本

- 图形用户界面版本
  - 基于vue-pywebview-pyinstaller二次开发
  - 我们的源码部分

```
GetPanorama
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
- 构建指令
```bash
# 国内用户请自行切换镜像，不然会下载的很忙
# 初始化安装依赖 (必须一个单词不落，因为pnpm init是默认pnpm 的init而不是本项目的init)
pnpm run init

# 进入虚拟化
./pyapp/pyenv/pyenv/Script/activate

# 开始构建
pnpm run build
```

---

<div class="annotation-container">
  <span class="text">注：</span>
  <div class="box">图片集所需图片尽量小于等于三张【<span class="text-important">可以尝试多次拼接</span>】</div>
  <div class="box">尺寸尽量小于1920*1080【<span class="text-important">使用压缩工具或项目脚本(minisize.py)</span>】</div>
  <div class="box code">python minisize.py -i path -wh 1920,1080</div>
  <div class="box">第二次拼接不要存在上一次路径【<span class="text-important">未开发hash命名功能</span>】</div>
</div>

---

## 致谢
- [vue-pywebview-pyinstaller](https://github.com/pangao1990/PPX)
- [skimae](https://github.com/scikit-image/scikit-image)
- [vue](https://cn.vuejs.org/)