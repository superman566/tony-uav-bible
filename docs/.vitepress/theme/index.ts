import { h, nextTick, onMounted, watch } from 'vue'
import { useRoute } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import mediumZoom from 'medium-zoom'
import SidebarToggle from './SidebarToggle.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'sidebar-nav-before': () => h(SidebarToggle),
    })
  },
  setup() {
    const route = useRoute()
    // 点击正文图片放大；切换页面后重新绑定新页面的图片
    const initZoom = () => {
      mediumZoom('.main img', { background: 'var(--vp-c-bg)' })
    }
    onMounted(initZoom)
    watch(
      () => route.path,
      () => nextTick(initZoom),
    )
  },
}
