# 混合检索重排平台

基于向量检索、ES检索和通义千问重排模型的智能文本检索系统。

## 功能特点

- 🔍 **混合检索**：结合向量相似度和BM25算法
- 📊 **多阶段处理**：6个处理阶段，每步可视化
- 🎯 **智能重排**：使用通义千问qwen3-rerank模型
- 📰 **新闻优化**：标题70% + 正文30%权重
- 🎨 **直观展示**：每个阶段的详细得分和变化理由

## 技术栈

- **前端**：HTML + JavaScript
- **后端**：Python + Flask
- **算法**：BM25、余弦相似度、通义千问重排

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端

```bash
python rerank_backend_deploy.py
```

### 3. 打开前端

在浏览器中打开 `hybrid-search.html`

## 部署

详见 [DEPLOYMENT.md](DEPLOYMENT.md)

## 文件说明

- `hybrid-search.html` - 前端页面
- `rerank_backend_deploy.py` - 后端服务
- `requirements.txt` - Python依赖
- `render.yaml` - Render部署配置
- `DEPLOYMENT.md` - 部署指南

## 处理流程

1. **向量召回** - 基于语义相似度
2. **ES召回** - 基于BM25算法（标题70% + 正文30%）
3. **合并去重** - 融合两种检索结果
4. **归一化** - 统一得分量纲
5. **相似度过滤** - 过滤低质量结果
6. **重排过滤** - 使用AI模型精排

## License

MIT
