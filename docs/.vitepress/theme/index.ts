import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import SidebarToggle from './SidebarToggle.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'sidebar-nav-before': () => h(SidebarToggle),
    })
  },
}
