<template>
  <div style="max-width:680px;margin:40px auto;font-family:system-ui">
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
    <h3>实时摄像头检测 (WebSocket)</h3>
    <div style="margin:12px 0; display:flex; gap:12px; align-items:center; flex-wrap:wrap">
      <select v-model="selectedDeviceId" @change="onDeviceChange" style="min-width:220px">
        <option v-for="d in devices" :key="d.deviceId" :value="d.deviceId">
          {{ d.label || ('摄像头 ' + (d.index+1)) }}
        </option>
      </select>
      <button @click="toggleRealtime">{{ realtimeOn ? '停止实时检测' : '开启摄像头实时检测' }}</button>
      <span v-if="wsError" style="color:#c00">{{ wsError }}</span>
      <span v-if="realtimeOn && lastObjects.length">检测: {{ lastObjects.join(', ') }}</span>
    </div>
    <div style="display:flex; gap:16px; align-items:flex-start; flex-wrap:wrap">
      <video ref="videoRef" autoplay playsinline style="width:320px; background:#000"></video>
      <canvas ref="canvasRef" width="320" height="240" style="display:none"></canvas>
    </div>
    <div style="margin-top:12px; display:flex; gap:12px; align-items:center; flex-wrap:wrap">
      <button @click="analyzeCurrentFrameEmotion" :disabled="!videoRef || !videoRef.srcObject">分析当前帧情绪</button>
      <span v-if="currentEmotion">情绪：{{ currentEmotion }}</span>
    </div>
    <div style="margin-top:12px; display:flex; gap:12px; align-items:center; flex-wrap:wrap">
      <button @click="analyzeCurrentFrameRelation" :disabled="!videoRef || !videoRef.srcObject">分析当前帧关系</button>
      <span v-if="relationActions.length">关系：{{ relationActions.join('；') }}</span>
    </div>
    <div style="margin-top:8px; display:flex; gap:12px; align-items:center; flex-wrap:wrap">
      <button @click="toggleRealtimeRelation">{{ realtimeRelationOn ? '停止实时关系' : '开启实时关系(低频)' }}</button>
      <span v-if="realtimeRelationOn && relationActions.length">实时关系：{{ relationActions.join('；') }}</span>
    </div>
  </div>
  </template>

<script setup>
import axios from 'axios'
import { ref, onBeforeUnmount, onMounted } from 'vue'

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
    const resp = await axios.post('http://127.0.0.1:8080/api/ai/ask-sync', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    answer.value = resp.data
  }catch(e){
    answer.value = '请求失败: ' + (e?.response?.data || e.message)
  }finally{
    loading.value = false
  }
}

// Realtime WS
const videoRef = ref(null)
const canvasRef = ref(null)
const realtimeOn = ref(false)
const wsError = ref('')
const lastObjects = ref([])
const devices = ref([]) // 可用摄像头列表
const selectedDeviceId = ref('')
const currentEmotion = ref('')
const relationActions = ref([])
const realtimeRelationOn = ref(false)
let wsRelation = null
let relationTimer = null
let mediaStream = null
let ws = null
let timer = null

async function refreshDevices(){
  try{
    const list = await navigator.mediaDevices.enumerateDevices()
    const cams = list.filter(d => d.kind === 'videoinput').map((d, i) => ({...d, index: i}))
    devices.value = cams
    if(!selectedDeviceId.value && cams.length){ selectedDeviceId.value = cams[0].deviceId }
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
  if(realtimeOn.value){
    try{ await startMediaStream() }catch(e){ wsError.value = '切换摄像头失败: ' + (e?.message || e) }
  }
}

async function analyzeCurrentFrameRelation(){
  if(!videoRef.value) return
  const tmp = document.createElement('canvas')
  tmp.width = 320; tmp.height = 240
  const tctx = tmp.getContext('2d')
  tctx.drawImage(videoRef.value, 0, 0, tmp.width, tmp.height)
  const blob = await new Promise(resolve => tmp.toBlob(resolve, 'image/jpeg', 0.8))
  const fd = new FormData()
  fd.append('file', blob, 'frame.jpg')
  try {
    const resp = await axios.post('http://127.0.0.1:8000/analyze/file', fd)
    const actions = Array.isArray(resp?.data?.actions) ? resp.data.actions : []
    relationActions.value = actions
  } catch (e){
    const data = e?.response?.data
    const msg = (data && typeof data === 'object') ? (data.detail || JSON.stringify(data)) : (data || e.message)
    wsError.value = '关系分析失败: ' + msg
  }
}

function toggleRealtimeRelation(){
  if(realtimeRelationOn.value){ stopRealtimeRelation(); return }
  startRealtimeRelation()
}

function startRealtimeRelation(){
  if(!videoRef.value) return
  wsError.value = ''
  try{
    wsRelation = new WebSocket('ws://127.0.0.1:8000/ws/analyze')
  }catch(e){
    wsError.value = '连接关系WS失败: ' + (e?.message || e)
    return
  }
  wsRelation.onopen = () => {
    realtimeRelationOn.value = true
    const sendFrame = () => {
      if(!realtimeRelationOn.value || wsRelation.readyState !== WebSocket.OPEN) return
      const tmp = document.createElement('canvas')
      tmp.width = 320; tmp.height = 240
      const tctx = tmp.getContext('2d')
      tctx.drawImage(videoRef.value, 0, 0, tmp.width, tmp.height)
      tmp.toBlob(b => {
        if(!b) return
        const fr = new FileReader()
        fr.onloadend = () => { wsRelation?.send(fr.result) }
        fr.readAsDataURL(b)
      }, 'image/jpeg', 0.8)
    }
    relationTimer = setInterval(sendFrame, 1000) // ~1 FPS，低频更稳
  }
  wsRelation.onmessage = ev => {
    try{
      const data = JSON.parse(ev.data)
      relationActions.value = Array.isArray(data?.actions) ? data.actions : []
    }catch(_){ }
  }
  wsRelation.onerror = () => { wsError.value = '关系WS错误' }
  wsRelation.onclose = () => { stopRealtimeRelation() }
}

function stopRealtimeRelation(){
  realtimeRelationOn.value = false
  if(relationTimer){ clearInterval(relationTimer); relationTimer = null }
  if(wsRelation && wsRelation.readyState === WebSocket.OPEN){ try{ wsRelation.close() }catch(_){} }
  wsRelation = null
}

async function toggleRealtime(){
  if(realtimeOn.value){ stopRealtime(); return }
  wsError.value = ''
  try {
    if(devices.value.length === 0){ await refreshDevices() }
    await startMediaStream()
  } catch (e) {
    wsError.value = '无法开启摄像头: ' + (e?.message || e)
    return
  }
  try {
    ws = new WebSocket('ws://127.0.0.1:8000/ws/detect')
  } catch (e) {
    wsError.value = '连接 WebSocket 失败: ' + (e?.message || e)
    return
  }
  ws.onopen = () => {
    realtimeOn.value = true
    const ctx = canvasRef.value.getContext('2d')
    const sendFrame = () => {
      if(!realtimeOn.value || ws.readyState !== WebSocket.OPEN) return
      ctx.drawImage(videoRef.value, 0, 0, canvasRef.value.width, canvasRef.value.height)
      canvasRef.value.toBlob(b => {
        if(!b) return
        const fr = new FileReader()
        fr.onloadend = () => { ws?.send(fr.result) }
        fr.readAsDataURL(b)
      }, 'image/jpeg', 0.7)
    }
    // 可调节发送频率：默认 2 FPS，减轻抖动与提升稳定性
    const intervalMs = 500
    timer = setInterval(sendFrame, intervalMs)
  }
  ws.onmessage = ev => {
    try {
      const data = JSON.parse(ev.data)
      const objs = Array.isArray(data?.objects) ? data.objects : []
      // 基于最近窗口的多数投票做平滑，减少类别闪烁
      pushDetection(objs)
      lastObjects.value = getSmoothedObjects()
    } catch (_) { /* ignore */ }
  }
  ws.onerror = () => { wsError.value = 'WebSocket 错误' }
  ws.onclose = () => { stopRealtime() }
}

function stopRealtime(){
  realtimeOn.value = false
  lastObjects.value = []
  if(timer){ clearInterval(timer); timer = null }
  if(ws && ws.readyState === WebSocket.OPEN){ try { ws.close() } catch(_){} }
  ws = null
  if(mediaStream){ mediaStream.getTracks().forEach(t => t.stop()); mediaStream = null }
}

onBeforeUnmount(() => { stopRealtime() })
onMounted(async () => {
  // 部分浏览器需先获取一次权限后才能拿到设备标签
  try { await refreshDevices() } catch(_){}
  if(navigator.mediaDevices?.addEventListener){
    navigator.mediaDevices.addEventListener('devicechange', refreshDevices)
  }
})

// --- 简单结果平滑：维护最近 N 帧的结果做多数投票 ---
const history = []
const HISTORY_MAX = 5
function pushDetection(arr){
  history.push(new Set(arr))
  if(history.length > HISTORY_MAX) history.shift()
}
function getSmoothedObjects(){
  const counter = new Map()
  for(const s of history){
    for(const x of s){ counter.set(x, (counter.get(x)||0)+1) }
  }
  const threshold = Math.ceil(HISTORY_MAX/2) // 半数以上出现
  return Array.from(counter.entries()).filter(([_,c])=>c>=threshold).map(([k])=>k)
}

async function analyzeCurrentFrameEmotion(){
  if(!videoRef.value) return
  // 使用更小分辨率的临时画布以加快上传和后端处理
  const tmp = document.createElement('canvas')
  tmp.width = 160; tmp.height = 120
  const tctx = tmp.getContext('2d')
  tctx.drawImage(videoRef.value, 0, 0, tmp.width, tmp.height)
  const blob = await new Promise(resolve => tmp.toBlob(resolve, 'image/jpeg', 0.8))
  const fd = new FormData()
  fd.append('file', blob, 'frame.jpg')
  try {
    const resp = await axios.post('http://127.0.0.1:8000/emotion/file', fd)
    currentEmotion.value = resp?.data?.emotion || ''
  } catch (e){
    const data = e?.response?.data
    const msg = (data && typeof data === 'object') ? (data.detail || JSON.stringify(data)) : (data || e.message)
    wsError.value = '情绪识别失败: ' + msg
  }
}
</script>

<style>
button{ padding:8px 16px }
</style>


