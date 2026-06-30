<template>
  <div class="page-container">
    <div class="page-header">
      <h2>订单详情</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>
    <el-card v-if="order" style="margin-bottom:20px">
      <template #header>基本信息</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ order.order_time }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(order.status)" size="small">{{ order.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="顾客">{{ order.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ order.customer_phone }}</el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ order.payment_method }}</el-descriptions-item>
        <el-descriptions-item label="收货人">{{ order.receiver_name }}</el-descriptions-item>
        <el-descriptions-item label="收货电话">{{ order.receiver_phone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="3">{{ order.receiver_address }}</el-descriptions-item>
        <el-descriptions-item label="订单备注" :span="3">{{ order.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card>
      <template #header>商品明细</template>
      <el-table :data="order.details" border stripe>
        <el-table-column prop="product_name" label="商品名称" min-width="200" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">&yen;{{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="subtotal" label="小计" width="120">
          <template #default="{ row }">&yen;{{ row.subtotal }}</template>
        </el-table-column>
      </el-table>
      <div style="text-align:right;margin-top:16px;font-size:18px;font-weight:bold">
        合计: &yen;{{ order.total_amount }}
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { orderApi } from '@/api'

const route = useRoute()
const router = useRouter()
const order = ref(null)

const statusType = (s) => {
  const map = { '待支付': 'warning', '待发货': 'info', '已发货': 'primary', '已完成': 'success', '已取消': 'danger' }
  return map[s] || 'info'
}

onMounted(async () => {
  const res = await orderApi.get(route.params.id)
  order.value = res.data
})
</script>
