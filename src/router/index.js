import Vue from 'vue'
import Router from 'vue-router'

// 1. 导入页面组件（请务必确认实际文件路径！此处按常规 src/views 目录示例）
// 若组件在 src/pages 或其他目录，需修改路径（如 @/pages/SearchPage）
import SearchPage from '@/components/SearchPage'       // 首页（搜索入口）
import SearchProcess from '@/components/SearchProcessPage.vue' // 极速模式进度页
import NewProgress from '@/components/ExploreProgress.vue'     // 探索模式进度页（new_progress）
import SearchResult from '@/components/SearchResultPage.vue'   // 搜索结果页（共用）



// 2. 解决Vue-Router 3.x重复导航报错问题（固定写法）
const originalPush = Router.prototype.push
Router.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err)
}

// 3. 安装路由插件
Vue.use(Router)

// 4. 路由配置（核心：每个路由对象必须包含 path、name、component，格式严格）
export default new Router({
  mode: 'hash', // 优先用hash模式（无需后端配置，避免刷新404；若需history模式需后端配合）
  base: process.env.BASE_URL,
  routes: [
    // 首页（默认路由）
    {
      path: '/', // 必传：路由路径，不能缺失
      name: 'SearchPage',
      component: SearchPage,
      meta: {
        title: '武汉大学 | AI 智能搜索' // 页面标题，用于全局设置浏览器标题
      }
    },
    // 极速模式进度页
    {
      path: '/search-process', // 必传：完整路径，无语法错误
      name: 'SearchProcess',
      component: SearchProcess,
      meta: {
        title: '极速搜索 - 处理中',
        requiresQuery: true // 标记需要携带question/mode参数
      },
      // 路由守卫：确保参数存在，防止非法访问
      beforeEnter: (to, from, next) => {
        if (to.query.question && to.query.mode === 'quick') {
          next() // 参数齐全，允许进入
        } else {
          next({ path: '/' }) // 参数缺失，跳回首页
        }
      }
    },
    // 探索模式进度页（new_progress）
    {
      path: '/new_progress', // 必传：路径与首页跳转目标一致
      name: 'NewProgress',
      component: NewProgress,
      meta: {
        title: '探索搜索 - 处理中',
        requiresQuery: true
      },
      // 路由守卫：仅允许探索模式进入
      beforeEnter: (to, from, next) => {
        if (to.query.question && to.query.mode === 'explore') {
          next()
        } else {
          next({ path: '/' })
        }
      }
    },
    // 搜索结果页（共用）
    {
      path: '/search-result', // 必传：结果页路径
      name: 'SearchResult',
      component: SearchResult,
      meta: {
        title: '搜索结果',
        requiresQuery: true
      },
      // 路由守卫：确保有结果数据
      beforeEnter: (to, from, next) => {
        // 检查URL参数或本地存储是否有结果数据
        const hasResult = to.query.searchResult || localStorage.getItem('exploreResult')
        if (hasResult && to.query.mode) {
          next()
        } else {
          next({ path: '/' })
        }
      }
    },
    
  ],
  // 路由切换时滚动到顶部（优化体验）
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { x: 0, y: 0 }
  }
})