<template>
  <div class="shop-container">
    <h2 style="margin-bottom:20px">我的订单</h2>
    <div v-if="!isLoggedIn" style="text-align:center;padding:40px">
      <p style="color:#909399">请先登录查看订单</p>
      <el-button type="primary" style="margin-top:12px" @click="router.push('/shop/login')">去登录</el-button>
    </div>
    <div v-else>
      <el-table :data="orders" stripe v-loading="loading" empty-text="暂无订单">
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">&yen;{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_time" label="下单时间" width="160" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleCancel(row)" v-if="row.status === '待支付' || row.status === '待发货'">
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orderApi } from '@/api'

const router = useRouter()
const orders = ref([])
const loading = ref(false)
const isLoggedIn = ref(!!localStorage.getItem('customer_info'))

const statusType = (s) => {
  const map = { '待支付': 'warning', '待发货': 'info', '已发货': 'primary', '已完成': 'success', '已取消': 'danger' }
  return map[s] || 'info'
}

const loadOrders = async () => {
  const customer = JSON.parse(localStorage.getItem('customer_info'))
  if (!customer) return
  loading.value = true
  try {
    const res = await orderApi.list({ keyword: customer.phone, page: 1, page_size: 50 })
    orders.value = res.data.data || []
  } finally { loading.value = false }
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm('确认取消此订单？', '提示')
    await orderApi.updateStatus(row.id, '已取消')
    ElMessage.success('订单已取消')
    loadOrders()
  } catch {}
}

onMounted(loadOrders)
</script>

<style scoped>
.shop-container { max-width: 1000px; margin: 0 auto; padding: 20px; }
</style>
