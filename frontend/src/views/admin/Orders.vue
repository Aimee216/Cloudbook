<template>
  <div class="page-container">
    <div class="page-header"><h2>订单管理</h2></div>
    <div class="search-bar">
      <el-input v-model="keyword" placeholder="订单号/顾客" clearable style="width:200px" />
      <el-select v-model="orderStatus" placeholder="订单状态" clearable style="width:140px">
        <el-option label="待支付" value="待支付" />
        <el-option label="待发货" value="待发货" />
        <el-option label="已发货" value="已发货" />
        <el-option label="已完成" value="已完成" />
        <el-option label="已取消" value="已取消" />
      </el-select>
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" style="width:260px" />
      <el-button type="primary" @click="search">搜索</el-button>
      <el-button @click="reset">重置</el-button>
    </div>
    <div class="table-container">
      <el-table :data="orders" stripe v-loading="loading" border>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="customer_name" label="顾客" width="100" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">&yen;{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100" />
        <el-table-column prop="order_time" label="下单时间" width="160" />
        <el-table-column prop="detail_count" label="商品数" width="70" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push('/admin/order-detail/' + row.id)">详情</el-button>
            <el-button v-if="row.status === '待发货'" link type="success" @click="updateStatus(row, '已发货')">发货</el-button>
            <el-button v-if="row.status === '已发货'" link type="success" @click="updateStatus(row, '已完成')">完成</el-button>
            <el-button v-if="row.status === '待支付' || row.status === '待发货'" link type="danger" @click="updateStatus(row, '已取消')">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev,pager,next" @current-change="loadOrders" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orderApi } from '@/api'

const router = useRouter()
const orders = ref([])
const loading = ref(false)
const keyword = ref('')
const orderStatus = ref('')
const dateRange = ref(null)
const page = ref(1)
const total = ref(0)

const statusType = (s) => {
  const map = { '待支付': 'warning', '待发货': 'info', '已发货': 'primary', '已完成': 'success', '已取消': 'danger' }
  return map[s] || 'info'
}

const loadOrders = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (keyword.value) params.keyword = keyword.value
    if (orderStatus.value) params.status = orderStatus.value
    if (dateRange.value) {
      params.start_date = dateRange.value[0].toISOString().slice(0, 10)
      params.end_date = dateRange.value[1].toISOString().slice(0, 10)
    }
    const res = await orderApi.list(params)
    orders.value = res.data.data || []
    total.value = res.data.total || 0
  } finally { loading.value = false }
}

const search = () => { page.value = 1; loadOrders() }
const reset = () => { keyword.value = ''; orderStatus.value = ''; dateRange.value = null; page.value = 1; loadOrders() }

const updateStatus = async (row, status) => {
  try {
    await ElMessageBox.confirm(`确认将订单 ${row.order_no} 状态更新为"${status}"？`, '提示')
    await orderApi.updateStatus(row.id, status)
    ElMessage.success('状态已更新')
    loadOrders()
  } catch {}
}

loadOrders()
</script>
