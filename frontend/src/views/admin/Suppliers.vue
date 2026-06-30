<template>
  <div class="page-container">
    <div class="page-header">
      <h2>供应商管理</h2>
      <el-button type="primary" @click="showDialog = true; isEdit = false">新增供应商</el-button>
    </div>
    <div class="search-bar">
      <el-input v-model="keyword" placeholder="供应商名称/联系人" clearable style="width:200px" />
      <el-button type="primary" @click="search">搜索</el-button>
    </div>
    <div class="table-container">
      <el-table :data="suppliers" stripe v-loading="loading" border>
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="120" />
        <el-table-column prop="supply_category" label="供货品类" width="120" />
        <el-table-column prop="rating" label="评分" width="80">
          <template #default="{ row }"><el-rate v-model="row.rating" disabled /></template>
        </el-table-column>
        <el-table-column prop="product_count" label="商品数" width="70" />
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

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑供应商' : '新增供应商'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact_person" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="供货品类"><el-input v-model="form.supply_category" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
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
import { supplierApi } from '@/api'

const suppliers = ref([])
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const page = ref(1)
const total = ref(0)
const showDialog = ref(false)
const isEdit = ref(false)
const form = ref({ name: '', contact_person: '', phone: '', address: '', supply_category: '', remark: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await supplierApi.list({ keyword: keyword.value, page: page.value, page_size: 20 })
    suppliers.value = res.data.data || []
    total.value = res.data.total || 0
  } finally { loading.value = false }
}

const search = () => { page.value = 1; loadData() }

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row }
  showDialog.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除供应商"${row.name}"？`, '提示')
    await supplierApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

const handleSave = async () => {
  saving.value = true
  try {
    if (isEdit.value) {
      await supplierApi.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await supplierApi.create(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    loadData()
  } finally { saving.value = false }
}

onMounted(loadData)
</script>
