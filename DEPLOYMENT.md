# 部署指南

## 方案：Vercel (前端) + Render (后端)

### 一、后端部署到 Render

1. **准备文件**
   - `rerank_backend_deploy.py` - 后端代码
   - `requirements.txt` - Python依赖
   - `render.yaml` - Render配置

2. **部署步骤**
   - 访问 https://render.com 注册账号
   - 点击 "New +" → "Web Service"
   - 连接你的GitHub仓库或直接上传代码
   - 配置：
     - Name: `rerank-backend`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT rerank_backend_deploy:app`
   - 添加环境变量：
     - `DASHSCOPE_API_KEY` = `sk-d2a40e93f9a64d7e9fe40b9da3a0ef40`
     - `FLASK_ENV` = `production`
   - 点击 "Create Web Service"
   - 等待部署完成，获取后端URL（如：https://rerank-backend.onrender.com）

### 二、前端部署到 Vercel

1. **修改前端API地址**
   
   打开 `hybrid-search.html`，找到这行：
   ```javascript
   const apiUrl = window.location.hostname === 'localhost' 
       ? 'http://localhost:5002/api/hybrid-search'
       : 'https://hanniennn.com/api/hybrid-search';
   ```
   
   改为你的Render后端地址：
   ```javascript
   const apiUrl = window.location.hostname === 'localhost' 
       ? 'http://localhost:5002/api/hybrid-search'
       : 'https://rerank-backend.onrender.com/api/hybrid-search';
   ```

2. **部署到Vercel**
   - 访问 https://vercel.com 注册账号
   - 点击 "Add New..." → "Project"
   - 导入你的GitHub仓库或直接拖拽 `hybrid-search.html`
   - 配置：
     - Framework Preset: `Other`
     - Root Directory: `./`
   - 点击 "Deploy"
   - 部署完成后，Vercel会给你一个URL（如：https://your-project.vercel.app）

3. **绑定自定义域名 hanniennn.com**
   - 在Vercel项目设置中，点击 "Domains"
   - 添加 `hanniennn.com`
   - 按照提示在你的域名DNS设置中添加记录：
     - Type: `A`
     - Name: `@`
     - Value: `76.76.21.21` (Vercel的IP)
   - 或者使用CNAME：
     - Type: `CNAME`
     - Name: `www`
     - Value: `cname.vercel-dns.com`

### 三、测试

1. 访问 https://hanniennn.com
2. 输入查询和文档
3. 点击"开始检索"
4. 查看结果

### 四、注意事项

- Render免费版会在30分钟无活动后休眠，首次访问可能需要等待10-20秒
- Vercel免费版有带宽限制，适合个人使用
- API Key已硬编码，生产环境建议使用环境变量管理

### 五、故障排查

**后端无响应：**
- 检查Render服务状态
- 查看Render日志：Dashboard → Logs

**前端无法连接后端：**
- 检查浏览器控制台错误
- 确认API地址正确
- 检查CORS设置

**重排API失败：**
- 检查API Key是否有效
- 查看后端日志中的错误信息
