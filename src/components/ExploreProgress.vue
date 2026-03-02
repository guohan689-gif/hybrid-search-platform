<template>
  <div class="search-process-page">
    <!-- 头部：Logo+标题+用户信息 -->
    <div class="header">
      <img
        src="https://gimg3.baidu.com/search/src=https%3A%2F%2Fstatic-data.gaokao.cn%2Fupload%2Flogo%2F42.jpg%3Ft%3D1756742428&refer=http%3A%2F%2Fwww.baidu.com&app=2021&size=w931&n=0&g=0n&er=404&q=75&fmt=auto&maxorilen2heic=2000000?sec=1757178000&t=98d042f584c3cfa55238ac85a033e451"
        alt="武汉大学logo"
        class="wuda-logo"
        @error="handleLogoError"
      />
      <span class="title">武汉大学 | AI 智能搜索</span>
      <div class="user-info" @click="toggleUserMenu">
        <img
          src="https://picsum.photos/id/64/200"
          alt="用户头像"
          class="user-avatar"
          @error="handleAvatarError"
        />
        <span class="username">郭含</span>
        <span class="icon-arrow-down" :class="{ 'rotate-180': isUserMenuOpen }">▼</span>
        <!-- 用户下拉菜单 -->
        <div class="user-menu" v-if="isUserMenuOpen">
          <div class="menu-item">个人中心</div>
          <div class="menu-item">搜索历史</div>
          <div class="menu-item text-danger">退出登录</div>
        </div>
      </div>
    </div>

    <!-- 搜索框：统一样式 -->
    <div class="search-box">
      <input
        type="text"
        :value="receivedQuestion"
        class="search-input"
        readonly
        placeholder="请输入搜索问题"
        title="当前搜索关键词"
      />
      <div class="mode-buttons">
        <button 
          class="mode-btn" 
          :class="{ 'active': currentMode === 'fast' }" 
          :disabled="isGenerating" 
          @click="$router.push({ path: '/search', query: { q: encodeURIComponent(receivedQuestion), mode: 'fast' } })" 
          :title="isGenerating ? '生成中，暂不支持切换模式' : '极速模式'"
        >
          <span class="icon-rocket">🚀</span>
          极速
        </button>
        <button 
          class="mode-btn" 
          :class="{ 'active': currentMode === 'explore' }" 
          :disabled="isGenerating" 
          @click="$router.push({ path: '/explore', query: { q: encodeURIComponent(receivedQuestion), mode: 'explore' } })" 
          :title="isGenerating ? '生成中，当前为探索模式' : '探索模式'"
        >
          <span class="icon-search">🔍</span>
          探索
        </button>
      </div>
      <button 
        class="send-btn" 
        :disabled="isGenerating" 
        @click="handleSend" 
        :title="isGenerating ? '生成中，请勿重复提交' : '已提交搜索请求'"
      >
        <span class="icon-send">→</span>
      </button>
    </div>

    <!-- 问题标题：统一样式 -->
    <div class="question-title" :title="receivedQuestion">
      {{ receivedQuestion }}
    </div>

    <!-- 进度流程：适配目标进度区样式 -->
    <div class="progress-wrapper" @click="toggleProgressCollapse">
      <!-- 进度区标题栏：控制折叠/展开 + 显示状态文本 -->
      <div class="progress-collapsed" v-if="isProgressCollapsed">
        <span class="check-icon">
          <span v-if="progress.summary === 'done'">✓</span>
          <span class="loading-icon" v-else-if="progress.summary === 'loading'"></span>
          <span v-else-if="progress.summary === 'error'">×</span>
        </span>
        <span class="collapsed-text">
          {{ progress.summary === 'done' ? '智能检索已完成' : 
            progress.summary === 'loading' ? '分析并完成总结中' : '检索出现错误' }}
        </span>
        <span class="toggle-icon" :class="{ 'rotate-180': !isProgressCollapsed }">↓</span>
      </div>

      <!-- 可折叠内容区：进度步骤 -->
      <div class="progress-expanded" v-else>
        <div class="progress-steps">
          <!-- 第一步：分析问题并定位研究方向 -->
          <div
            class="progress-item"
            :class="{ 'completed': progress.analysis === 'done', 'error': progress.analysis === 'error' }"
          >
            <span class="icon-check">
              <span v-if="progress.analysis === 'done'">✓</span>
              <span class="loading-icon" v-else-if="progress.analysis === 'loading'"></span>
              <span v-else-if="progress.analysis === 'error'">×</span>
            </span>
            <span class="progress-text">{{ progress.analysisText }}</span>
          </div>
          
          <!-- 第二步：查询应用 -->
          <div
            class="progress-item"
            :class="{ 'completed': progress.app === 'done', 'error': progress.app === 'error' }"
          >
            <span class="icon-check">
              <span v-if="progress.app === 'done'">✓</span>
              <span class="loading-icon" v-else-if="progress.app === 'loading'"></span>
              <span v-else-if="progress.app === 'error'">×</span>
            </span>
            <span class="progress-text">{{ progress.appText }}</span>
          </div>
          
          <!-- 第三步：查询新闻 -->
          <div
            class="progress-item"
            :class="{ 'completed': progress.news === 'done', 'error': progress.news === 'error' }"
          >
            <span class="icon-check">
              <span v-if="progress.news === 'done'">✓</span>
              <span class="loading-icon" v-else-if="progress.news === 'loading'"></span>
              <span v-else-if="progress.news === 'error'">×</span>
            </span>
            <span class="progress-text">{{ progress.newsText }}</span>
          </div>
          
          <!-- 第四步：查询文件 -->
          <div
            class="progress-item"
            :class="{ 'completed': progress.file === 'done', 'error': progress.file === 'error' }"
          >
            <span class="icon-check">
              <span v-if="progress.file === 'done'">✓</span>
              <span class="loading-icon" v-else-if="progress.file === 'loading'"></span>
              <span v-else-if="progress.file === 'error'">×</span>
            </span>
            <span class="progress-text">{{ progress.fileText }}</span>
          </div>
          
          <!-- 第五步：分析并完成总结 -->
          <div
            class="progress-item"
            :class="{ 'completed': progress.summary === 'done', 'error': progress.summary === 'error' }"
          >
            <span class="icon-check">
              <span v-if="progress.summary === 'done'">✓</span>
              <span class="loading-icon" v-else-if="progress.summary === 'loading'"></span>
              <span v-else-if="progress.summary === 'error'">×</span>
            </span>
            <span class="progress-text">{{ progress.summaryText }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 大模型生成文本：独立区块 -->
    <div class="summary-container" v-if="summaryContent">
      <div class="summary-content">
        <div class="summary-text">{{ summaryContent }}</div>
      </div>
    </div>

    <!-- 检索结果展示区：统一结果样式 -->
    <div class="results-container" v-if="Object.keys(exploreCategories).length">
      <!-- 应用结果 -->
      <div class="result-group" v-if="exploreCategories.apps?.length">
        <h3 class="group-title">
          <span class="group-icon">📱</span>
          相关应用 
          <span class="count-text">共{{ exploreCategories.apps.length }}个应用</span>
        </h3>
        <div class="result-list app-list">
          <div class="app-card" v-for="(app, idx) in displayApps" :key="app.id" @click="handleCardClick(app.url || '#')">
            <div class="card-icon" :style="{ backgroundColor: getAppColor(idx) }">
              <span class="icon">📱</span>
            </div>
            <div class="card-content">
              <div class="card-title">{{ app.name || `应用${idx+1}` }}</div>
              <div class="card-desc">
                {{ app.description || '无应用描述' }}
              </div>
              <div class="card-meta">
                <span class="meta-item">{{ formatTime(app.publish_time) }}</span>
              </div>
            </div>
          </div>
        </div>
        <!-- 展开更多按钮 -->
        <button 
          class="expand-more-btn" 
          v-if="exploreCategories.apps.length > 8 && displayApps.length < exploreCategories.apps.length"
          @click="displayApps = exploreCategories.apps"
        >
          展开更多
        </button>
      </div>

      <!-- 新闻结果 -->
      <div class="result-group" v-if="exploreCategories.news?.length">
        <h3 class="group-title">
          <span class="group-icon">📰</span>
          相关新闻 
          <span class="count-text">共{{ exploreCategories.news.length }}条新闻</span>
        </h3>
        <div class="result-list news-list">
          <div class="news-item" v-for="(news, idx) in displayNews" :key="news.id" @click="handleCardClick(news.url || '#')">
            <div class="news-number">{{ idx + 1 }}</div>
            <div class="news-content">
              <div class="news-title">{{ news.title || `新闻${idx+1}` }}</div>
              <div class="news-desc">
                {{ news.content || '无正文信息' }}
              </div>
              <div class="news-meta">
                <span class="source">{{ news.source || '教务处' }}</span>
                <span class="time">{{ formatTime(news.publish_time) }}</span>
              </div>
            </div>
          </div>
        </div>
        <!-- 展开更多按钮 -->
        <button 
          class="expand-more-btn" 
          v-if="exploreCategories.news.length > 8 && displayNews.length < exploreCategories.news.length"
          @click="displayNews = exploreCategories.news"
        >
          展开更多
        </button>
      </div>

      <!-- 文件结果 -->
      <div class="result-group" v-if="exploreCategories.docs?.length">
        <h3 class="group-title">
          <span class="group-icon">📄</span>
          相关文件 
          <span class="count-text">共{{ exploreCategories.docs.length }}个结果</span>
        </h3>
        <div class="result-list file-list">
          <div class="result-card file-card" v-for="(doc, idx) in displayDocs" :key="doc.id" @click="handleCardClick(doc.url || '#')">
            <div class="file-header">
              <div class="card-title file-title">{{ doc.title || `文件${idx+1}` }}</div>
              <span class="file-type">{{ getFileType(doc) }}</span>
            </div>
            <div class="card-desc file-desc">
              {{ doc.content || '无文件内容' }}
            </div>
            <div class="card-meta file-meta">
              <span class="meta-item">来源：{{ doc.source || '教务处' }}</span>
              <span class="meta-item">发布时间：{{ formatTime(doc.publish_time) }}</span>
            </div>
          </div>
        </div>
        <!-- 展开更多按钮 -->
        <button 
          class="expand-more-btn" 
          v-if="exploreCategories.docs.length > 8 && displayDocs.length < exploreCategories.docs.length"
          @click="displayDocs = exploreCategories.docs"
        >
          展开全部（共{{ exploreCategories.docs.length }}条）
        </button>
      </div>
    </div>

    <!-- 错误提示：统一样式 -->
    <div class="error-container" v-if="progress.summary === 'error'">
      <span class="error-icon">×</span>
      <span class="error-text">{{ errorMessage }}</span>
      <div class="error-actions">
        <button class="retry-btn" @click="retrySearch" :disabled="isRetrying">
          <span class="icon-loading small" v-if="isRetrying"></span>
          {{ isRetrying ? "重试中..." : "重新探索" }}
        </button>
        <button class="cancel-btn" @click="goBack">返回首页</button>
      </div>
    </div>
  </div>
</template>


<script>
import { MessageBox } from 'element-ui'; 
export default {
  name: "SearchProcessPage",
  data() {
    return {
      isGenerating: false,
      receivedQuestion: "",
      isAllFinished: false,
      errorMessage: "接口检索失败，请检查网络或重试",
      isUserMenuOpen: false,  
      currentMode: 'explore',     
      isStopping: false,      
      isRetrying: false,      
      // 进度区折叠状态（默认展开，仅summary步骤自动收起）
      isProgressCollapsed: false,
      progress: {
        analysis: "loading",
        analysisText: "分析问题并定位研究方向...",
        app: "waiting",
        appText: "等待查询相关应用...",
        news: "waiting",
        newsText: "等待查询相关新闻...",
        file: "waiting",
        fileText: "等待查询相关文件...",
        summary: "waiting",
        summaryText: "等待分析并完成总结..."
      },
      timers: [],
      abortController: null,
      isApiRequestPending: false,
      // 大模型总结文本（逐字拼接）
      summaryContent: "",
      // 检索结果数据（实时更新）
      exploreCategories: {},
      // 分页显示控制
      displayApps: [],
      displayNews: [],
      displayDocs: [],
      // 应用卡片颜色池（用于区分不同应用）
      appColors: ['#ff6b6b', '#36b37e', '#ffab00', '#0fc6c2', '#722ed1', '#f5222d', '#fa8c16', '#1890ff']
    };
  },
  mounted() {
    this.receivedQuestion = this.$route?.query?.question
      ? decodeURIComponent(this.$route.query.question)  
      : "默认搜索问题";
    this.startExploreStepProgress();
  },
  beforeDestroy() {
    // 清除所有定时器
    this.timers.forEach(timer => clearTimeout(timer));
    // 中断未完成的请求
    if (this.abortController && this.isApiRequestPending) this.abortController.abort();
  },
  computed: {
    allSteps() {
      return ["analysis", "app", "news", "file", "summary"];
    }
  },
  methods: {
    // 获取应用卡片颜色（循环使用颜色池）
    getAppColor(index) {
      return this.appColors[index % this.appColors.length];
    },
    
    // 获取文件类型（简单判断，可根据实际需求扩展）
    getFileType(doc) {
      // 如果有文件后缀，提取后缀作为类型
      if (doc.title && doc.title.includes('.')) {
        const ext = doc.title.split('.').pop().toLowerCase();
        const typeMap = {
          'doc': 'Word文档',
          'docx': 'Word文档',
          'pdf': 'PDF文档',
          'xls': 'Excel表格',
          'xlsx': 'Excel表格',
          'ppt': 'PPT演示',
          'pptx': 'PPT演示',
          'txt': '文本文件',
          'pdf': 'PDF文档'
        };
        return typeMap[ext] || `${ext.toUpperCase()}文件`;
      }
      return '文档';
    },
    
    // 格式化时间显示
    formatTime(timeStr) {
      if (!timeStr) return '未知时间';
      
      // 尝试解析多种时间格式
      const date = new Date(timeStr);
      if (!isNaN(date.getTime())) {
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        }).replace(',', ' ');
      }
      
      // 如果无法解析，直接返回原始字符串
      return timeStr;
    },
    
    // Logo加载失败处理
    handleLogoError(e) {
      e.target.src = "https://via.placeholder.com/40x40?text=武大";
    },

    // 头像加载失败处理
    handleAvatarError(e) {
      e.target.src = "https://via.placeholder.com/32x32?text=用户";
    },

    // 切换用户菜单显示/隐藏
    toggleUserMenu() {
      this.isUserMenuOpen = !this.isUserMenuOpen;
    },

    // 返回首页
    goBack() {
      this.$router.push({ path: "/" });
    },

    // 切换进度区折叠/展开状态
    toggleProgressCollapse() {
      this.isProgressCollapsed = !this.isProgressCollapsed;
    },

    // 检查所有步骤是否完成
    checkAllFinished() {
      this.isAllFinished = this.allSteps.every(
        step => this.progress[step] === "done" || this.progress[step] === "error"
      );
      this.isGenerating = !this.isAllFinished;  
    },

    // 延迟执行函数（统一管理定时器）
    delayExecute(callback, delay = 1000) {
      const timer = setTimeout(callback, delay);
      this.timers.push(timer);
      return timer;
    },

    // 执行单个进度步骤
    runStep(step, delay, { loadingText, doneText, errorText }) {
      // 参数验证
      if (!step || !this.progress.hasOwnProperty(step)) {
        console.error(`无效的步骤名称: ${step}`);
        return Promise.reject(new Error(`无效的步骤: ${step}`));
      }

      return new Promise((resolve, reject) => {
        // 记录当前步骤初始状态，用于异常恢复
        const initialState = this.progress[step];
        const initialText = this.progress[`${step}Text`];
        
        try {
          // 设置加载状态
          this.progress[step] = "loading";
          this.progress[`${step}Text`] = loadingText || `处理中...`;
          this.checkAllFinished();

          // 创建延迟执行的计时器
          const timerId = this.delayExecute(() => {
            try {
              // 设置完成状态
              this.progress[step] = "done";
              this.progress[`${step}Text`] = doneText || "处理完成";
              this.checkAllFinished();
              resolve({ step, status: "done" });
            } catch (error) {
              console.error(`步骤 ${step} 执行失败:`, error);
              // 异常时恢复状态
              this.progress[step] = "error";
              this.progress[`${step}Text`] = `处理异常: ${error.message}`;
              this.checkAllFinished();
              reject({ step, message: `执行异常: ${error.message}` });
            }
          }, delay);

          // 提供取消步骤的方法
          this.cancelStep = () => {
            clearTimeout(timerId);
            // 恢复初始状态
            this.progress[step] = initialState;
            this.progress[`${step}Text`] = initialText;
            this.checkAllFinished();
            reject({ step, message: "步骤已取消" });
          };
        } catch (error) {
          console.error(`步骤 ${step} 初始化失败:`, error);
          // 初始化失败时恢复状态
          this.progress[step] = initialState;
          this.progress[`${step}Text`] = initialText;
          this.checkAllFinished();
          reject({ step, message: `初始化失败: ${error.message}` });
        }
      });
    },

    // 开始探索流程的进度展示
    async startExploreStepProgress() {
      try {
        // 第一步：分析问题并定位研究方向
        await this.runStep("analysis", 1500, {
          doneText: "分析问题并定位研究方向完成",
          errorText: "分析问题失败，请重试"
        });

        // 第二步：查询应用
        await this.runStep("app", 1200, {
          loadingText: "正在查询相关应用...",
          doneText: "相关应用查询完成",
          errorText: "查询相关应用失败"
        });

        // 第三步：查询新闻
        await this.runStep("news", 1300, {
          loadingText: "正在查询相关新闻...",
          doneText: "相关新闻查询完成",
          errorText: "查询相关新闻失败"
        });

        // 第四步：查询文件
        await this.runStep("file", 1400, {
          loadingText: "正在查询相关文件...",
          doneText: "相关文件查询完成",
          errorText: "查询相关文件失败"
        });

        // 最后一步：分析并完成总结（自动收起进度区）
        this.progress.summary = "loading";
        this.progress.summaryText = "分析并完成总结中...";
        this.isProgressCollapsed = true; // 自动收起进度区，显示标题
        this.checkAllFinished();
        this.isGenerating = false;
        await this.callExploreApi();
      } catch (error) {
        const failedStep = error.step || "summary";
        this.progress[failedStep] = "error";
        this.progress[`${failedStep}Text`] = error.message || `步骤执行失败`;
        this.errorMessage = error.message || "探索流程执行失败，请重试";
        this.checkAllFinished();
      }
    },

    // 调用探索模式API
    async callExploreApi() {
      try {
        this.isGenerating = true;
        this.abortController = new AbortController();
        const signal = this.abortController.signal;
        this.summaryContent = "";
        this.exploreCategories = {};
        this.isApiRequestPending = true;

        const requestBody = {
          query: this.receivedQuestion.trim(),
          mode: this.currentMode,
          categories: ["apps", "news", "docs"],
          limit: 10,
          timestamp: Date.now()  
        };

        // 接口调用逻辑
        const response = await Promise.race([
          fetch("http://localhost:5003/api/search/deep", {
            method: "POST",
            signal,
            headers: {
              "Content-Type": "application/json",
              "Accept": "text/event-stream"
            },
            body: JSON.stringify(requestBody)
          }),
          new Promise((_, reject) => {
            this.delayExecute(() => {
              reject(new Error("请求超时，请检查网络连接"));
            }, 80000);
          })
        ]);

        if (!response.ok) {
          throw new Error(`请求失败（${response.status}）：${response.statusText || '未知错误'}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        const parseStream = async () => {
          try {
            const { done, value } = await reader.read();

            if (done) {
              this.progress.summary = "done";
              this.progress.summaryText = "智能检索已完成";
        this.isApiRequestPending = false;
        this.checkAllFinished();

              // 更新分页数据
              this.displayApps = this.exploreCategories.apps?.slice(0, 8) || [];
              this.displayNews = this.exploreCategories.news?.slice(0, 8) || [];
              this.displayDocs = this.exploreCategories.docs?.slice(0, 8) || [];

              localStorage.setItem("exploreResult", JSON.stringify({
                question: this.receivedQuestion,
                mode: "explore",
                summary: this.summaryContent || "未获取到总结内容",
                categories: this.exploreCategories
              }));

              return;
            }

            const chunk = decoder.decode(value, { stream: true });
            const dataSegments = chunk.split("\n\n")
              .map(seg => seg.trim())
              .filter(seg => seg.startsWith("data: "));

            dataSegments.forEach(seg => {
              try {
                const data = JSON.parse(seg.slice(6).trim());
                switch (data.type) {
                  case "summary":
                    // 逐字添加总结内容，实现打字效果
                    if (data.content) {
                      this.summaryContent += data.content;
                    }
                    this.progress.summaryText = `分析并完成总结中（已生成 ${this.summaryContent.length} 字）`;
                    break;
                  case "result":
                    // 实时更新检索结果
                    this.exploreCategories = { ...this.exploreCategories, ...data.content };
                    
                    // 初始化分页数据
                    if (this.exploreCategories.apps && this.displayApps.length === 0) {
                      this.displayApps = this.exploreCategories.apps.slice(0, 8);
                    }
                    if (this.exploreCategories.news && this.displayNews.length === 0) {
                      this.displayNews = this.exploreCategories.news.slice(0, 8);
                    }
                    if (this.exploreCategories.docs && this.displayDocs.length === 0) {
                      this.displayDocs = this.exploreCategories.docs.slice(0, 8);
                    }
                    
                    // 更新步骤计数文本
                    if (this.exploreCategories.apps?.length) {
                      this.progress.appText = `相关应用查询完成（找到 ${this.exploreCategories.apps.length} 条）`;
                    }
                    if (this.exploreCategories.news?.length) {
                      this.progress.newsText = `相关新闻查询完成（找到 ${this.exploreCategories.news.length} 条）`;
                    }
                    if (this.exploreCategories.docs?.length) {
                      this.progress.fileText = `相关文件查询完成（找到 ${this.exploreCategories.docs.length} 条）`;
                    }
                    break;
                  case "error":
                    throw new Error(data.message || "服务器返回错误");
                }
              } catch (err) {
                console.warn("解析数据片段失败：", err, "片段内容：", seg);
              }
            });

            await parseStream();
          } catch (readErr) {
            throw new Error(`数据解析失败：${readErr.message}`);
          }
        };

        await parseStream();
        // 所有数据处理完成，更新状态
        this.progress.summary = 'done';
        this.progress.summaryText = '分析总结完成';
        this.isAllFinished = true;
        this.isGenerating = false;
      } catch (error) {
        this.isGenerating = false;
        // 排除用户主动中断的错误
        if (error.name !== "AbortError") {
          this.progress.summary = "error";
          this.progress.summaryText = "分析总结失败";
          this.errorMessage = error.message || "探索过程发生错误，请重试";
          this.checkAllFinished();
        }
      } finally {
        this.isGenerating = false;
      }
    },

    // 处理卡片点击
    handleCardClick(url) {
      if (url && url !== '#') {
        url.startsWith("http") ? window.open(url, "_blank") : this.$router.push(url);
      } else {
        alert("暂无相关链接");
      }
    },

    // 处理发送按钮点击
    handleSend() {
      this.retrySearch();
    },

    // 重试搜索
    retrySearch() {
      if (this.isRetrying) return;

      this.isRetrying = true;
      // 重置状态
      this.progress = {
        analysis: "loading",
        analysisText: "分析问题并定位研究方向...",
        app: "waiting",
        appText: "等待查询相关应用...",
        news: "waiting",
        newsText: "等待查询相关新闻...",
        file: "waiting",
        fileText: "等待查询相关文件...",
        summary: "waiting",
        summaryText: "等待分析并完成总结..."
      };
      this.isAllFinished = false;
      this.errorMessage = "接口检索失败，请检查网络或重试";
        this.isApiRequestPending = false;
      this.isProgressCollapsed = false; // 重置为展开状态
      
      // 中断上一次未完成的请求
      if (this.abortController) {
        this.abortController.abort();
        this.abortController = null;
      }

      // 清空状态数据
      this.summaryContent = "";
      this.exploreCategories = {};
      this.displayApps = [];
      this.displayNews = [];
      this.displayDocs = [];
      this.timers = [];

      // 延迟启动，避免UI闪烁
      this.delayExecute(() => {
        this.startExploreStepProgress();
        this.isRetrying = false;
      }, 600);
    }
  }
};
</script>

<style scoped>
/* 页面基础样式 - 与结果页统一 */
.search-process-page {
  background: #fff;
  min-height: 100vh;
  padding: 24px 80px;
  box-sizing: border-box;
  font-family: "Inter", sans-serif;
}

/* 顶部导航 - 与结果页统一 */
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
  position: relative;
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

/* 用户下拉菜单 */
.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 160px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 8px 0;
  margin-top: 5px;
  z-index: 100;
  border: 1px solid #f0f2f5;
}
.menu-item {
  padding: 8px 16px;
  font-size: 14px;
  color: #4e5969;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.menu-item:hover {
  background-color: #f9fafb;
}
.text-danger {
  color: #f53f3f;
}

/* 搜索框 - 与结果页统一 */
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
.send-btn:disabled {
  background: #c9d1e3;
  cursor: not-allowed;
}

/* 问题标题 - 与结果页统一 */
.question-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 进度区 - 与结果页进度区样式统一 */
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
.progress-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.progress-item {
  display: flex;
  align-items: center;
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
.progress-item.completed .icon-check {
  background: #165dff;
  color: #fff;
}
.progress-item.error .icon-check {
  background: #ffebea;
  color: #f53f3f;
}
.progress-text {
  font-size: 14px;
  color: #4e5969;
}
.progress-item.completed .progress-text {
  color: #165dff;
  font-weight: 500;
}
.progress-item.error .progress-text {
  color: #f53f3f;
}

/* 大模型总结文本容器 */
.summary-container {
  background: #fff;
  padding: 20px;
  margin-bottom: 24px;
}
.summary-content {
  padding: 0;
}
.summary-text {
  font-size: 15px;
  color: #4e5969;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 检索结果容器样式 - 与结果页统一 */
.results-container {
  padding: 0;
  margin-bottom: 0;
}

/* 结果分组样式 - 与结果页统一 */
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

/* 应用结果样式 - 与结果页统一 */
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
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
  color: #86909c;
}

/* 新闻结果样式 - 与结果页统一 */
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
  cursor: pointer;
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
.relevance {
  margin-left: auto;
}

/* 文档结果样式 - 与结果页统一 */
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
  cursor: pointer;
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
  margin-bottom: 0;
  font-size: 12px;
  color: #86909c;
}
.meta-item {
  display: inline-block;
  padding: 2px 6px;
  background: #f9fafb;
  border-radius: 4px;
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

/* 展开更多按钮 - 与结果页统一 */
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

/* 加载状态 - 与结果页统一 */
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

/* 错误提示 - 与结果页统一 */
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
.error-actions {
  display: flex;
  gap: 10px;
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
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.retry-btn:hover {
  background: #d43737;
}
.retry-btn:disabled {
  background: #ffccc7;
  cursor: not-allowed;
}
.cancel-btn {
  background: #fff;
  color: #4e5969;
  border: 1px solid #f0f2f5;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.cancel-btn:hover {
  background: #f9fafb;
  border-color: #e5e7eb;
}

/* 动画效果 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.loading-icon {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
.icon-loading.small {
  width: 14px;
  height: 14px;
  border-width: 2px;
}

/* 响应式调整 - 与结果页统一 */
@media (max-width: 1200px) {
  .search-process-page {
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
  .search-process-page {
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
  .news-meta {
    flex-direction: column;
    gap: 4px;
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
  .error-container {
    flex-direction: column;
    align-items: flex-start;
  }
  .error-actions {
    width: 100%;
    justify-content: space-between;
    margin-top: 12px;
  }
}

/* 通用工具类 */
.rotate-180 {
  transform: rotate(180deg);
}

/* 滚动条样式优化 - 与结果页统一 */
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
</style>
