# Tony UAV Bible

Tony 的无人机（UAV）与 AI 学习笔记，基于 [VitePress](https://vitepress.dev/) 构建，通过 GitHub Actions 自动部署到 GitHub Pages。

在线阅读：https://superman566.github.io/tony-uav-bible/

## 项目结构

```
docs/
├── .vitepress/
│   ├── config.ts          # 站点配置：导航栏、侧边栏、主题设置
│   └── theme/              # 自定义主题层（在默认主题基础上扩展）
│       ├── index.ts        # 挂载自定义组件（侧边栏收起/展开按钮）
│       ├── SidebarToggle.vue
│       └── custom.css
├── index.md                # 首页（hero + features）
├── uav/                    # 无人机基础笔记
└── ai-yolo/                 # AI / 计算机视觉（YOLO）笔记

.github/workflows/deploy.yml  # CI：build → 上传 artifact → 部署到 GitHub Pages
```

新增笔记分类：在 `docs/` 下新建文件夹、添加 `.md` 文件，再到 `docs/.vitepress/config.ts` 的 `themeConfig.sidebar` 中按路径前缀注册导航项。

## 本地运行

需要 Node.js（建议 20+）。

```bash
npm install            # 安装依赖

npm run docs:dev       # 启动本地开发服务器（热更新）
npm run docs:build     # 构建到 docs/.vitepress/dist/
npm run docs:preview   # 本地预览构建产物
```

## 部署

推送到 `main` 分支会自动触发 GitHub Actions 工作流完成构建与部署，无需手动操作或维护 `gh-pages` 分支。
