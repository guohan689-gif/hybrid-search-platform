# 混合检索重排平台

基于向量检索、ES BM25检索和通义千问重排模型的混合检索系统。

## 功能特点

- 向量召回（TF-IDF + 余弦相似度）
- ES BM25召回
- 混合检索结果合并与去重
- ES分数归一化
- 最小相似度阈值过滤
- 通义千问Qwen3-rerank模型重排

## 项目结构

```
.
├── hybrid-search.html          # 前端页面
└── deploy/                     # 后端部署文件
    ├── rerank_backend.py       # Flask后端服务
    ├── requirements.txt        # Python依赖
    ├── render.yaml            # Render部署配置
    ├── Procfile               # 进程配置
    └── DEPLOYMENT.md          # 部署说明文档
```

## 本地运行

### 后端

```bash
cd deploy
pip install -r requirements.txt
export DASHSCOPE_API_KEY=your_api_key
python rerank_backend.py
```

后端服务将在 http://localhost:5001 启动

### 前端

直接在浏览器中打开 `hybrid-search.html` 文件即可使用。

## 部署

详细部署说明请查看 [deploy/DEPLOYMENT.md](deploy/DEPLOYMENT.md)

### 快速部署

1. **后端部署到Render**
   - 连接GitHub仓库
   - Root Directory设置为 `deploy`
   - 添加环境变量 `DASHSCOPE_API_KEY`

2. **前端部署到Vercel**
   - 导入GitHub仓库
   - 部署后绑定域名
   - 更新前端API地址

## 技术栈

- 前端：原生HTML/CSS/JavaScript
- 后端：Python Flask
- 重排模型：通义千问Qwen3-rerank
- 部署：Render + Vercel

## License

MIT
