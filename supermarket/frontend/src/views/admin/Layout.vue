<template>
  <el-container style="height: 100vh">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo" @click="router.push('/admin/dashboard')">
        <el-icon :size="24"><ShoppingCart /></el-icon>
        <span v-show="!isCollapse">超市管理系统</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        background-color="#001529"
        text-color="rgba(255,255,255,0.7)"
        active-text-color="#fff"
        router
      >
        <el-menu-item index="/admin/dashboard"><el-icon><DataAnalysis /></el-icon><span>工作台</span></el-menu-item>
        <el-sub-menu index="product">
          <template #title><el-icon><Goods /></el-icon><span>商品管理</span></template>
          <el-menu-item index="/admin/categories">商品分类</el-menu-item>
          <el-menu-item index="/admin/products">商品列表</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="stock">
          <template #title><el-icon><Coin /></el-icon><span>库存管理</span></template>
          <el-menu-item index="/admin/stock">库存查询</el-menu-item>
          <el-menu-item index="/admin/stock-records">库存流水</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/admin/orders"><el-icon><List /></el-icon><span>订单管理</span></el-menu-item>
        <el-menu-item index="/admin/customers"><el-icon><User /></el-icon><span>顾客管理</span></el-menu-item>
        <el-menu-item index="/admin/suppliers"><el-icon><Truck /></el-icon><span>供应商管理</span></el-menu-item>
        <el-menu-item index="/admin/employees"><el-icon><UserFilled /></el-icon><span>员工管理</span></el-menu-item>
        <el-sub-menu index="report">
          <template #title><el-icon><TrendCharts /></el-icon><span>数据报表</span></template>
          <el-menu-item index="/admin/reports">报表中心</el-menu-item>
          <el-menu-item index="/admin/logs">操作日志</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon @click="isCollapse = !isCollapse" style="cursor:pointer;font-size:20px">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/" style="margin-left:16px">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title">{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span>{{ user.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)

const user = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('admin_user')) || { username: '管理员' }
  } catch { return { username: '管理员' } }
})

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确认退出登录？', '提示')
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
    router.push('/admin/login')
  } catch {}
}
</script>

<style scoped>
.sidebar { background: #001529; overflow-y: auto; transition: width 0.3s; }
.sidebar::-webkit-scrollbar { width: 4px; }
.logo {
  height: 60px; display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 16px; font-weight: bold; gap: 8px; cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.header {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border-bottom: 1px solid #e4e7ed; height: 60px; padding: 0 20px;
}
.header-left { display: flex; align-items: center; }
.header-right .user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.main-content { background: #f5f7fa; padding: 0; overflow-y: auto; }
</style>
