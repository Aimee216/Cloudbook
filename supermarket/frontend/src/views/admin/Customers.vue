<template>
  <div class="page-container">
    <div class="page-header"><h2>顾客管理</h2></div>
    <div class="search-bar">
      <el-input v-model="keyword" placeholder="姓名/手机号" clearable style="width:200px" />
      <el-select v-model="level" placeholder="会员等级" clearable style="width:140px">
        <el-option label="普通会员" value="普通会员" />
        <el-option label="银卡会员" value="银卡会员" />
        <el-option label="金卡会员" value="金卡会员" />
      </el-select>
      <el-button type="primary" @click="search">搜索</el-button>
    </div>
    <div class="table-container">
      <el-table :data="customers" stripe v-loading="loading" border>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="total_consumption" label="累计消费" width="120">
          <template #default="{ row }">&yen;{{ row.total_consumption }}</template>
        </el-table-column>
        <el-table-column prop="member_level" label="会员等级" width="100">
          <template #default="{ row }">
            <el-tag :type="levelType(row.member_level)" size="small">{{ row.member_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="points" label="积分" width="80" />
        <el-table-column prop="register_time" label="注册时间" width="160" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev,pager,next" @current-change="loadData" />
      </div>
    </div>

    <el-dialog v-model="showDetail" :title="'顾客详情 - ' + detail.name" width="800px">
      <el-descriptions :column="2" border v-if="detail.id">
        <el-descriptions-item label="姓名">{{ detail.name }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ detail.phone }}</el-descriptions-item>
        <el-descriptions-item label="会员等级">{{ detail.member_level }}</el-descriptions-item>
        <el-descriptions-item label="积分">{{ detail.points }}</el-descriptions-item>
        <el-descriptions-item label="累计消费">&yen;{{ detail.total_consumption }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ detail.register_time }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail.orders || []" stripe style="margin-top:16px" max-height="300">
        <el-table-column prop="order_no" label="订单号" width="180" />
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
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { customerApi } from '@/api'

const customers = ref([])
const loading = ref(false)
const keyword = ref('')
const level = ref('')
const page = ref(1)
const total = ref(0)
const showDetail = ref(false)
const detail = ref({})

const levelType = (l) => {
  if (l === '金卡会员') return 'warning'
  if (l === '银卡会员') return 'primary'
  return 'info'
}
const statusType = (s) => {
  const map = { '待支付': 'warning', '待发货': 'info', '已发货': 'primary', '已完成': 'success', '已取消': 'danger' }
  return map[s] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await customerApi.list({ keyword: keyword.value, member_level: level.value, page: page.value, page_size: 20 })
    customers.value = res.data.data || []
    total.value = res.data.total || 0
  } finally { loading.value = false }
}

const search = () => { page.value = 1; loadData() }

const handleDetail = async (row) => {
  const res = await customerApi.get(row.id)
  detail.value = res.data
  showDetail.value = true
}

loadData()
</script>
