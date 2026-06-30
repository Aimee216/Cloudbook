<template>
  <div class="page-container">
    <div class="page-header">
      <h2>员工管理</h2>
      <el-button type="primary" @click="showDialog = true; isEdit = false">新增员工</el-button>
    </div>
    <div class="search-bar">
      <el-input v-model="keyword" placeholder="姓名/手机号" clearable style="width:200px" />
      <el-button type="primary" @click="search">搜索</el-button>
    </div>
    <div class="table-container">
      <el-table :data="employees" stripe v-loading="loading" border>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="position" label="职位" width="120" />
        <el-table-column prop="hire_date" label="入职日期" width="120" />
        <el-table-column prop="salary" label="薪资" width="100">
          <template #default="{ row }">&yen;{{ row.salary }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === '在职' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="系统账号" width="100" />
        <el-table-column prop="role" label="角色" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev,pager,next" @current-change="loadData" />
      </div>
    </div>

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑员工' : '新增员工'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" required><el-input v-model="form.name" /></el-form-item>
            <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
            <el-form-item label="职位"><el-input v-model="form.position" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-radio-group v-model="form.gender">
                <el-radio value="男">男</el-radio>
                <el-radio value="女">女</el-radio>
                <el-radio value="未知">未知</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="入职日期"><el-date-picker v-model="form.hire_date" type="date" style="width:100%" /></el-form-item>
            <el-form-item label="薪资"><el-input-number v-model="form.salary" :precision="2" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { employeeApi } from '@/api'

const employees = ref([])
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const page = ref(1)
const total = ref(0)
const showDialog = ref(false)
const isEdit = ref(false)
const form = ref({ name: '', phone: '', position: '', gender: '未知', hire_date: null, salary: 0 })

const loadData = async () => {
  loading.value = true
  try {
    const res = await employeeApi.list({ keyword: keyword.value, page: page.value, page_size: 20 })
    employees.value = res.data.data || []
    total.value = res.data.total || 0
  } finally { loading.value = false }
}

const search = () => { page.value = 1; loadData() }

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row, hire_date: row.hire_date || null }
  showDialog.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除员工"${row.name}"？`, '提示')
    await employeeApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

const handleSave = async () => {
  saving.value = true
  try {
    if (isEdit.value) {
      await employeeApi.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await employeeApi.create(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    loadData()
  } finally { saving.value = false }
}

onMounted(loadData)
</script>
