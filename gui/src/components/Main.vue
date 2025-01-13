<template>
  <ElButton @click="handleBlackBarSeparately" type="text" :icon="Edit" class="small-btn">点我{{ inOnlyBlackBar ? "回到默认页面" : "单独处理黑边" }}</ElButton>
  <div class="center-col">
    <ElInput v-if="inOnlyBlackBar" v-model="input_file_f" placeholder="请输入图片路径" class="center-col-item"></ElInput>
    <ElInput v-else v-model="input_f" placeholder="请输入图片集文件夹路径" class="center-col-item"></ElInput>
    <ElInput v-model="output_f" placeholder="请输入输出文件夹路径" class="center-col-item"></ElInput>
    <div v-if="inOnlyBlackBar">
      <ElButton @click="getNoBlackBarImageByFile" type="primary" class="ooo">去除黑边</ElButton>
    </div>
    <div v-else style="display: flex; justify-content: center;">
      <ElButton @click="getPanorama" type="primary">开始拼接</ElButton>
      <ElButton @click="getNoBlackBarImage" type="primary" :disabled="canGetNoBlackBarImage">去除黑边</ElButton>
    </div>
  </div>
  <img :src="imgbase64 ? imgbase64 : 'GP.svg'" class="plt-img center-col-item" :style="`height: ${imgbase64 ? 'auto' : '50%'};`"></img>
</template>

<script setup>
import { ElButton, ElInput } from 'element-plus';
import { ref } from 'vue'
import { Edit } from '@element-plus/icons-vue'
import { ElLoading, ElMessage } from 'element-plus'

let input_f = ref('')
let input_file_f = ref('')
let output_f = ref('')
let imgbase64 = ref('')
let canGetNoBlackBarImage = ref(true)
let inOnlyBlackBar = ref(false)

const getPanorama = () => {
  const loading = ElLoading.service({
    lock: true,
    text: '请稍等',
    background: 'rgba(0, 0, 0, 0.7)',
  })
  if (!input_f.value || !output_f.value) {
    loading.close()
    ElMessage.error('请输入图片路径')
    return
  }
  window.pywebview.api.panorama_stitching(input_f.value, output_f.value).then((/** @type {string} */res) => {
    if (res.includes("error")) {
      ElMessage.error('拼接失败')
      console.log(res)
      loading.close()
      return
    }
    imgbase64.value = "data:image/png;base64," + res
    window.pywebview.api.base64_show_in_plt(res).then((/** @type {string} */res) => {
      if (res) {
        loading.close()
        ElMessage.success('拼接成功')
        ElMessage.success(
          "保存在" + output_f.value + "/panorama_result.png" + "，请前往查看"
        )
        canGetNoBlackBarImage.value = false
      }
    })
  })
  
}

const getNoBlackBarImage = () => {
  canGetNoBlackBarImage.value = true
  const loading = ElLoading.service({
    lock: true,
    text: '请稍等',
    background: 'rgba(0, 0, 0, 0.7)',
  })
  const base64str = imgbase64.value.substring(imgbase64.value.indexOf(',') + 1)
  window.pywebview.api.get_no_black_bar_image(base64str, output_f.value).then((/** @type {string} */res) => {
    if (res.includes("error")) {
      ElMessage.error('去除黑边失败')
      loading.close()
      return
    }
    imgbase64.value = "data:image/png;base64," + res
    window.pywebview.api.base64_show_in_plt(res).then((/** @type {string} */res) => {
      if (res) {
        loading.close()
        ElMessage.success('去除黑边成功')
        ElMessage.success(
          "保存在" + output_f.value + "/panorama_result_noblack.png" + "，请前往查看"
        )
      }
    })
  })
  
}

const getNoBlackBarImageByFile = () => {
  const loading = ElLoading.service({
    lock: true,
    text: '请稍等',
    background: 'rgba(0, 0, 0, 0.7)',
  })
  window.pywebview.api.get_no_black_bar_image_by_file(input_file_f.value, output_f.value).then((/** @type {string} */res) => {
    if (res.includes("error")) {
      ElMessage.error('去除黑边失败')
      loading.close()
      return
    }
    imgbase64.value = "data:image/png;base64," + res
    window.pywebview.api.base64_show_in_plt(res).then((/** @type {string} */res) => {
      if (res) {
        loading.close()
        ElMessage.success('去除黑边成功')
        ElMessage.success(
          "保存在" + output_f.value + "/panorama_result_noblack.png" + "，请前往查看"
        )
      }
    })
  })
  
}

const handleBlackBarSeparately = () => {
  inOnlyBlackBar.value = !inOnlyBlackBar.value
}
</script>

<style scoped>
* {
  --size-width: 70vw;
}

a {
  color: #42b983;
}

.plt-img {
  width: var(--size-width);
}

:deep(button.el-button.el-button--primary):not(.ooo) {
  width: calc(var(--size-width) / 2.025);
}

:deep(button.el-button.el-button--primary) {
  width: var(--size-width);
}

:deep(div[tabindex="-1"].el-input__wrapper) {
  width: calc(var(--size-width) - 20px);
}

.center-col-item {
  padding: 8px;
}

.small-btn {
  height: 10px;
}
</style>
