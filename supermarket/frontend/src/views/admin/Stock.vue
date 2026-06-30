<template>
  <div class="page-container">
    <div class="page-header"><h2>库存管理</h2></div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="商品名称" clearable style="width:180px" />
      <el-switch v-model="alertOnly" active-text="仅显示预警" style="margin-left:8px" />
      <el-button type="primary" @click="search">搜索</el-button>
      <el-button @click="reset">重置</el-button>
      <div style="margin-left:auto;display:flex;gap:8px">
        <el-button type="success" @click="showInbound = true">入库</el-button>
        <el-button type="warning" @click="showOutbound = true">出库</el-button>
        <el-button @click="handleStockCheck">创建盘点</el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table :data="stockList" stripe v-loading="loading" border>
        <el-table-column prop="name" label="商品名称" min-width="140" />
        <el-table-column prop="barcode" label="条形码" width="120" />
        <el-table-column prop="stock_quantity" label="当前库存" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_alert ? (row.status === '库存不足' ? 'danger' : 'warning') : 'success'" size="default">
              {{ row.stock_quantity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="stock_lower_limit" label="下限" width="70" />
        <el-table-column prop="stock_upper_limit" label="上限" width="70" />
        <el-table-column prop="unit" label="单位" width="60" />
        <el-table-column prop="selling_price" label="售价" width="80">
          <template #default="{ row }">&yen;{{ row.selling_price }}</template>
        </el-table-column>
        <el-table-column prop="status" label="预警状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_alert ? 'danger' : 'success'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev,pager,next" @current-change="loadStock" />
      </div>
    </div>

    <!-- 入库对话框 -->
    <el-dialog v-model="showInbound" title="入库" width="450px">
      <el-form :model="inboundForm" label-width="100px">
        <el-form-item label="商品" required>
          <el-select v-model="inboundForm.product_id" filterable placeholder="搜索商品" style="width:100%">
            <el-option v-for="p in allProducts" :key="p.id" :label="p.name + ' (' + p.barcode + ')'" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="入库数量" required><el-input-number v-model="inboundForm.change_quantity" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="类型"><el-input v-model="inboundForm.change_type" placeholder="采购入库" /></el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="inboundForm.supplier_id" clearable placeholder="选择供应商" style="width:100%">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="inboundForm.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInbound = false">取消</el-button>
        <el-button type="primary" @click="handleInbound" :loading="saving">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 出库对话框 -->
    <el-dialog v-model="showOutbound" title="出库" width="450px">
      <el-form :model="outboundForm" label-width="100px">
        <el-form-item label="商品" required>
          <el-select v-model="outboundForm.product_id" filterable placeholder="搜索商品" style="width:100%">
            <el-option v-for="p in allProducts" :key="p.id" :label="p.name + ' (' + p.barcode + ')'" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="出库数量" required><el-input-number v-model="outboundForm.change_quantity" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="类型"><el-input v-model="outboundForm.change_type" placeholder="报损/调拨" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="outboundForm.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showOutbound = false">取消</el-button>
        <el-button type="primary" @click="handleOutbound" :loading="saving">确认出库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { stockApi, productApi, supplierApi } from '@/api'

const stockList = ref([])
const allProducts = ref([])
const suppliers = ref([])
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const alertOnly = ref(false)
const page = ref(1)
const total = ref(0)
const showInbound = ref(false)
const showOutbound = ref(false)

const inboundForm = ref({ product_id: null, change_quantity: 1, change_type: '采购入库', supplier_id: null, remark: '' })
const outboundForm = ref({ product_id: null, change_quantity: 1, change_type: '报损', remark: '' })

const loadStock = async () => {
  loading.value = true
  try {
    const res = await stockApi.list({ keyword: keyword.value, alert_only: alertOnly.value, page: page.value, page_size: 20 })
    stockList.value = res.data.data || []
    total.value = res.data.total || 0
  } finally { loading.value = false }
}

const search = () => { page.value = 1; loadStock() }
const reset = () => { keyword.value = ''; alertOnly.value = false; page.value = 1; loadStock() }

const handleInbound = async () => {
  if (!inboundForm.value.product_id) { ElMessage.warning('请选择商品'); return }
  if (!inboundForm.value.change_quantity || inboundForm.value.change_quantity <= 0) { ElMessage.warning('请输入有效数量'); return }
  saving.value = true
  try {
    await stockApi.inbound(inboundForm.value)
    ElMessage.success('入库成功')
    showInbound.value = false
    inboundForm.value = { product_id: null, change_quantity: 1, change_type: '采购入库', supplier_id: null, remark: '' }
    loadStock()
  } finally { saving.value = false }
}

const handleOutbound = async () => {
  if (!outboundForm.value.product_id) { ElMessage.warning('请选择商品'); return }
  saving.value = true
  try {
    await stockApi.outbound(outboundForm.value)
    ElMessage.success('出库成功')
    showOutbound.value = false
    outboundForm.value = { product_id: null, change_quantity: 1, change_type: '报损', remark: '' }
    loadStock()
  } finally { saving.value = false }
}

const handleStockCheck = async () => {
  try {
    await ElMessageBox.confirm('创建盘点单将记录所有商品的当前库存，确认创建？', '提示')
    const res = await stockApi.createCheck()
    ElMessage.success('盘点单已创建，编号: ' + res.data.check_no)
  } catch {}
}

onMounted(async () => {
  const [pRes, sRes] = await Promise.all([
    productApi.list({ page: 1, page_size: 999 }),
    supplierApi.list({ page: 1, page_size: 999 })
  ])
  allProducts.value = pRes.data.data || []
  suppliers.value = sRes.data.data || []
  loadStock()
})
</script>
