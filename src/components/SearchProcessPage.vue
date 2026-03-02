<template>
  <div class="search-process-page">
    <div class="header">
      <img
        src="https://gimg3.baidu.com/search/src=https%3A%2F%2Fstatic-data.gaokao.cn%2Fupload%2Flogo%2F42.jpg%3Ft%3D1756742428&refer=http%3A%2F%2Fwww.baidu.com&app=2021&size=w931&n=0&g=0n&er=404&q=75&fmt=auto&maxorilen2heic=2000000?sec=1757178000&t=98d042f584c3cfa55238ac85a033e451"
        alt="武汉大学logo"
        class="wuda-logo"
      />
      <span class="title">武汉大学 | AI 智能搜索</span>
      <div class="user-info">
        <img
          src="https://picsum.photos/id/64/200"
          alt="头像"
          class="user-avatar"
        />
        <span class="username">郭含</span>
        <span class="icon-arrow-down">▼</span>
      </div>
    </div>

    <div class="search-box">
      <input
        type="text"
        :value="receivedQuestion"
        class="search-input"
        readonly
      />
      <div class="mode-buttons">
        <button 
          class="mode-btn" 
          :class="{ active: currentMode === 'quick' }"
          disabled
        >
          <span class="icon-rocket">🚀</span>
          极速
        </button>
        <button 
          class="mode-btn" 
          :class="{ active: currentMode === 'explore' }"
          disabled
        >
          <span class="icon-search">🔍</span>
          探索
        </button>
      </div>
      <button class="send-btn" disabled>
        <span class="icon-send">→</span>
      </button>
    </div>

    <div class="question-title">{{ receivedQuestion }}</div>

    <div class="progress-container">
      <!-- 应用查询 -->
      <div class="progress-item">
        <span class="icon-check" v-if="progress.app === 'done'">✓</span>
        <span class="icon-loading" v-else-if="progress.app === 'loading'"></span>
        <span class="progress-text">{{ progress.appText }}</span>
      </div>
      <!-- 新闻查询 -->
      <div class="progress-item">
        <span class="icon-check" v-if="progress.news === 'done'">✓</span>
        <span class="icon-loading" v-else-if="progress.news === 'loading'"></span>
        <span class="progress-text">{{ progress.newsText }}</span>
      </div>
      <!-- 文件查询 -->
      <div class="progress-item">
        <span class="icon-check" v-if="progress.file === 'done'">✓</span>
        <span class="icon-loading" v-else-if="progress.file === 'loading'"></span>
        <span class="icon-error" v-else-if="progress.file === 'error'">×</span>
        <span class="progress-text">{{ progress.fileText }}</span>
      </div>
    </div>

    <!-- 骨架屏：仅在文件接口加载中/整体未完成时显示，与错误提示互斥 -->
    <div class="skeleton-container" v-if="!isAllFinished && progress.file !== 'error'">
      <div class="skeleton-line"></div>
      <div class="skeleton-line" style="width: 90%"></div>
      <div class="skeleton-line" style="width: 80%"></div>
      <div class="skeleton-line" style="width: 95%"></div>
      <div class="skeleton-line" style="width: 75%"></div>
      <!-- 模拟结果列表占位 -->
      <div class="skeleton-card">
        <div class="skeleton-card-header"></div>
        <div class="skeleton-card-body">
          <div class="skeleton-line" style="width: 90%"></div>
          <div class="skeleton-line" style="width: 85%"></div>
          <div class="skeleton-line" style="width: 70%"></div>
        </div>
      </div>
      <div class="skeleton-card">
        <div class="skeleton-card-header"></div>
        <div class="skeleton-card-body">
          <div class="skeleton-line" style="width: 88%"></div>
          <div class="skeleton-line" style="width: 92%"></div>
          <div class="skeleton-line" style="width: 65%"></div>
        </div>
      </div>
    </div>

    <!-- 错误提示：仅在文件接口失败时显示 -->
    <div class="error-container" v-if="progress.file === 'error'">
      <span class="error-icon">×</span>
      <span class="error-text">{{ errorMessage }}</span>
      <button class="retry-btn" @click="retrySearch">重试</button>
    </div>
  </div>
</template>

<script>
export default {
  name: "SearchProcessPage",
  data() {
    return {
      receivedQuestion: "",
      currentMode: "quick", // 默认选中极速模式
      isAllFinished: false,
      errorMessage: "接口检索失败，请检查网络或重试",
      progress: {
        app: "loading",
        appText: "等待查询应用...",
        news: "loading",
        newsText: "等待查询新闻...",
        file: "loading",
        fileText: "等待查询文件...",
        knowledge: "loading",
        knowledgeText: "等待查询知识库..."
      }
    };
  },
  mounted() {
    this.receivedQuestion = this.$route.query.question || "默认搜索问题";
    this.simulateStepProgress();
  },
  methods: {
    checkAllFinished() {
      const allStages = ["app", "news", "file", "knowledge"];
      this.isAllFinished = allStages.every(stage => 
        this.progress[stage] === "done" || this.progress[stage] === "error"
      );
    },

    simulateStepProgress() {
      // 第1秒：模拟应用查询完成
      setTimeout(() => {
        this.progress.app = "done";
        this.progress.appText = "应用查询完成";
        this.checkAllFinished();
      }, 1000);

      // 第2秒：模拟新闻查询完成 + 调用真实全量接口（关键修改）
      setTimeout(() => {
        this.progress.news = "done";
        this.progress.newsText = "新闻查询完成";
        this.checkAllFinished();
        this.fetchFullSearchApi(); // 改为调用全量接口
      }, 2000);

      // 第4秒：模拟知识库查询完成
      setTimeout(() => {
        if (this.progress.file === "done") {
          this.progress.knowledge = "done";
          this.progress.knowledgeText = "知识库查询完成";
          this.checkAllFinished();
        } else if (this.progress.file === "error") {
          this.progress.knowledge = "error";
          this.progress.knowledgeText = "知识库查询终止（主查询失败）";
          this.checkAllFinished();
        }
      }, 4000);
    },

   fetchFullSearchApi() {
    this.progress.file = "loading";

    // 1. 拼接 GET 请求地址（后端接口为 /api/search，通过 URL 参数传 query）
    // 用 encodeURIComponent 处理特殊字符（如空格、中文）
    const requestUrl = `http://localhost:5002/api/search?query=${encodeURIComponent(this.receivedQuestion)}`;
    fetch(requestUrl, {
        method: "GET",  // 2. 改为 GET 方法（与后端一致）
        // 3. 移除 POST 相关的 headers 和 body（GET 无需这些）
        // 后端已配置 CORS，无需额外设置 credentials
    })
    .then(response => {
        // 处理 HTTP 错误（如 404、400、500）
        if (!response.ok) {
        // 可进一步解析后端返回的错误信息（如“缺少 query 参数”）
        return response.json().then(errData => {
            throw new Error(errData.error || `请求失败（${response.status}）`);
        });
        }
        return response.json();
    })
    .then(fullData => {
        // 接口成功：更新进度并跳转（后续逻辑不变）
        this.progress.file = "done";
        this.progress.fileText = "文件查询完成"; // 修正文案（与实际功能匹配）
        this.checkAllFinished();

        setTimeout(() => {
        // 根据模式区分跳转路由：极速→search-result，探索→new_progress
        const targetPath = this.currentMode === 'explore' ? '/new_progress' : '/search-result';
        this.$router.push({
            path: targetPath,
            query: {
            question: this.receivedQuestion,
            mode: this.currentMode,
            searchResult: JSON.stringify(fullData)
            }
        });
        }, 500);
    })
    .catch(error => {
        // 错误处理（文案与实际请求匹配）
        this.progress.file = "error";
        this.progress.fileText = "全量数据查询失败";
        this.errorMessage = `查询失败：${error.message}（点击重试）`;
        this.checkAllFinished();
    });
    },
   
    

    retrySearch() {
      this.isAllFinished = false;
      this.errorMessage = "接口检索失败，请检查网络或重试";
      this.progress = {
        app: "loading",
        appText: "等待查询应用...",
        news: "loading",
        newsText: "等待查询新闻...",
        file: "loading",
        fileText: "等待查询文件...",
        knowledge: "loading",
        knowledgeText: "等待查询知识库..."
      };
      this.simulateStepProgress();
    }
  }
};
</script>


<style scoped>
.search-process-page {
  background: linear-gradient(to bottom, #f5f7ff, #ffffff);
  min-height: 100vh;
  padding: 20px 80px;
  box-sizing: border-box;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.wuda-logo {
  width: 40px;
  height: 40px;
  margin-right: 10px;
  object-fit: cover;
}

.title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 5px;
  object-fit: cover;
}

.username {
  margin-right: 5px;
  color: #333;
}

.icon-arrow-down {
  font-size: 12px;
  color: #666;
  cursor: pointer;
}

.search-box {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 10px;
  font-size: 14px;
  color: #666;
  background: transparent;
}

.mode-buttons {
  display: flex;
  margin-right: 10px;
}

.mode-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
  display: flex;
  align-items: center;
  font-size: 12px;
  background: #f5f5f5;
  color: #666;
}

.mode-btn.active {
  background: #6b63ff;
  color: #fff;
}

.mode-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.mode-btn .icon-rocket,
.mode-btn .icon-search {
  margin-right: 3px;
}

.send-btn {
  background: #6b63ff;
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.send-btn:disabled {
  cursor: not-allowed;
  background: #c4c0ff;
}

.question-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
}

.progress-container {
  background: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.progress-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

/* 对号图标 */
.icon-check {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  border-radius: 50%;
  background: #6b63ff;
  color: #fff;
  font-size: 12px;
}

/* 加载图标 */
.icon-loading {
  width: 20px;
  height: 20px;
  display: inline-block;
  margin-right: 8px;
  border: 2px solid #6b63ff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: rotate 1s linear infinite;
}

/* 错误图标 */
.icon-error {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  border-radius: 50%;
  background: #ffecec;
  color: #ff4d4f;
  font-size: 12px;
  font-weight: bold;
}

.progress-text {
  font-size: 14px;
  color: #333;
}

/* 骨架屏样式：新增卡片占位，优化视觉层次 */
.skeleton-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shine 1.5s infinite;
  border-radius: 4px;
  width: 100%;
}

/* 骨架屏卡片：模拟结果项 */
.skeleton-card {
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-card-header {
  width: 35%;
  height: 18px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shine 1.5s infinite;
  border-radius: 4px;
}
.skeleton-card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 错误提示容器 */
.error-container {
  background: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  color: #ff4d4f;
}

.error-icon {
  font-size: 18px;
  margin-right: 8px;
}

.error-text {
  flex: 1;
  font-size: 14px;
}

.retry-btn {
  padding: 6px 12px;
  background: #6b63ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #554dff;
}

/* 动画定义 */
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes shine {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .search-process-page {
    padding: 15px 20px;
  }

  .title {
    font-size: 18px;
  }

  .search-box {
    flex-wrap: wrap;
  }

  .mode-buttons {
    margin: 10px 0;
    width: 100%;
    justify-content: space-between;
  }
}
</style>
