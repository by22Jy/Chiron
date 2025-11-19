/**
 * 移动端手势服务
 * YOLO-LLM Platform
 *
 * 提供移动端触摸手势支持、设备检测和移动端优化
 */

export class MobileGestureService {
  constructor() {
    this.touchStartX = 0
    this.touchStartY = 0
    this.touchEndX = 0
    this.touchEndY = 0
    this.gestureHandlers = new Map()
    this.isMobile = this.detectMobile()
    this.isTablet = this.detectTablet()
    this.touchThreshold = 50 // 滑动阈值
    this.tapThreshold = 200 // 点击时间阈值
    this.tapStartTime = 0
    this.longPressThreshold = 500 // 长按阈值
    this.longPressTimer = null
  }

  /**
   * 检测移动设备
   */
  detectMobile() {
    return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           (window.innerWidth <= 768 && 'ontouchstart' in window)
  }

  /**
   * 检测平板设备
   */
  detectTablet() {
    return /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent) ||
           (window.innerWidth > 768 && window.innerWidth <= 1024 && 'ontouchstart' in window)
  }

  /**
   * 获取设备信息
   */
  getDeviceInfo() {
    return {
      isMobile: this.isMobile,
      isTablet: this.isTablet,
      isDesktop: !this.isMobile && !this.isTablet,
      screenWidth: window.innerWidth,
      screenHeight: window.innerHeight,
      pixelRatio: window.devicePixelRatio || 1,
      touchSupport: 'ontouchstart' in window,
      orientation: screen.orientation?.type || 'unknown'
    }
  }

  /**
   * 初始化触摸手势监听
   */
  init(element) {
    if (!this.isMobile || !element) return

    element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false })
    element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false })
    element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false })

    // 防止默认的触摸行为
    element.addEventListener('touchstart', this.preventDefaults, { passive: false })
  }

  /**
   * 注册手势处理器
   */
  on(gestureType, handler) {
    if (!this.gestureHandlers.has(gestureType)) {
      this.gestureHandlers.set(gestureType, [])
    }
    this.gestureHandlers.get(gestureType).push(handler)
  }

  /**
   * 移除手势处理器
   */
  off(gestureType, handler) {
    if (this.gestureHandlers.has(gestureType)) {
      const handlers = this.gestureHandlers.get(gestureType)
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  /**
   * 触摸开始处理
   */
  handleTouchStart(e) {
    this.touchStartX = e.touches[0].clientX
    this.touchStartY = e.touches[0].clientY
    this.tapStartTime = Date.now()

    // 设置长按定时器
    this.longPressTimer = setTimeout(() => {
      this.handleGesture('longpress', e)
    }, this.longPressThreshold)
  }

  /**
   * 触摸移动处理
   */
  handleTouchMove(e) {
    // 如果移动距离太大，清除长按定时器
    const moveX = Math.abs(e.touches[0].clientX - this.touchStartX)
    const moveY = Math.abs(e.touches[0].clientY - this.touchStartY)

    if (moveX > 10 || moveY > 10) {
      this.clearLongPressTimer()
    }
  }

  /**
   * 触摸结束处理
   */
  handleTouchEnd(e) {
    this.touchEndX = e.changedTouches[0].clientX
    this.touchEndY = e.changedTouches[0].clientY

    const tapDuration = Date.now() - this.tapStartTime
    this.clearLongPressTimer()

    // 处理手势
    this.handleGesture(this.detectGesture(), e, tapDuration)
  }

  /**
   * 检测手势类型
   */
  detectGesture() {
    const deltaX = this.touchEndX - this.touchStartX
    const deltaY = this.touchEndY - this.touchStartY
    const absDeltaX = Math.abs(deltaX)
    const absDeltaY = Math.abs(deltaY)

    // 判断是否为点击
    if (absDeltaX < 10 && absDeltaY < 10) {
      return 'tap'
    }

    // 判断滑动方向
    if (absDeltaX > absDeltaY) {
      return deltaX > 0 ? 'swiperight' : 'swipeleft'
    } else {
      return deltaY > 0 ? 'swipedown' : 'swipeup'
    }
  }

  /**
   * 处理手势事件
   */
  handleGesture(gestureType, e, duration = 0) {
    const handlers = this.gestureHandlers.get(gestureType)
    if (handlers) {
      const gestureData = {
        type: gestureType,
        startX: this.touchStartX,
        startY: this.touchStartY,
        endX: this.touchEndX,
        endY: this.touchEndY,
        duration,
        timestamp: Date.now()
      }

      handlers.forEach(handler => {
        try {
          handler(gestureData, e)
        } catch (error) {
          console.error('手势处理错误:', error)
        }
      })
    }
  }

  /**
   * 清除长按定时器
   */
  clearLongPressTimer() {
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer)
      this.longPressTimer = null
    }
  }

  /**
   * 防止默认行为
   */
  preventDefaults(e) {
    e.preventDefault()
  }

  /**
   * 添加触觉反馈
   */
  vibrate(pattern = 10) {
    if ('vibrate' in navigator) {
      navigator.vibrate(pattern)
    }
  }

  /**
   * 获取安全区域
   */
  getSafeArea() {
    const style = getComputedStyle(document.documentElement)
    return {
      top: parseInt(style.getPropertyValue('--safe-area-inset-top')) || 0,
      right: parseInt(style.getPropertyValue('--safe-area-inset-right')) || 0,
      bottom: parseInt(style.getPropertyValue('--safe-area-inset-bottom')) || 0,
      left: parseInt(style.getPropertyValue('--safe-area-inset-left')) || 0
    }
  }

  /**
   * 设置viewport元标签
   */
  setViewport() {
    const viewport = document.querySelector('meta[name="viewport"]')
    if (viewport) {
      viewport.setAttribute('content',
        'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover'
      )
    }
  }

  /**
   * 添加移动端CSS变量
   */
  setMobileCSSVariables() {
    const root = document.documentElement
    const deviceInfo = this.getDeviceInfo()

    root.style.setProperty('--mobile-device-width', `${deviceInfo.screenWidth}px`)
    root.style.setProperty('--mobile-device-height', `${deviceInfo.screenHeight}px`)
    root.style.setProperty('--mobile-pixel-ratio', deviceInfo.pixelRatio)
    root.style.setProperty('--is-mobile', deviceInfo.isMobile ? '1' : '0')
    root.style.setProperty('--is-tablet', deviceInfo.isTablet ? '1' : '0')
  }

  /**
   * 优化移动端输入体验
   */
  optimizeMobileInputs() {
    // 防止双击缩放
    let lastTouchEnd = 0
    document.addEventListener('touchend', (e) => {
      const now = Date.now()
      if (now - lastTouchEnd <= 300) {
        e.preventDefault()
      }
      lastTouchEnd = now
    }, { passive: false })

    // 优化输入框焦点
    const inputs = document.querySelectorAll('input, textarea')
    inputs.forEach(input => {
      input.addEventListener('focus', () => {
        // 延迟滚动到输入框
        setTimeout(() => {
          input.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }, 300)
      })
    })
  }

  /**
   * 处理屏幕旋转
   */
  handleOrientationChange(callback) {
    if ('orientation' in screen) {
      screen.orientation.addEventListener('change', callback)
    } else {
      window.addEventListener('orientationchange', callback)
    }
  }

  /**
   * 检查是否为PWA环境
   */
  isPWA() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true
  }

  /**
   * 获取移动端浏览器信息
   */
  getMobileBrowserInfo() {
    const userAgent = navigator.userAgent

    return {
      isChrome: /Chrome/i.test(userAgent),
      isSafari: /Safari/i.test(userAgent) && !/Chrome/i.test(userAgent),
      isFirefox: /Firefox/i.test(userAgent),
      isEdge: /Edge/i.test(userAgent),
      isSamsung: /SamsungBrowser/i.test(userAgent),
      isUC: /UCBrowser/i.test(userAgent),
      version: this.getBrowserVersion()
    }
  }

  /**
   * 获取浏览器版本
   */
  getBrowserVersion() {
    const userAgent = navigator.userAgent
    const match = userAgent.match(/(Chrome|Safari|Firefox|Edge|SamsungBrowser|UCBrowser)\/(\d+)/)
    return match ? parseInt(match[2]) : 0
  }

  /**
   * 销毁服务
   */
  destroy() {
    this.clearLongPressTimer()
    this.gestureHandlers.clear()
  }
}

// 创建全局移动端手势服务实例
export const mobileGestureService = new MobileGestureService()

// 导出默认实例
export default mobileGestureService