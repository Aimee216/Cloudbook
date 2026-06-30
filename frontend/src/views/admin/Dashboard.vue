<template>
  <div class="page-container">
    <div class="page-header"><h2>工作台</h2></div>

    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="6" v-for="card in statsCards" :key="card.label">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" :style="{ background: card.bg }">
              <el-icon :size="24" color="#fff">{{ card.icon }}</el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ card.value }}</p>
              <p class="stat-label">{{ card.label }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header><span>近期订单</span></template>
          <el-table :data="recentOrders" stripe v-loading="loading">
            <el-table-column prop="order_no" label="订单号" width="180" />
            <el-table-column prop="customer_name" label="顾客" />
            <el-table-column prop="total_amount" label="金额" width="100">
              <template #default="{ row }">&yen;{{ row.total_amount }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="order_time" label="时间" width="160" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header><span>库存预警</span></template>
          <div v-if="alerts.length === 0" style="text-align:center;color:#909399;padding:20px">暂无预警</div>
          <div v-for="a in alerts" :key="a.id" class="alert-item">
            <el-tag :type="a.is_low ? 'danger' : 'warning'" size="small" style="margin-right:8px">
              {{ a.is_low ? "偏低" : "偏高" }}
            </el-tag>
            <span>{{ a.name }}</span>
            <span style="margin-left:auto;color:#909399;font-size:12px">库存: {{ a.stock_quantity }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { orderApi, stockApi } from '@/api'

const loading = ref(false)
const recentOrders = ref([])
const alerts = ref([])

const statsCards = ref([
  { label: '今日订单', value: '-', icon: 'List', bg: '#409eff' },
  { label: '本月销售额', value: '-', icon: 'Money', bg: '#67c23a' },
  { label: '商品总数', value: '-', icon: 'Goods', bg: '#e6a23c' },
  { label: '预警商品', value: '-', icon: 'WarningFilled', bg: '#f56c6c' }
])

const statusType = (s) => {
  const map = { '待支付': 'warning', '待发货': 'info', '已发货': 'primary', '已完成': 'success', '已取消': 'danger' }
  return map[s] || 'info'
}

onMounted(async () => {
  try {
    loading.value = true
    const [orderRes, stockRes] = await Promise.all([
      orderApi.list({ page: 1, page_size: 10 }),
      stockApi.list({ alert_only: true, page: 1, page_size: 10 })
    ])
    recentOrders.value = orderRes.data.data || []
    alerts.value = (stockRes.data.data || []).filter(a => a.is_alert)

    // 获取统计数据
    const allStock = await stockApi.list({ page: 1, page_size: 1 })
    statsCards.value[0].value = orderRes.data.total || 0
    statsCards.value[2].value = allStock.data.total || 0
    statsCards.value[3].value = alerts.value.length
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stat-card { display: flex; align-items: center; gap: 16px; }
.stat-icon {
  width: 56px; height: 56px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
}
.stat-value { font-size: 24px; font-weight: bold; color: #303133; }
.stat-label { font-size: 14px; color: #909399; margin-top: 4px; }
.alert-item {
  display: flex; align-items: center; padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.alert-item:last-child { border-bottom: none; }
</style>
