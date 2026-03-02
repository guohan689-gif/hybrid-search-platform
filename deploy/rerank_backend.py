import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math

app = Flask(__name__)
CORS(app)

# 通义千问API配置（从环境变量读取）
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', 'sk-d2a40e93f9a64d7e9fe40b9da3a0ef40')
RERANK_API_URL = "https://dashscope.aliyuncs.com/compatible-api/v1/reranks"

def tokenize(text):
    """简单分词"""
    import re
    return re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z0-9]+', text.lower())

def vector_similarity(query, doc):
    """计算向量相似度"""
    q_tokens = set(tokenize(query))
    d_tokens = set(tokenize(doc))
    if not q_tokens or not d_tokens:
        return 0
    intersection = len(q_tokens.intersection(d_tokens))
    return intersection / max(len(q_tokens), len(d_tokens))

def bm25_score(query, title, content, avgdl_title, avgdl_content, doc_count, title_doc_freq, content_doc_freq):
    """计算BM25得分，标题和正文权重7:3"""
    q_tokens = tokenize(query)
    
    k1, b = 1.2, 0.75
    
    # 计算标题得分
    title_tokens = tokenize(title)
    title_freq = {}
    for token in title_tokens:
        title_freq[token] = title_freq.get(token, 0) + 1
    
    title_score = 0
    for term in q_tokens:
        tf = title_freq.get(term, 0)
        if tf > 0:
            df = title_doc_freq.get(term, 0)
            idf = math.log(1 + (doc_count - df + 0.5) / (df + 0.5))
            norm = 1 - b + b * (len(title_tokens) / avgdl_title) if avgdl_title > 0 else 1
            title_score += idf * (tf * (k1 + 1)) / (tf + k1 * norm)
    
    # 计算正文得分
    content_tokens = tokenize(content)
    content_freq = {}
    for token in content_tokens:
        content_freq[token] = content_freq.get(token, 0) + 1
    
    content_score = 0
    for term in q_tokens:
        tf = content_freq.get(term, 0)
        if tf > 0:
            df = content_doc_freq.get(term, 0)
            idf = math.log(1 + (doc_count - df + 0.5) / (df + 0.5))
            norm = 1 - b + b * (len(content_tokens) / avgdl_content) if avgdl_content > 0 else 1
            content_score += idf * (tf * (k1 + 1)) / (tf + k1 * norm)
    
    return title_score * 0.7 + content_score * 0.3

def normalize_scores(scores):
    """归一化得分到0-1"""
    if not scores:
        return []
    max_score = max(scores)
    min_score = min(scores)
    range_score = max_score - min_score
    if range_score == 0:
        return [0] * len(scores)
    return [(s - min_score) / range_score for s in scores]

def call_rerank_api(query, documents, top_n=None):
    """调用通义千问重排API"""
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen3-rerank",
        "documents": documents,
        "query": query,
        "instruct": "Given a web search query, retrieve relevant passages that answer the query."
    }
    
    if top_n:
        payload["top_n"] = top_n
    
    try:
        response = requests.post(RERANK_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"重排API调用失败: {e}")
        return None

@app.route('/api/hybrid-search', methods=['POST'])
def hybrid_search():
    try:
        data = request.json
        query = data.get('query', '').strip()
        docs_text = data.get('docs', '').strip()
        slice_size = int(data.get('sliceSize', 200))
        max_recall = int(data.get('maxRecall', 10))
        vector_ratio = int(data.get('vectorRatio', 50))
        min_threshold = float(data.get('minThreshold', 0.3))
        rerank_threshold = float(data.get('rerankThreshold', 0.5))
        
        if not query or not docs_text:
            return jsonify({'error': '请输入查询和文档'}), 400
        
        vector_recall = round(max_recall * vector_ratio / 100)
        es_recall = max_recall - vector_recall
        
        docs = [d.strip() for d in docs_text.split('---') if d.strip()]
        all_slices = []
        
        for doc_idx, doc in enumerate(docs):
            lines = doc.split('\n', 1)
            title = lines[0].strip() if lines else ''
            content = lines[1].strip() if len(lines) > 1 else ''
            
            for i in range(0, len(content), slice_size):
                slice_text = content[i:i + slice_size]
                all_slices.append({
                    'id': f'{doc_idx}-{i // slice_size}',
                    'docId': doc_idx,
                    'sliceIndex': i // slice_size,
                    'title': title,
                    'content': slice_text,
                    'text': slice_text
                })
        
        avgdl_title = sum(len(tokenize(s['title'])) for s in all_slices) / len(all_slices) if all_slices else 1
        avgdl_content = sum(len(tokenize(s['content'])) for s in all_slices) / len(all_slices) if all_slices else 1
        
        title_doc_freq = {}
        content_doc_freq = {}
        for item in all_slices:
            title_terms = set(tokenize(item['title']))
            for term in title_terms:
                title_doc_freq[term] = title_doc_freq.get(term, 0) + 1
            
            content_terms = set(tokenize(item['content']))
            for term in content_terms:
                content_doc_freq[term] = content_doc_freq.get(term, 0) + 1
        
        doc_count = len(all_slices)
        
        for item in all_slices:
            item['vectorScore'] = vector_similarity(query, item['content'])
        
        vector_scores = sorted(all_slices, key=lambda x: x['vectorScore'], reverse=True)[:vector_recall]
        stage1 = [{'id': item['id'], 'docId': item['docId'], 'sliceIndex': item['sliceIndex'], 
                   'title': item['title'], 'text': item['content'], 'vectorScore': item['vectorScore']} for item in vector_scores]
        
        for item in all_slices:
            item['esScore'] = bm25_score(query, item['title'], item['content'], 
                                        avgdl_title, avgdl_content, doc_count, 
                                        title_doc_freq, content_doc_freq)
        
        es_scores = sorted(all_slices, key=lambda x: x['esScore'], reverse=True)[:es_recall]
        stage2 = [{'id': item['id'], 'docId': item['docId'], 'sliceIndex': item['sliceIndex'],
                   'title': item['title'], 'text': item['content'], 'esScore': item['esScore']} for item in es_scores]
        
        merged = {}
        for item in vector_scores:
            merged[item['id']] = {
                'id': item['id'],
                'docId': item['docId'],
                'sliceIndex': item['sliceIndex'],
                'title': item['title'],
                'text': item['content'],
                'vectorScore': item['vectorScore'],
                'esScore': 0
            }
        
        for item in es_scores:
            if item['id'] in merged:
                merged[item['id']]['esScore'] = item['esScore']
            else:
                merged[item['id']] = {
                    'id': item['id'],
                    'docId': item['docId'],
                    'sliceIndex': item['sliceIndex'],
                    'title': item['title'],
                    'text': item['content'],
                    'vectorScore': 0,
                    'esScore': item['esScore']
                }
        
        merged_list = list(merged.values())
        stage3 = merged_list.copy()
        
        es_scores_only = [item['esScore'] for item in merged_list]
        es_norm = normalize_scores(es_scores_only)
        
        for i, item in enumerate(merged_list):
            item['esNorm'] = es_norm[i]
            item['combinedScore'] = (item['vectorScore'] + item['esNorm']) / 2
        
        stage4 = merged_list.copy()
        
        filtered1 = []
        passed1 = []
        
        for item in merged_list:
            item_copy = item.copy()
            item_copy['filtered'] = item['combinedScore'] < min_threshold
            filtered1.append(item_copy)
            if not item_copy['filtered']:
                passed1.append(item)
        
        stage5 = filtered1
        
        if passed1:
            documents = [item['text'] for item in passed1]
            rerank_result = call_rerank_api(query, documents)
            
            if rerank_result and 'results' in rerank_result:
                for result in rerank_result['results']:
                    idx = result['index']
                    passed1[idx]['rerankScore'] = result['relevance_score']
            else:
                for item in passed1:
                    item['rerankScore'] = item['vectorScore']
            
            passed1.sort(key=lambda x: x['rerankScore'], reverse=True)
        
        final = []
        for item in passed1:
            item_copy = item.copy()
            item_copy['filtered'] = item['rerankScore'] < rerank_threshold
            final.append(item_copy)
        
        stage6 = final
        
        return jsonify({
            'stage1': stage1,
            'stage2': stage2,
            'stage3': stage3,
            'stage4': stage4,
            'stage5': stage5,
            'stage6': stage6,
            'summary': {
                'stage1': len(stage1),
                'stage2': len(stage2),
                'stage3': len(stage3),
                'stage4': len(stage4),
                'stage5': len([x for x in stage5 if not x['filtered']]),
                'stage6': len([x for x in stage6 if not x['filtered']])
            }
        })
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    debug = os.getenv('FLASK_ENV') != 'production'
    print("启动混合检索重排服务...")
    print(f"服务地址: http://0.0.0.0:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
