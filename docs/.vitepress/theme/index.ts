import { h } from 'vue'
import { onContentUpdated } from 'vitepress'
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
    // 点击正文图片放大。onContentUpdated 在切换页面和开发时热更新（改 md 后正文重新渲染）都会触发，
    // 每次先解绑旧图片再绑定当前正文里的图片，避免热更新后新图片失去放大功能
    const zoom = mediumZoom({ background: 'var(--vp-c-bg)' })
    onContentUpdated(() => {
      zoom.detach()
      zoom.attach('.main img')
    })
  },
}
