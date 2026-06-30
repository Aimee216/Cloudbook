<template>
  <div class="page-container">
    <div class="page-header"><h2>商品管理</h2></div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="商品名称" clearable style="width:180px" />
      <el-select v-model="categoryId" placeholder="分类" clearable style="width:140px">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-select v-model="status" placeholder="状态" clearable style="width:120px">
        <el-option label="上架" value="上架" />
        <el-option label="下架" value="下架" />
      </el-select>
      <el-button type="primary" @click="search">搜索</el-button>
      <el-button @click="reset">重置</el-button>
      <div style="margin-left:auto;display:flex;gap:8px">
        <el-button type="primary" @click="showDialog = true; isEdit = false">新增商品</el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table :data="products" stripe v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="商品名称" min-width="140" />
        <el-table-column prop="barcode" label="条形码" width="120" />
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="selling_price" label="售价" width="90">
          <template #default="{ row }">&yen;{{ row.selling_price }}</template>
        </el-table-column>
        <el-table-column prop="purchase_price" label="进价" width="90">
          <template #default="{ row }">&yen;{{ row.purchase_price }}</template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存" width="80" />
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status === '上架' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev,pager,next" @current-change="loadProducts" />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="showDialog" :title="isEdit ? '编辑商品' : '新增商品'" width="650px">
      <el-form :model="form" label-width="100px" ref="formRef" :rules="rules">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name"><el-input v-model="form.name" /></el-form-item>
            <el-form-item label="条形码"><el-input v-model="form.barcode" /></el-form-item>
            <el-form-item label="商品分类">
              <el-tree-select v-model="form.category_id" :data="categories" :props="{ label: 'name', value: 'id' }" clearable placeholder="选择分类" style="width:100%" />
            </el-form-item>
            <el-form-item label="规格单位"><el-input v-model="form.unit" /></el-form-item>
            <el-form-item label="进价"><el-input-number v-model="form.purchase_price" :precision="2" :min="0" style="width:100%" /></el-form-item>
            <el-form-item label="售价" prop="selling_price"><el-input-number v-model="form.selling_price" :precision="2" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-select v-model="form.supplier_id" clearable placeholder="选择供应商" style="width:100%">
                <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="库存下限"><el-input-number v-model="form.stock_lower_limit" :min="0" style="width:100%" /></el-form-item>
            <el-form-item label="库存上限"><el-input-number v-model="form.stock_upper_limit" :min="0" style="width:100%" /></el-form-item>
            <el-form-item label="商品状态">
              <el-radio-group v-model="form.status">
                <el-radio value="上架">上架</el-radio>
                <el-radio value="下架">下架</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="商品描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
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
import { productApi, categoryApi, supplierApi } from '@/api'

const products = ref([])
const categories = ref([])
const suppliers = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const keyword = ref('')
const categoryId = ref(null)
const status = ref('')
const page = ref(1)
const total = ref(0)

const form = ref({
  name: '', barcode: '', category_id: null, unit: '个',
  purchase_price: 0, selling_price: 0,
  stock_lower_limit: 0, stock_upper_limit: 99999,
  supplier_id: null, status: '上架', description: ''
})

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  selling_price: [{ required: true, message: '请输入售价', trigger: 'blur' }]
}

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await productApi.list({ keyword: keyword.value, category_id: categoryId.value, status: status.value, page: page.value, page_size: 20 })
    products.value = res.data.data || []
    total.value = res.data.total || 0
  } finally { loading.value = false }
}

const search = () => { page.value = 1; loadProducts() }
const reset = () => { keyword.value = ''; categoryId.value = null; status.value = ''; page.value = 1; loadProducts() }

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row, category_id: row.category_id || null, supplier_id: row.supplier_id || null }
  showDialog.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除商品"${row.name}"？`, '提示')
    await productApi.delete(row.id)
    ElMessage.success('删除成功')
    loadProducts()
  } catch {}
}

const handleSave = async () => {
  saving.value = true
  try {
    if (isEdit.value) {
      await productApi.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await productApi.create(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    loadProducts()
  } finally { saving.value = false }
}

onMounted(async () => {
  const [catRes, supRes] = await Promise.all([categoryApi.list(), supplierApi.list({ page: 1, page_size: 999 })])
  categories.value = catRes.data || []
  suppliers.value = supRes.data.data || []
  loadProducts()
})
</script>
