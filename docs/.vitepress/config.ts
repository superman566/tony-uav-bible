import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'Tony UAV Bible',
  description: 'Tony 的无人机学习笔记',

  base: '/tony-uav-bible/',

  themeConfig: {
    logo: '/logo.svg',
    nav: [
      { text: '首页', link: '/' },
      { text: '无人机', link: '/uav/intro' },
      { text: 'AI YOLO', link: '/ai-yolo/intro' },
    ],

    sidebar: {
      '/uav/': [
        {
          text: '无人机基础',
          items: [
            { text: '简介', link: '/uav/intro' },
          ],
        },
      ],
      '/ai-yolo/': [
        {
          text: 'AI YOLO',
          collapsed: false,
          items: [
            { text: '简介', link: '/ai-yolo/intro' },
            { text: '搭建深度学习开发环境', link: '/ai-yolo/dl-env-setup' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/superman566/tony-uav-bible' },
    ],

    footer: {
      message: '基于 VitePress 构建',
      copyright: 'Copyright © 2026 Tony He',
    },

    search: {
      provider: 'local',
    },

    outline: {
      label: '本页目录',
      level: [2, 3],
    },

    docFooter: {
      prev: '上一篇',
      next: '下一篇',
    },
  },
})
