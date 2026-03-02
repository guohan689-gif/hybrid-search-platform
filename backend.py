from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba

app = Flask(__name__)
CORS(app)

def analyze_similarity_reason(sentence1, sentence2, similarity_score):
    """分析相似度结果的可能原因"""
    reasons = []
    
    # 分词
    words1 = set(jieba.cut(sentence1))
    words2 = set(jieba.cut(sentence2))
    
    # 计算共同词汇
    common_words = words1.intersection(words2)
    common_ratio = len(common_words) / max(len(words1), len(words2)) if max(len(words1), len(words2)) > 0 else 0
    
    # 分析原因
    if similarity_score > 0.8:
        reasons.append(f"高度相似 (相似度: {similarity_score:.2%})")
        if common_ratio > 0.6:
            reasons.append(f"共享了 {len(common_words)} 个关键词: {', '.join(list(common_words)[:5])}")
        reasons.append("句子表达的核心意思非常接近")
    elif similarity_score > 0.5:
        reasons.append(f"中等相似 (相似度: {similarity_score:.2%})")
        if common_ratio > 0.3:
            reasons.append(f"有 {len(common_words)} 个共同词汇: {', '.join(list(common_words)[:5])}")
        reasons.append("句子有一定的主题关联性")
    elif similarity_score > 0.2:
        reasons.append(f"低相似度 (相似度: {similarity_score:.2%})")
        if len(common_words) > 0:
            reasons.append(f"仅有少量共同词: {', '.join(list(common_words)[:3])}")
        reasons.append("句子主题或表达方式差异较大")
    else:
        reasons.append(f"几乎不相似 (相似度: {similarity_score:.2%})")
        reasons.append("句子内容完全不同，没有明显的关联性")
    
    # 长度分析
    len_diff = abs(len(sentence1) - len(sentence2))
    if len_diff > 20:
        reasons.append(f"句子长度差异较大 (相差 {len_diff} 个字符)")
    
    return reasons

@app.route('/api/similarity', methods=['POST'])
def calculate_similarity():
    try:
        data = request.json
        sentence1 = data.get('sentence1', '').strip()
        sentence2 = data.get('sentence2', '').strip()
        
        if not sentence1 or not sentence2:
            return jsonify({'error': '请输入两个句子'}), 400
        
        # 使用TF-IDF向量化
        vectorizer = TfidfVectorizer(tokenizer=lambda x: jieba.cut(x))
        tfidf_matrix = vectorizer.fit_transform([sentence1, sentence2])
        
        # 计算余弦相似度
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # 分析原因
        reasons = analyze_similarity_reason(sentence1, sentence2, similarity)
        
        return jsonify({
            'similarity': float(similarity),
            'percentage': f"{similarity * 100:.2f}%",
            'reasons': reasons,
            'sentence1_length': len(sentence1),
            'sentence2_length': len(sentence2)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("正在启动句子相似度计算服务...")
    print("服务地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
