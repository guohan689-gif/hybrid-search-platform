# 部署指南

## 方案：Vercel (前端) + Render (后端)

### 一、后端部署到 Render

1. **文件位置**
   所有部署文件都在 `deploy` 文件夹中

2. **部署步骤**
   - 访问 https://render.com 注册账号
   - 点击 "New +" → "Web Service"
   - 连接你的GitHub仓库 `hybrid-search-platform`
   - 配置：
     - Name: `rerank-backend`
     - Environment: `Python 3`
     - Root Directory: `deploy`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT rerank_backend:app`
   - 添加环境变量：
     - `DASHSCOPE_API_KEY` = `sk-d2a40e93f9a64d7e9fe40b9da3a0ef40`
     - `FLASK_ENV` = `production`
   - 点击 "Create Web Service"
   - 等待部署完成，获取后端URL（如：https://rerank-backend.onrender.com）

### 二、前端部署到 Vercel

1. **修改前端API地址**
   
   打开 `hybrid-search.html`，修改API地址为你的Render后端URL

2. **部署到Vercel**
   - 访问 https://vercel.com 注册账号
   - 点击 "Add New..." → "Project"
   - 导入GitHub仓库
   - 点击 "Deploy"

3. **绑定自定义域名 hanniennn.com**
   - 在Vercel项目设置中，点击 "Domains"
   - 添加 `hanniennn.com`
   - 按照提示配置DNS

### 三、测试

访问你的域名，测试功能是否正常。
