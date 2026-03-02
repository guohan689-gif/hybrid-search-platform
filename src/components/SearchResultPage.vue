<template>
  <div class="search-result-page">
    <!-- 顶部导航栏 -->
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
          alt="用户头像"
          class="user-avatar"
        />
        <span class="username">郭含</span>
        <span class="icon-arrow-down">▼</span>
      </div>
    </div>

    <!-- 搜索框区域（支持再次搜索） -->
    <div class="search-box">
      <input
        type="text"
        v-model="searchQuery"
        class="search-input"
        placeholder="输入问题再次搜索..."
        @keyup.enter="handleSearch"
      />
      <div class="mode-buttons">
        <button class="mode-btn" :class="{ active: currentMode === 'quick' }" @click="currentMode = 'quick'">
          <span class="icon-rocket">🚀</span>
          极速
        </button>
        <button class="mode-btn" :class="{ active: currentMode === 'explore' }" @click="currentMode = 'explore'">
          <span class="icon-search">🔍</span>
          探索
        </button>
      </div>
      <button class="send-btn" @click="handleSearch">
        <span class="icon-send">→</span>
      </button>
    </div>

    <!-- 搜索问题标题 -->
    <div class="question-title">{{ receivedQuestion || '大学生奖学金申请流程是什么' }}</div>


    <!-- 可展开/收起的进度区 -->
    <div 
      class="progress-wrapper"
      @click="toggleProgress"
    >
      <div class="progress-collapsed" v-if="!isProgressExpanded">
        <span class="check-icon">✓</span>
        <span class="collapsed-text">智能检索已完成（共{{ totalResults }}条结果）</span>
        <span class="toggle-icon" :style="{ transform: isProgressExpanded ? 'rotate(180deg)' : 'rotate(0)' }">↓</span>
      </div>
      <div class="progress-expanded" v-else>
        <div class="progress-item">
          <span class="icon-check">✓</span>
          <span class="progress-text">已完成应用检索（{{ filteredApps.length }}个）</span>
        </div>
        <div class="progress-item">
          <span class="icon-check">✓</span>
          <span class="progress-text">已完成文档检索（{{ filteredDocs.length }}个）</span>
        </div>
        <div class="progress-item">
          <span class="icon-check">✓</span>
          <span class="progress-text">已完成新闻检索（{{ filteredNews.length }}个）</span>
        </div>
        <div class="progress-item">
          <span class="icon-check">✓</span>
          <span class="progress-text">检索耗时：{{ totalTime }}秒</span>
        </div>
      </div>
    </div>

    <!-- 加载状态（再次搜索时显示） -->
    <div class="loading-container" v-if="isLoading">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在检索{{ currentMode === 'quick' ? '极速' : '探索' }}模式结果...</div>
    </div>

    <!-- 错误提示（接口请求失败时显示） -->
    <div class="error-container" v-if="isError">
      <span class="error-icon">×</span>
      <span class="error-text">{{ errorMessage }}</span>
      <button class="retry-btn" @click="handleSearch">重试</button>
    </div>

    <!-- 空结果提示（接口返回无数据时显示） -->
    <div class="empty-container" v-if="!isLoading && !isError && isEmptyResult">
      <div class="empty-icon">🔍</div>
      <div class="empty-title">未找到相关结果</div>
      <div class="empty-desc">尝试调整关键词或切换探索模式重新搜索</div>
      <button class="empty-retry-btn" @click="resetSearch">重新搜索</button>
    </div>

    <!-- 应用结果（提取标题和描述） -->
    <div class="result-group" v-if="!isLoading && !isError && filteredApps.length > 0">
      <h3 class="group-title">
        <span class="group-icon">📱</span>
        应用 
        <span class="count-text">共{{ filteredApps.length }}个应用</span>
      </h3>
      <div class="result-list app-list">
        <div class="app-card" v-for="(app, index) in displayApps" :key="`app-${app.db_id || index}`">
          <div class="card-icon" :style="{ backgroundColor: app.iconColor || '#ff6b6b' }">
            <span class="icon">📱</span>
          </div>
          <div class="card-content">
            <div class="card-title">{{extractAppTitle(app.description) }}</div>
            <div class="card-desc">{{ extractAppDesc(app.description) }}</div>
          </div>
        </div>
      </div>
      <button 
        class="expand-more-btn" 
        v-if="filteredApps.length > 8 && displayApps.length < filteredApps.length"
        @click="displayApps = filteredApps"
      >
        展开更多
      </button>
    </div>

    <!-- 新闻结果（提取标题和内容） -->
    <div class="result-group" v-if="!isLoading && !isError && filteredNews.length > 0">
      <h3 class="group-title">
        <span class="group-icon">📰</span>
        新闻 
        <span class="count-text">共{{ filteredNews.length }}条新闻</span>
      </h3>
      <div class="result-list news-list">
        <div class="news-item" v-for="(news, index) in displayNews" :key="`news-${news.db_id || index}`">
          <div class="news-number">{{ index + 1 }}</div>
          <div class="news-content">
            <div class="news-title">{{ extractContentTitle(news.content) }}</div>
            <div class="news-desc">
              {{ extractContentBody(news.content) }}
            </div>
            <div class="news-meta">
              <span class="source">来源：{{ news.source_type || '未知来源' }}</span>
              <span class="time">发布时间：{{ news.publish_time || '未知时间' }}</span>
            </div>
          </div>
        </div>
      </div>
      <button 
        class="expand-more-btn" 
        v-if="filteredNews.length > 8 && displayNews.length < filteredNews.length"
        @click="displayNews = filteredNews"
      >
        展开更多
      </button>
    </div>

    <!-- 文档结果（提取标题和内容） -->
    <div class="result-group" v-if="!isLoading && !isError && filteredDocs.length > 0">
      <h3 class="group-title">
        <span class="group-icon">📄</span>
        文档 
        <span class="count-text">共{{ filteredDocs.length }}个结果</span>
      </h3>
      <div class="result-list file-list">
        <div class="result-card file-card" v-for="(doc, index) in displayDocs" :key="`doc-${doc.db_id || index}`">
          <div class="file-header">
            <div class="card-title file-title">{{ extractContentTitle(doc.content) }}</div>
            <span class="file-type">{{ doc.source_type || '文档' }}</span>
          </div>
          <div class="card-desc file-desc">
            {{ extractContentBody(doc.content) }}
          </div>
          <div class="card-meta file-meta">
            <span class="meta-item">来源：{{ doc.source_type || '未知来源' }}</span>
            <span class="meta-item">发布时间：{{ doc.publish_time || '未知时间' }}</span>
          </div>
        </div>
      </div>
      <button 
        class="expand-more-btn" 
        v-if="filteredDocs.length > 8 && displayDocs.length < filteredDocs.length"
        @click="displayDocs = filteredDocs"
      >
        展开全部（共{{ filteredDocs.length }}条）
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "SearchResultPage",
  data() {
    return {
      // 本地存储搜索结果（匹配后端顶级结构）
      searchResult: {
        categories: {
          apps: { count: 0, results: [], threshold: 0 },
          docs: { count: 0, results: [], threshold: 0 },
          news: { count: 0, results: [], threshold: 0 }
        },
        original_query: "",
        rewritten_queries: [],
        timestamp: "",
        total_results: 0,
        total_time: 0,
        status: "success"
      },
      receivedQuestion: "",
      searchQuery: "",
      currentMode: "quick",
      isProgressExpanded: false,
      isLoading: false,
      isError: false,
      errorMessage: "",
      displayApps: [],
      displayNews: [],
      displayDocs: []
    };
  },
  computed: {
    // 从 categories 中提取各类型结果
    filteredApps() {
      return this.searchResult.categories?.apps?.results || [];
    },
    filteredNews() {
      return this.searchResult.categories?.news?.results || [];
    },
    filteredDocs() {
      return this.searchResult.categories?.docs?.results || [];
    },
    // 总结果数
    totalResults() {
      return this.searchResult.total_results || 
        (this.filteredApps.length + this.filteredNews.length + this.filteredDocs.length);
    },
    // 检索耗时
    totalTime() {
      return this.searchResult.total_time ? this.searchResult.total_time.toFixed(2) : "0.00";
    },
    // 判断是否为空结果
    isEmptyResult() {
      return this.filteredApps.length === 0 && 
             this.filteredNews.length === 0 && 
             this.filteredDocs.length === 0;
    }
  },
  watch: {
    // 监听searchResult变化，同步更新显示数据
    searchResult: {
      deep: true,
      handler(newVal) {
        this.receivedQuestion = newVal.original_query || "大学生奖学金申请流程是什么";
        this.updateDisplayData();
      }
    }
  },
  mounted() {
    this.initFromRoute();
  },
  methods: {
    // 提取应用的标题（从description中）
    extractAppTitle(description) {
      if (!description) return "未命名应用";
      // 优化正则：匹配"标题："后直到"，"或"描述："之前的内容
      const regex = /标题：([^，,描]+)/;
      const match = description.match(regex);
      return match ? match[1].trim() : "未命名应用";
    },
    
    
    // 提取应用的描述内容
    extractAppDesc(description) {
      if (!description) return "无描述";
      const regex = /描述：([^，,]+)/;
      const match = description.match(regex);
      return match ? match[1] : "无描述";
    },
    
    // 提取新闻/文档的标题
    extractContentTitle(content) {
      if (!content) return "无标题";
      const regex = /标题：([^，,]+)/;
      const match = content.match(regex);
      return match ? match[1] : "无标题";
    },
    
    // 提取新闻/文档的内容（截止到"内容之后"）
    extractContentBody(content) {
      if (!content) return "无内容";
      const regex = /内容：([\s\S]*?)(?=内容之后|$)/;
      const match = content.match(regex);
      return match ? match[1] : "无内容";
    },

    // 统一更新分页数据
    updateDisplayData() {
      this.displayApps = this.filteredApps.slice(0, 8);
      this.displayNews = this.filteredNews.slice(0, 8);
      this.displayDocs = this.filteredDocs.slice(0, 8);
    },
    
    // 从路由获取后端返回的搜索结果并解析
    initFromRoute() {
      const queryResult = this.$route.query.searchResult;
      if (queryResult) {
        try {
          const parsedResult = JSON.parse(queryResult);
          this.searchResult = {
            categories: parsedResult.categories || {
              apps: { count: 0, results: [], threshold: 0 },
              docs: { count: 0, results: [], threshold: 0 },
              news: { count: 0, results: [], threshold: 0 }
            },
            original_query: parsedResult.original_query || "",
            rewritten_queries: parsedResult.rewritten_queries || [],
            timestamp: parsedResult.timestamp || "",
            total_results: parsedResult.total_results || 0,
            total_time: parsedResult.total_time || 0,
            status: parsedResult.status || "success"
          };
          this.receivedQuestion = this.searchResult.original_query || "大学生奖学金申请流程是什么";
          this.currentMode = this.$route.query.mode || "quick";
          this.updateDisplayData();
          
          if (this.searchResult.status !== "success") {
            this.isError = true;
            this.errorMessage = "后端检索失败，请重新尝试";
          }
        } catch (e) {
          console.error("后端数据解析失败：", e);
          this.isError = true;
          this.errorMessage = "结果数据解析错误，请重新搜索";
        }
      } else {
        console.warn("路由中未获取到后端搜索结果");
        this.isError = true;
        this.errorMessage = "未获取到搜索结果，请重新搜索";
      }
    },
    
    // 切换进度区展开/收起
    toggleProgress() {
      this.isProgressExpanded = !this.isProgressExpanded;
    },
    
    // 处理再次搜索
    handleSearch() {
      const query = this.searchQuery.trim();
      if (!query) {
        alert("请输入搜索关键词（如：大学生奖学金申请材料）");
        return;
      }

      const targetPath = this.currentMode === 'explore' ? '/new_progress' : '/search-process';
      this.$router.push({
        path: targetPath,
        query: {
          question: query,
          mode: this.currentMode
        }
      });
    },
    
    // 重置搜索框
    resetSearch() {
      this.searchQuery = "";
      this.searchQuery.focus();
    }
  }
};
</script>

<style scoped>
/* 页面基础样式 */
.search-result-page {
  background: #fff;
  min-height: 100vh;
  padding: 24px 80px;
  box-sizing: border-box;
  font-family: "Inter", sans-serif;
}

/* 顶部导航 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.wuda-logo {
  width: 44px;
  height: 44px;
  margin-right: 12px;
  object-fit: contain;
}
.title {
  font-size: 22px;
  font-weight: 600;
  color: #1d2129;
  display: flex;
  align-items: center;
}
.user-info {
  display: flex;
  align-items: center;
}
.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  margin-right: 8px;
  object-fit: cover;
}
.username {
  font-size: 14px;
  color: #4e5969;
  margin-right: 6px;
}
.icon-arrow-down {
  font-size: 12px;
  color: #86909c;
  cursor: pointer;
  transition: transform 0.2s ease;
}

/* 搜索框 */
.search-box {
  display: flex;
  align-items: center;
  background: #f9fafb;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 24px;
  border: 1px solid #f0f2f5;
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 10px 12px;
  font-size: 15px;
  color: #4e5969;
  background: transparent;
  border-radius: 8px;
}
.search-input::placeholder {
  color: #999;
  font-size: 13px;
}
.mode-buttons {
  display: flex;
  margin-right: 12px;
}
.mode-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 8px;
  display: flex;
  align-items: center;
  font-size: 13px;
  background-color: #fff;
  color: #4e5969;
  transition: all 0.2s ease;
  border: 1px solid #e5e7eb;
}
.mode-btn.active {
  background-color: #165dff;
  color: #ffffff;
  border-color: #165dff;
}
.mode-btn .icon-rocket,
.mode-btn .icon-search {
  margin-right: 4px;
}
.send-btn {
  background: #165dff;
  color: #ffffff;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease;
}
.send-btn:hover {
  background: #0e4bdb;
}

/* 问题标题 */
.question-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}

/* 进度区 */
.progress-wrapper {
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.2s ease;
  border: 1px solid #f0f2f5;
}
.progress-wrapper:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}
.progress-collapsed {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
}
.check-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #165dff;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-right: 12px;
}
.collapsed-text {
  font-size: 16px;
  font-weight: 500;
  color: #1d2129;
  flex: 1;
}
.toggle-icon {
  font-size: 18px;
  color: #86909c;
  transition: transform 0.2s ease;
}
.progress-expanded {
  padding: 20px 24px;
  border-top: 1px solid #f0f2f5;
}
.progress-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.progress-item:last-child {
  margin-bottom: 0;
}
.icon-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e8f3ff;
  color: #165dff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin-right: 12px;
}
.progress-text {
  font-size: 14px;
  color: #4e5969;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
  border: 1px solid #f0f2f5;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f0f2f5;
  border-top: 4px solid #165dff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}
.loading-text {
  font-size: 14px;
  color: #4e5969;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误提示 */
.error-container {
  background: #fff0f0;
  border-left: 4px solid #f53f3f;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  border: 1px solid #ffebea;
}
.error-icon {
  color: #f53f3f;
  font-size: 18px;
  margin-right: 12px;
}
.error-text {
  flex: 1;
  font-size: 14px;
  color: #f53f3f;
}
.retry-btn {
  background: #f53f3f;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.retry-btn:hover {
  background: #d43737;
}

/* 空结果提示 */
.empty-container {
  text-align: center;
  padding: 60px 20px;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
  border: 1px solid #f0f2f5;
}
.empty-icon {
  font-size: 48px;
  color: #c9cdD4;
  margin-bottom: 20px;
}
.empty-title {
  font-size: 18px;
  font-weight: 500;
  color: #1d2129;
  margin-bottom: 8px;
}
.empty-desc {
  font-size: 14px;
  color: #86909c;
  margin-bottom: 24px;
}
.empty-retry-btn {
  background: #165dff;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.empty-retry-btn:hover {
  background: #0e4bdb;
}

/* 结果分组 */
.result-group {
  margin-bottom: 32px;
}
.group-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}
.group-icon {
  margin-right: 8px;
  font-size: 20px;
}
.count-text {
  font-size: 14px;
  color: #86909c;
  margin-left: 8px;
  font-weight: normal;
}

/* 应用结果样式 */
.app-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}
.app-card {
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #f0f2f5;
  padding: 16px;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  cursor: pointer;
}
.app-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: #e5e7eb;
}
.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  margin-right: 12px;
}
.card-content .card-title {
  font-size: 16px;
  font-weight: 500;
  color: #1d2129;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-content .card-desc {
  font-size: 13px;
  color: #86909c;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 新闻结果样式 */
.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}
.news-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #f0f2f5;
  transition: all 0.2s ease;
}
.news-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: #e5e7eb;
}
.news-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f9fafb;
  color: #86909c;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-right: 12px;
  flex-shrink: 0;
}
.news-content {
  flex: 1;
}
.news-title {
  font-size: 15px;
  font-weight: 500;
  color: #1d2129;
  margin-bottom: 8px;
  line-height: 1.4;
}
.news-desc {
  font-size: 13px;
  color: #4e5969;
  margin-bottom: 8px;
  line-height: 1.5;
}
.ai-tag {
  display: inline-block;
  background: #e8f3ff;
  color: #165dff;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 8px;
}
.news-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: #86909c;
}

/* 文档结果特有样式 */
.file-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}
.result-card {
  background: #ffffff;
  padding: 16px;
  border: 1px solid #f0f2f5;
  border-radius: 8px;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}
.result-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: #e5e7eb;
}
.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #1d2129;
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-desc {
  font-size: 14px;
  color: #4e5969;
  margin-bottom: 12px;
  line-height: 1.5;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 12px;
  color: #86909c;
}
.meta-item {
  display: inline-block;
  padding: 2px 6px;
  background: #f9fafb;
  border-radius: 4px;
}
.meta-item.score {
  color: #fa7d3c;
  background: #fff8f0;
  margin-left: auto;
}
.file-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
}
.file-title {
  -webkit-line-clamp: 1;
  margin-bottom: 0;
  flex: 1;
}
.file-type {
  font-size: 12px;
  color: #36b37e;
  background: #f0fff4;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 12px;
  white-space: nowrap;
}

/* 展开更多按钮 */
.expand-more-btn {
  background: none;
  border: 1px solid #165dff;
  color: #165dff;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
  margin-top: 8px;
  display: inline-flex;
  align-items: center;
}
.expand-more-btn::after {
  content: "↓";
  margin-left: 6px;
  font-size: 12px;
}
.expand-more-btn:hover {
  background: #e8f3ff;
}

/* 滚动条样式优化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #f9fafb;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .search-result-page {
    padding: 24px 40px;
  }
  .app-list {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
  .file-list {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .search-result-page {
    padding: 16px 16px;
  }
  .header {
    flex-wrap: wrap;
    gap: 12px;
  }
  .title {
    font-size: 18px;
    order: 3;
    width: 100%;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #f0f2f5;
  }
  .app-list, .file-list {
    grid-template-columns: 1fr;
  }
  .mode-buttons {
    margin-right: 8px;
  }
  .mode-btn {
    padding: 6px 10px;
    font-size: 12px;
  }
  .question-title {
    font-size: 16px;
  }
  .group-title {
    font-size: 16px;
  }
  .news-title {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .search-box {
    flex-wrap: wrap;
    gap: 12px;
  }
  .search-input {
    width: 100%;
    order: 1;
  }
  .mode-buttons {
    width: 100%;
    justify-content: center;
    order: 2;
    margin-right: 0;
  }
  .send-btn {
    order: 3;
    margin: 0 auto;
  }
  .progress-collapsed {
    padding: 16px;
  }
  .collapsed-text {
    font-size: 14px;
  }
  .expand-more-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
    