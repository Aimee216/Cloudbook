<template>
  <div class="page-container">
    <div class="page-header"><h2>操作日志</h2></div>
    <div class="table-container">
      <el-table :data="logs" stripe v-loading="loading" border>
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column prop="username" label="操作人" width="100" />
        <el-table-column prop="action" label="操作" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="对象类型" width="100" />
        <el-table-column prop="detail" label="详情" min-width="300" />
      </el-table>
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="50" :total="total" layout="prev,pager,next" @current-change="loadLogs" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { employeeApi } from '@/api'

const logs = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

const loadLogs = async () => {
  loading.value = true
  try {
    const res = await employeeApi.logs({ page: page.value, page_size: 50 })
    logs.value = res.data.data || []
    total.value = res.data.total || 0
  } finally { loading.value = false }
}

onMounted(loadLogs)
</script>
