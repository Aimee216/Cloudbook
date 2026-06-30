<template>
  <div>
    <el-header class="shop-header">
      <div class="header-inner">
        <div class="logo" @click="router.push('/shop')">
          <el-icon :size="28" color="#409eff"><ShoppingCart /></el-icon>
          <span style="font-size:20px;font-weight:bold;margin-left:8px">优选超市</span>
        </div>
        <div class="nav">
          <router-link to="/shop" class="nav-link">首页</router-link>
          <router-link to="/shop/products" class="nav-link">全部商品</router-link>
          <router-link to="/shop/cart" class="nav-link">
            购物车
            <el-badge :value="cartCount" :hidden="!cartCount" />
          </router-link>
          <router-link to="/shop/orders" class="nav-link">我的订单</router-link>
          <router-link to="/shop/profile" class="nav-link">个人中心</router-link>
          <el-button v-if="!isLoggedIn" type="primary" size="small" @click="router.push('/shop/login')">登录</el-button>
          <el-button v-else type="default" size="small" @click="handleLogout">退出</el-button>
        </div>
      </div>
    </el-header>
    <el-main class="shop-main">
      <router-view />
    </el-main>
    <el-footer class="shop-footer">
      <p>&copy; 2024 优选超市 - 线上商城</p>
    </el-footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const isLoggedIn = ref(!!localStorage.getItem('customer_token'))
const cartItems = ref(JSON.parse(localStorage.getItem('cart') || '[]'))
const cartCount = computed(() => cartItems.value.reduce((s, i) => s + i.quantity, 0))

const handleLogout = () => {
  localStorage.removeItem('customer_token')
  localStorage.removeItem('customer_info')
  isLoggedIn.value = false
  ElMessage.success('已退出')
  router.push('/shop')
}

onMounted(() => {
  window.addEventListener('storage', () => {
    cartItems.value = JSON.parse(localStorage.getItem('cart') || '[]')
    isLoggedIn.value = !!localStorage.getItem('customer_token')
  })
})
</script>

<style scoped>
.shop-header {
  background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  position: fixed; top: 0; left: 0; right: 0; z-index: 100; height: 60px !important;
}
.header-inner {
  max-width: 1200px; margin: 0 auto; display: flex;
  align-items: center; justify-content: space-between; height: 60px;
}
.logo { display: flex; align-items: center; cursor: pointer; }
.nav { display: flex; align-items: center; gap: 20px; }
.nav-link {
  color: #606266; font-size: 14px; transition: color 0.2s;
  display: flex; align-items: center; gap: 4px;
}
.nav-link:hover, .nav-link.router-link-active { color: #409eff; }
.shop-main { margin-top: 60px; min-height: calc(100vh - 120px); background: #f5f7fa; }
.shop-footer {
  text-align: center; color: #909399; font-size: 13px;
  background: #fff; height: 60px !important; line-height: 60px;
}
</style>
