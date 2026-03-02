<template>
  <div class="search-page">
    <div class="user-info">
      <img src="https://picsum.photos/id/64/200" alt="用户头像" class="avatar" />
      <span class="username">郭含</span>
      <i class="icon-arrow-down"></i>
    </div>
    
    <div class="logo-container">
      <img src="https://gimg3.baidu.com/search/src=https%3A%2F%2Fstatic-data.gaokao.cn%2Fupload%2Flogo%2F42.jpg%3Ft%3D1756742428&refer=http%3A%2F%2Fwww.baidu.com&app=2021&size=w931&n=0&g=0n&er=404&q=75&fmt=auto&maxorilen2heic=2000000?sec=1757178000&t=98d042f584c3cfa55238ac85a033e451" alt="武汉大学logo" class="wuda-logo" />
      <span class="title">武汉大学 | AI 智能搜索</span>
    </div>
    
    <p class="subtitle">一站式搜索与多源内容调用能力，覆盖应用、新闻、文件核心资源</p>
    
    <div class="search-box">
      <input 
        type="text" 
        class="search-input"
        placeholder="请输入您的问题"
        v-model="searchQuery"
        @keyup.enter="handleSearch"
      />
      
      <!-- 极速/探索模式按钮组 - 左下角 -->
      <div class="search-buttons">
        <button 
          class="mode-btn" 
          :class="{ active: currentMode === 'quick' }"
          @click="currentMode = 'quick'"
        >
          <i class="icon-speed"></i>
          <span>极速</span>
        </button>
        <button 
          class="mode-btn" 
          :class="{ active: currentMode === 'explore' }"
          @click="currentMode = 'explore'"
        >
          <i class="icon-explore"></i>
          <span>探索</span>
        </button>
      </div>
      
      <button class="send-btn" @click="handleSearch">
        <i class="icon-send"></i>
      </button>
    </div>
    
    <div class="hot-questions">
      <!-- 热门问题标题 -->
      <div class="hot-title">热门问题</div>
      <button class="question-btn" v-for="(question, index) in hotQuestions" :key="index" @click="selectQuestion(question)">
        {{ question }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "SearchPage",
  data() {
    return {
      searchQuery: "",
      currentMode: "quick", // 默认选中极速模式
      hotQuestions: [
        "大学生奖学金申请流程是什么",
        "活动广场里咋报名社团活动呀？报名后不想参加了，如何取消报名？",
        "报销要啥材料？",
        "我要请假",
        "校园卡丢了"
      ]
    };
  },
  methods: {
    handleSearch() {
      console.log('进入handleSearch方法');
      const trimmedQuery = this.searchQuery.trim();
      if (trimmedQuery) {
        console.log('搜索内容有效，准备跳转，当前模式：', this.currentMode);
        // 根据模式区分跳转路由：极速→原进度页，探索→new_progress页
        const targetPath = this.currentMode === 'explore' ? '/new_progress' : '/search-process';
        const targetRoute = {
          path: targetPath,
          query: { 
            question: trimmedQuery,
            mode: this.currentMode // 携带模式参数，供目标页使用
          }
        };

        const currentRouteStr = JSON.stringify({
          path: this.$route.path,
          query: this.$route.query
        });
        const targetRouteStr = JSON.stringify(targetRoute);

        if (currentRouteStr !== targetRouteStr) {
          this.$router.push(targetRoute);
        }
      } else {
        // 空输入提示
        alert('请输入您要搜索的问题');
      }
    },

    // 修改：热门问题仅填充到搜索框，不直接跳转
    selectQuestion(question) {
      this.searchQuery = question;
      // 可选：填充后自动聚焦搜索框，提升用户体验
      this.$nextTick(() => {
        const inputElement = document.querySelector('.search-input');
        if (inputElement) {
          inputElement.focus();
        }
      });
      // 移除原有的自动跳转逻辑，保留用户手动点击发送按钮的操作权
      console.log(`已将热门问题填充到搜索框：${question}`);
    }
  }
};
</script>

<style scoped>
.search-page {
  background: linear-gradient(to right, #f8f9fd, #e6e8f6);
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* 用户信息区域 */
.user-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-bottom: 60px;
  font-size: 14px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin-right: 8px;
  object-fit: cover;
  border: 1px solid #eee;
}

.username {
  margin-right: 5px;
  color: #333;
}

.icon-arrow-down {
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid #666;
  cursor: pointer;
  margin-top: 3px;
}

/* Logo区域 */
.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
}

.wuda-logo {
  width: 52px;
  height: 52px;
  margin-right: 12px;
  object-fit: contain;
}

.title {
  font-size: 30px;
  font-weight: 700;
  color: #333;
}

.subtitle {
  text-align: center;
  margin-bottom: 40px;
  color: #666;
  font-size: 15px;
  max-width: 650px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.5;
}

/* 搜索框区域 - 不使用 flex，使用绝对定位实现更自由的高度控制 */
.search-box {
  width: 750px;
  height: 180px; /* 明显增加高度，比如从 90px → 120px */
  margin: 0 auto 40px;
  background: #fff;
  border-radius: 12px;
  padding: 0 20px;
  box-shadow: 0 3px 15px rgba(0, 0, 0, 0.08);
  box-sizing: border-box;
  position: relative; /* 父容器相对定位 */
}

.search-input {
  width: calc(100% - 160px); /* 减去左右两侧按钮的宽度 */
  height: 100%; /* 占据整个父容器的高度 */
  border: none;
  outline: none;
  font-size: 14px; /* 调整字体大小 */
  color: #333;
  padding: 10px 15px; /* 增加上下内边距，使文本有更多空间 */
  border-radius: 8px;
  background: transparent;
  box-sizing: border-box;
  position: relative;
}

.search-input::placeholder {
  color: #999;
  font-size: 12px; /* 进一步减小占位符字体大小 */
  text-indent: 4px; /* 微调文本缩进，确保从左上角开始 */
  position: absolute;
  top: 10px; /* 根据padding调整，确保位于顶部 */
  left: 10px; /* 确保从左侧开始 */
}

/* 模式按钮组 - 绝对定位在左下角 */
.search-buttons {
  position: absolute;
  left: 20px;
  bottom: 20px; /* 可自由调整距离底部的位置 */
  display: flex;
  gap: 8px;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  background: #f5f5f5;
  font-size: 14px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-btn.active {
  background: #6b63ff;
  color: white;
  border-color: #6b63ff;
}

.mode-btn:hover:not(.active) {
  background: #eee;
}

/* 发送按钮 - 绝对定位在右下角 */
.send-btn {
  position: absolute;
  right: 20px; /* 距离右侧的距离根据需要调整 */
  bottom: 20px; /* 移动到底部 */
  background: #6b63ff;
  color: white;
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.send-btn:hover {
  background: #5a53e0;
  transform: translateY(-50%) scale(1.05);
}

.icon-send {
  display: inline-block;
  width: 24px; /* 稍微增大图标 */
  height: 24px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M2.05 13h19.9c.07-.23.1-.46.1-.7s-.03-.47-.1-.7H2.05c-.07.23-.1.47-.1.7s.03.47.1.7zM12 17.5c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7zm0-12c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

/* 热门问题 - 新增标题样式，优化布局 */
.hot-questions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px 16px;
  max-width: 900px;
  margin: 0 auto;
  padding-top: 10px;
}

.hot-title {
  width: 100%;
  text-align: center;
  font-size: 16px;
  color: #666;
  margin-bottom: 12px;
  font-weight: 500;
}

.question-btn {
  padding: 11px 20px;
  background: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  white-space: nowrap;
  font-size: 15px;
  color: #495057;
  transition: all 0.2s ease;
}

/* 热门问题按钮 hover 效果优化，增强交互感知 */
.question-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  background: #fafbff;
  color: #6b63ff;
}

/* 补充模式按钮图标样式（避免图标缺失） */
.icon-speed::before {
  content: "🚀";
  margin-right: 4px;
}
.icon-explore::before {
  content: "🔍";
  margin-right: 4px;
}
</style>