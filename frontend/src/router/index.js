import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/admin/login'
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/Layout.vue'),
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: '工作台' } },
      { path: 'products', component: () => import('@/views/admin/Products.vue'), meta: { title: '商品管理' } },
      { path: 'categories', component: () => import('@/views/admin/Categories.vue'), meta: { title: '分类管理' } },
      { path: 'stock', component: () => import('@/views/admin/Stock.vue'), meta: { title: '库存管理' } },
      { path: 'stock-records', component: () => import('@/views/admin/StockRecords.vue'), meta: { title: '库存流水' } },
      { path: 'orders', component: () => import('@/views/admin/Orders.vue'), meta: { title: '订单管理' } },
      { path: 'order-detail/:id', component: () => import('@/views/admin/OrderDetail.vue'), meta: { title: '订单详情' } },
      { path: 'customers', component: () => import('@/views/admin/Customers.vue'), meta: { title: '顾客管理' } },
      { path: 'suppliers', component: () => import('@/views/admin/Suppliers.vue'), meta: { title: '供应商管理' } },
      { path: 'employees', component: () => import('@/views/admin/Employees.vue'), meta: { title: '员工管理' } },
      { path: 'reports', component: () => import('@/views/admin/Reports.vue'), meta: { title: '数据报表' } },
      { path: 'logs', component: () => import('@/views/admin/Logs.vue'), meta: { title: '操作日志' } }
    ]
  },
  {
    path: '/admin/login',
    component: () => import('@/views/admin/Login.vue')
  },
  {
    path: '/shop',
    component: () => import('@/views/customer/Layout.vue'),
    children: [
      { path: '', component: () => import('@/views/customer/Home.vue'), meta: { title: '商城首页' } },
      { path: 'products', component: () => import('@/views/customer/ProductList.vue'), meta: { title: '商品列表' } },
      { path: 'product/:id', component: () => import('@/views/customer/ProductDetail.vue'), meta: { title: '商品详情' } },
      { path: 'cart', component: () => import('@/views/customer/Cart.vue'), meta: { title: '购物车' } },
      { path: 'orders', component: () => import('@/views/customer/Orders.vue'), meta: { title: '我的订单' } },
      { path: 'profile', component: () => import('@/views/customer/Profile.vue'), meta: { title: '个人中心' } }
    ]
  },
  {
    path: '/shop/login',
    component: () => import('@/views/customer/Login.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  if (to.path.startsWith('/admin') && to.path !== '/admin/login') {
    if (!token) {
      next('/admin/login')
      return
    }
  }
  const title = to.meta.title
  document.title = title ? title + ' - 超市管理系统' : '超市管理系统'
  next()
})

export default router
