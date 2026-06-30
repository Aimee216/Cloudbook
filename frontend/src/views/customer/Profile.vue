<template>
  <div class="shop-container">
    <h2 style="margin-bottom:20px">个人中心</h2>
    <div v-if="!isLoggedIn" style="text-align:center;padding:40px">
      <p style="color:#909399">请先登录</p>
      <el-button type="primary" style="margin-top:12px" @click="router.push('/shop/login')">去登录</el-button>
    </div>
    <div v-else>
      <el-card>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ info.name || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ info.phone }}</el-descriptions-item>
          <el-descriptions-item label="会员等级">
            <el-tag :type="levelType(info.member_level)" size="small">{{ info.member_level }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="积分">{{ info.points }}</el-descriptions-item>
          <el-descriptions-item label="累计消费">&yen;{{ info.total_consumption || 0 }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ info.register_time }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { customerApi } from '@/api'

const router = useRouter()
const isLoggedIn = ref(!!localStorage.getItem('customer_info'))
const info = ref({})

const levelType = (l) => {
  if (l === '金卡会员') return 'warning'
  if (l === '银卡会员') return 'primary'
  return 'info'
}

onMounted(async () => {
  const stored = JSON.parse(localStorage.getItem('customer_info'))
  if (stored) {
    try {
      const res = await customerApi.get(stored.id)
      info.value = res.data
    } catch {
      info.value = stored
    }
  }
})
</script>

<style scoped>
.shop-container { max-width: 800px; margin: 0 auto; padding: 20px; }
</style>
