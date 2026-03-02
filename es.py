from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
import uuid

# ================= 配置区域 =================
# 你的 ES 连接信息
ES_HOST = "https://my-elasticsearch-project-cdbb61.es.us-central1.gcp.elastic.cloud:443"
ES_API_KEY = "TGYtdG81d0JMVlZZMmF1M2lWOUc6WVdTQk1rWGNoYjRnQndjZThPRkFSdw=="

# 【在这里修改你要测试的两句话】
sentence_A = "公开招聘"  # 查询句 (Query)
sentence_B = "广东省外语艺术职业学院关于2015年第四批公开招聘工作人员（流动编制）的公告" # 被搜句 (Document)
# ===========================================

# 1. 初始化客户端
client = Elasticsearch(
    ES_HOST,
    api_key=ES_API_KEY
)

# 检查连接
if not client.ping():
    print("❌ 无法连接到 Elasticsearch，请检查网络或账号密码。")
    exit()

# 生成一个唯一的索引名，避免和旧数据冲突 (例如: test-score-550e8400)
index_name = f"test-score-{uuid.uuid4().hex[:8]}"

print(f"⚡ 开始测试...\n句子 A (查询): {sentence_A}\n句子 B (文档): {sentence_B}\n")

try:
    # 2. 创建索引 (使用标准的 text 类型，兼容所有 ES 版本)
    mappings = {
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "standard" # 使用标准分词器
            }
        }
    }
    client.indices.create(index=index_name, mappings=mappings)
    print(f"✅ 索引 '{index_name}' 创建成功。")

    # 3. 写入句子 B (作为文档)
    doc = { "content": sentence_B }
    client.index(index=index_name, document=doc, refresh="wait_for")
    print("✅ 句子 B 已写入数据库。")

    # 4. 用句子 A 进行搜索
    search_query = {
        "query": {
            "match": {
                "content": sentence_A
            }
        }
    }
    
    response = client.search(index=index_name, body=search_query)
    
    # 5. 提取并打印得分
    hits = response['hits']['hits']
    
    if hits:
        score = hits[0]['_score']
        print("\n" + "="*30)
        print(f"🎯 相关性得分 (_score): {score}")
        print("="*30)
        
        if score > 0:
            print("💡 结论：两句话存在关键词匹配，得分越高相关性越强。")
        else:
            print("💡 结论：两句话没有共同词汇，得分为 0。")
    else:
        print("\n⚠️ 未找到匹配结果 (得分为 0)。")

except RequestError as e:
    print(f"❌ ES 请求错误: {e}")
except Exception as e:
    print(f"❌ 发生未知错误: {e}")

finally:
    # 6. 清理：删除临时索引，保持环境干净
    try:
        client.indices.delete(index=index_name)
        print("\n🧹 临时索引已清理。")
    except:
        pass