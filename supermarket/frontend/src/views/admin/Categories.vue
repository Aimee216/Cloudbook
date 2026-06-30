<template>
  <div class="page-container">
    <div class="page-header">
      <h2>商品分类</h2>
      <el-button type="primary" @click="showDialog = true; isEdit = false">新增分类</el-button>
    </div>
    <div class="table-container">
      <el-table :data="flatCategories" stripe v-loading="loading" border row-key="id">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="分类名称" min-width="200" />
        <el-table-column prop="parent_id" label="父级ID" width="80" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑分类' : '新增分类'" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="分类名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="父级分类">
          <el-tree-select v-model="form.parent_id" :data="categories" :props="{ label: 'name', value: 'id' }" clearable placeholder="顶级分类" style="width:100%" />
        </el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { categoryApi } from '@/api'

const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const form = ref({ name: '', parent_id: null, sort_order: 0 })

const flatCategories = computed(() => {
  const flatten = (list, level = 0) => {
    let arr = []
    for (const item of list) {
      arr.push({ ...item, _level: level })
      if (item.children && item.children.length) arr = arr.concat(flatten(item.children, level + 1))
    }
    return arr
  }
  return flatten(categories.value)
})

const loadCategories = async () => {
  loading.value = true
  try {
    const res = await categoryApi.list()
    categories.value = res.data || []
  } finally { loading.value = false }
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { name: row.name, parent_id: row.parent_id, sort_order: row.sort_order }
  form.value._id = row.id
  showDialog.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除分类"${row.name}"？`, '提示')
    await categoryApi.delete(row.id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch {}
}

const handleSave = async () => {
  saving.value = true
  try {
    if (isEdit.value) {
      await categoryApi.update(form.value._id, form.value)
      ElMessage.success('更新成功')
    } else {
      await categoryApi.create(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    loadCategories()
  } finally { saving.value = false }
}

onMounted(loadCategories)
</script>
