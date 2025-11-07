<template>
  <div style="max-width:800px;margin:40px auto;font-family:system-ui">
    <!-- Image Carousel for Gesture Control -->
    <div style="margin-bottom: 24px;">
      <h3>手势控制演示区域</h3>
      <div style="position: relative; width: 100%; max-width:640px; margin: auto; border: 2px solid #666; padding: 8px;">
        <img :src="images[currentImageIndex]" style="width: 100%; display: block;" />
        <div style="position: absolute; top: 8px; left: 12px; background: rgba(0,0,0,0.5); color: white; padding: 4px 8px; border-radius: 4px;">
          图片 {{ currentImageIndex + 1 }} / {{ images.length }}
        </div>
        <div v-if="lastGesture" style="position: absolute; top: 8px; right: 12px; background: #1E90FF; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">
          {{ lastGesture === 'swipe_right' ? '→ 右挥' : '← 左挥' }}
        </div>
      </div>
    </div>

    <hr style="margin:28px 0" />

    <h2>YOLO + LLM 同步演示</h2>
    <form @submit.prevent="onSubmit">
      <div style="margin:12px 0">
        <input type="file" accept="image/*" @change="onFile" />
      </div>
      <div style="margin:12px 0">
        <input v-model="question" placeholder="输入你的问题" style="width:100%;padding:8px" />
      </div>
      <button :disabled="loading">{{ loading ? '处理中...' : '提交' }}</button>
    </form>
    <div v-if="answer" style="margin-top:16px;padding:12px;border:1px solid #ddd">
      <b>答案：</b>
      <div>{{ answer }}</div>
    </div>

    <hr style="margin:28px 0" />
    <h3>实时摄像头分析 (WebSocket)</h3>
    <div style="margin:12px 0; display:flex; gap:12px; align-items:center; flex-wrap:wrap">
      <select v-model="selectedDeviceId" @change="onDeviceChange" style="min-width:220px">
        <option v-for="d in devices" :key="d.deviceId" :value="d.deviceId">
          {{ d.label || ('摄像头 ' + (d.index+1)) }}
        </option>
      </select>
      <button @click="toggleRealtimeRelation">{{ realtimeRelationOn ? '停止实时分析' : '开启摄像头实时分析' }}</button>
      <span v-if="wsError" style="color:#c00">{{ wsError }}</span>
    </div>
    <div style="display:flex; gap:16px; align-items:flex-start; flex-wrap:wrap">
      <video ref="videoRef" autoplay playsinline style="width:320px; background:#000"></video>
      <div>
        <p v-if="realtimeRelationOn && relationActions.length"><b>识别到的动作:</b> {{ relationActions.join('；') }}</p>
        <p v-if="!realtimeRelationOn && !wsError">请开启实时分析以进行手势控制</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onBeforeUnmount, onMounted } from 'vue'

// --- Carousel State ---
const images = ref([
  'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=640', // Cat
  'https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=640', // Book
  'https://images.unsplash.com/photo-1503220317375-aaad61436b1b?w=640', // Mountain
])
const currentImageIndex = ref(0)
const lastGesture = ref('')
let gestureTimeout = null

function nextImage() {
  currentImageIndex.value = (currentImageIndex.value + 1) % images.value.length
}
function prevImage() {
  currentImageIndex.value = (currentImageIndex.value - 1 + images.value.length) % images.value.length
}

// --- YOLO + LLM State ---
const file = ref(null)
const question = ref('这张图里有什么？')
const loading = ref(false)
const answer = ref('')

function onFile(e){ file.value = e.target.files?.[0] || null }

async function onSubmit(){
  if(!file.value){ alert('请选择图片'); return }
  loading.value = true
  answer.value = ''
  try{
    const fd = new FormData()
    fd.append('image', file.value)
    fd.append('question', question.value)
    const resp = await axios.post('http://127.0.0.1:8080/api/ai/ask-sync', fd)
    answer.value = resp.data
  }catch(e){
    answer.value = '请求失败: ' + (e?.response?.data || e.message)
  }finally{
    loading.value = false
  }
}

// --- Realtime WS State ---
const videoRef = ref(null)
const realtimeRelationOn = ref(false)
const wsError = ref('')
const devices = ref([])
const selectedDeviceId = ref('')
const relationActions = ref([])

let mediaStream = null
let wsRelation = null
let relationTimer = null

// --- Gesture Mappings ---
const gestureMappings = ref({})

async function fetchConfig() {
  try {
    // 获取全局配置 (不指定用户/应用)
    const resp = await axios.get('http://127.0.0.1:8080/api/config', { params: { os: 'any' } })
    const mappings = resp.data?.mappings || []
    const webActions = {}
    mappings.forEach(m => {
      if (m.action?.type === 'WEB_ACTION') {
        webActions[m.code] = m.action.value
      }
    })
    gestureMappings.value = webActions
    console.log('Gesture mappings loaded:', webActions)
  } catch (e) {
    wsError.value = '获取手势配置失败: ' + (e?.response?.data || e.message)
  }
}

// --- Core Logic ---
async function refreshDevices(){
  try{
    const list = await navigator.mediaDevices.enumerateDevices()
    devices.value = list.filter(d => d.kind === 'videoinput').map((d, i) => ({...d, index: i}))
    if(!selectedDeviceId.value && devices.value.length){ selectedDeviceId.value = devices.value[0].deviceId }
  }catch(e){ wsError.value = '无法获取摄像头列表: ' + (e?.message || e) }
}

async function startMediaStream(){
  if(mediaStream){ mediaStream.getTracks().forEach(t => t.stop()); mediaStream = null }
  const constraints = { video: { width: 320, height: 240 } }
  if(selectedDeviceId.value){ constraints.video.deviceId = { exact: selectedDeviceId.value } }
  mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
  videoRef.value.srcObject = mediaStream
}

async function onDeviceChange(){
  if(realtimeRelationOn.value){
    try{ await startMediaStream() }catch(e){ wsError.value = '切换摄像头失败: ' + (e?.message || e) }
  }
}

function toggleRealtimeRelation(){
  if(realtimeRelationOn.value){ stopRealtimeRelation(); return }
  startRealtimeRelation()
}

async function startRealtimeRelation(){
  wsError.value = ''
  try {
    if(devices.value.length === 0) await refreshDevices()
    await startMediaStream()
    await fetchConfig() // 获取配置
  } catch (e) {
    wsError.value = '无法开启摄像头或获取配置: ' + (e?.message || e)
    return
  }

  try{
    wsRelation = new WebSocket('ws://127.0.0.1:8000/ws/analyze')
  }catch(e){
    wsError.value = '连接分析WS失败: ' + (e?.message || e)
    return
  }

  wsRelation.onopen = () => {
    realtimeRelationOn.value = true
    const sendFrame = () => {
      if(!realtimeRelationOn.value || wsRelation.readyState !== WebSocket.OPEN || !videoRef.value?.srcObject) return
      const tmp = document.createElement('canvas')
      tmp.width = 320; tmp.height = 240
      const tctx = tmp.getContext('2d')
      tctx.drawImage(videoRef.value, 0, 0, tmp.width, tmp.height)
      tmp.toBlob(b => {
        if(!b) return
        const fr = new FileReader()
        fr.onloadend = () => { if(wsRelation?.readyState === WebSocket.OPEN) wsRelation.send(fr.result) }
        fr.readAsDataURL(b)
      }, 'image/jpeg', 0.8)
    }
    relationTimer = setInterval(sendFrame, 500) // ~2 FPS
  }

  wsRelation.onmessage = ev => {
    try{
      const data = JSON.parse(ev.data)
      const actions = Array.isArray(data?.actions) ? data.actions : []
      relationActions.value = actions
      // --- Handle Gestures ---
      handleGesture(actions)
    }catch(_){ }
  }
  wsRelation.onerror = () => { wsError.value = '分析WS发生错误' }
  wsRelation.onclose = () => { stopRealtimeRelation() }
}

function stopRealtimeRelation(){
  realtimeRelationOn.value = false
  relationActions.value = []
  if(relationTimer){ clearInterval(relationTimer); relationTimer = null }
  if(wsRelation && wsRelation.readyState === WebSocket.OPEN){ try{ wsRelation.close() }catch(_){} }
  wsRelation = null
  if(mediaStream){ mediaStream.getTracks().forEach(t => t.stop()); mediaStream = null }
}

function handleGesture(actions) {
  // 防抖，如果正在冷却中，则不处理新的手势
  if (gestureTimeout) return

  const gesture = actions.find(a => a.startsWith('swipe_'))
  if (!gesture) return

  const action = gestureMappings.value[gesture]
  if (action === 'carousel_next') {
    nextImage()
  } else if (action === 'carousel_prev') {
    prevImage()
  }

  if (action) {
    lastGesture.value = gesture
    // 设置一个冷却时间 (e.g., 1.5秒) 来显示手势并防止重复触发
    gestureTimeout = setTimeout(() => {
      gestureTimeout = null
      lastGesture.value = ''
    }, 1500)
  }
}

onBeforeUnmount(() => { 
  stopRealtimeRelation()
  if(navigator.mediaDevices?.removeEventListener){
    navigator.mediaDevices.removeEventListener('devicechange', refreshDevices)
  }
})

onMounted(async () => {
  await refreshDevices()
  if(navigator.mediaDevices?.addEventListener){
    navigator.mediaDevices.addEventListener('devicechange', refreshDevices)
  }
})

</script>

<style>
button{ padding:8px 16px; cursor: pointer; }
button:disabled { cursor: not-allowed; opacity: 0.6; }
</style>