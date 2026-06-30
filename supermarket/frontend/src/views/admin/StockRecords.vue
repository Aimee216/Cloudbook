<template>
  <div class="page-container">
    <div class="page-header"><h2>库存流水</h2></div>
    <div class="search-bar">
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width:260px" />
      <el-select v-model="changeType" placeholder="变动类型" clearable style="width:140px">
        <el-option label="采购入库" value="采购入库" />
        <el-option label="销售出库" value="销售出库" />
        <el-option label="报损" value="报损" />
        <el-option label="调拨" value="调拨" />
        <el-option label="盘点" value="盘点" />
      </el-select>
      <el-button type="primary" @click="search">搜索</el-button>
    </div>
    <div class="table-container">
      <el-table :data="records" stripe v-loading="loading" border>
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column prop="product_name" label="商品" min-width="140" />
        <el-table-column prop="change_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.change_quantity > 0 ? 'success' : 'danger'" size="small">{{ row.change_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="change_quantity" label="变动数量" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.change_quantity > 0 ? '#67c23a' : '#f56c6c', fontWeight: 'bold' }">
              {{ row.change_quantity > 0 ? '+' : '' }}{{ row.change_quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="before_quantity" label="变动前" width="70" />
        <el-table-column prop="after_quantity" label="变动后" width="70" />
        <el-table-column prop="supplier_name" label="供应商" width="120" />
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="remark" label="备注" min-width="120" />
      </el-table>
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev,pager,next" @current-change="loadRecords" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { stockApi } from '@/api'

const records = ref([])
const loading = ref(false)
const dateRange = ref(null)
const changeType = ref('')
const page = ref(1)
const total = ref(0)

const loadRecords = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (changeType.value) params.change_type = changeType.value
    if (dateRange.value) {
      params.start_date = dateRange.value[0].toISOString().slice(0, 10)
      params.end_date = dateRange.value[1].toISOString().slice(0, 10)
    }
    const res = await stockApi.records(params)
    records.value = res.data.data || []
    total.value = res.data.total || 0
  } finally { loading.value = false }
}

const search = () => { page.value = 1; loadRecords() }

loadRecords()
</script>
