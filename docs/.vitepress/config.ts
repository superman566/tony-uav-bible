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
					items: [{ text: '简介', link: '/uav/intro' }],
				},
			],
			'/ai-yolo/': [
				{
					text: 'AI YOLO',
					collapsed: false,
					items: [
						{ text: '简介', link: '/ai-yolo/intro' },
						{ text: '搭建深度学习开发环境', link: '/ai-yolo/dl-env-setup' },
						{
							text: '经典计算机视觉核心技术与算法',
							link: '/ai-yolo/classic-cv-algorithms',
						},
						{ text: '图像识别的数学基础', link: '/ai-yolo/math-basics' },
						{ text: '深度学习基础', link: '/ai-yolo/dl-basics' },
						{
							text: '训练与优化神经网络',
							link: '/ai-yolo/nn-training-optimization',
						},
						{
							text: 'PyTorch 手写数字识别实战',
							link: '/ai-yolo/pytorch-mnist',
						},
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
			level: [2, 4],
		},

		docFooter: {
			prev: '上一篇',
			next: '下一篇',
		},
	},
});
