<template>
  <div class="page-container">
    <div class="page-header"><h2>数据报表</h2></div>

    <el-tabs v-model="activeTab">
      <!-- 销售报表 -->
      <el-tab-pane label="销售报表" name="sales">
        <el-card>
          <div style="margin-bottom:16px;display:flex;align-items:center;gap:12px">
            <el-radio-group v-model="salesPeriod">
              <el-radio-button value="day">日</el-radio-button>
              <el-radio-button value="week">周</el-radio-button>
              <el-radio-button value="month">月</el-radio-button>
              <el-radio-button value="year">年</el-radio-button>
            </el-radio-group>
            <el-button type="primary" @click="loadSales">查询</el-button>
          </div>

          <el-descriptions :column="3" border style="margin-bottom:16px">
            <el-descriptions-item label="总销售额">&yen;{{ salesSummary.total_sales }}</el-descriptions-item>
            <el-descriptions-item label="总订单数">{{ salesSummary.total_orders }}</el-descriptions-item>
            <el-descriptions-item label="客单价">&yen;{{ salesSummary.avg_order_amount }}</el-descriptions-item>
          </el-descriptions>

          <el-table :data="salesData" stripe border max-height="400">
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="order_count" label="订单数" width="80" />
            <el-table-column prop="total_sales" label="销售额" width="120">
              <template #default="{ row }">&yen;{{ row.total_sales }}</template>
            </el-table-column>
            <el-table-column prop="avg_order_amount" label="客单价" width="120">
              <template #default="{ row }">&yen;{{ row.avg_order_amount }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 商品销售排行 -->
      <el-tab-pane label="商品销售排行" name="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>热销商品 Top {{ topN }}</template>
              <el-table :data="topProducts" stripe border max-height="500">
                <el-table-column type="index" label="排名" width="60" />
                <el-table-column prop="product_name" label="商品名称" min-width="160" />
                <el-table-column prop="total_quantity" label="销量" width="80" />
                <el-table-column prop="total_amount" label="金额" width="120">
                  <template #default="{ row }">&yen;{{ row.total_amount }}</template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>滞销商品</template>
              <el-table :data="slowMovingProducts" stripe border max-height="500">
                <el-table-column prop="name" label="商品名称" min-width="160" />
                <el-table-column prop="stock_quantity" label="库存" width="80" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 库存分析 -->
      <el-tab-pane label="库存分析" name="inventory">
        <el-row :gutter="20">
          <el-col :span="6" v-for="item in inventoryStats" :key="item.label">
            <el-card shadow="hover" style="margin-bottom:16px">
              <div style="text-align:center">
                <p style="font-size:28px;font-weight:bold;color:item.color">{{ item.value }}</p>
                <p style="color:#909399;margin-top:8px">{{ item.label }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-card>
          <template #header>周转率</template>
          <p>库存周转率: <strong>{{ inventoryAnalysis?.turnover_rate }}</strong></p>
          <p>滞销库存占比: <strong>{{ inventoryAnalysis?.low_stock_ratio }}%</strong></p>
        </el-card>
      </el-tab-pane>

      <!-- 财务报表 -->
      <el-tab-pane label="财务报表" name="finance">
        <el-card>
          <div style="margin-bottom:16px;display:flex;gap:12px">
            <el-date-picker v-model="financeStart" type="date" placeholder="开始日期" />
            <el-date-picker v-model="financeEnd" type="date" placeholder="结束日期" />
            <el-button type="primary" @click="loadFinance">查询</el-button>
          </div>
          <el-descriptions :column="2" border v-if="financeData">
            <el-descriptions-item label="销售收入">&yen;{{ financeData.sales_revenue }}</el-descriptions-item>
            <el-descriptions-item label="销售成本">&yen;{{ financeData.sales_cost }}</el-descriptions-item>
            <el-descriptions-item label="毛利润">&yen;{{ financeData.gross_profit }}</el-descriptions-item>
            <el-descriptions-item label="毛利率">{{ financeData.gross_margin }}%</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { statsApi } from '@/api'

const activeTab = ref('sales')
const salesPeriod = ref('month')
const salesData = ref([])
const salesSummary = ref({ total_sales: 0, total_orders: 0, avg_order_amount: 0 })
const topProducts = ref([])
const slowMovingProducts = ref([])
const topN = ref(10)
const inventoryStats = ref([])
const inventoryAnalysis = ref(null)
const financeStart = ref(null)
const financeEnd = ref(null)
const financeData = ref(null)

const loadSales = async () => {
  const res = await statsApi.sales({ period: salesPeriod.value })
  salesData.value = res.data.details || []
  salesSummary.value = res.data.summary || { total_sales: 0, total_orders: 0, avg_order_amount: 0 }
}

const loadTopProducts = async () => {
  const res = await statsApi.topProducts({ top_n: topN.value })
  topProducts.value = res.data.top_products || []
  slowMovingProducts.value = res.data.slow_moving_products || []
}

const loadInventory = async () => {
  const res = await statsApi.inventoryAnalysis()
  inventoryAnalysis.value = res.data
  inventoryStats.value = [
    { label: '商品总数', value: res.data.total_products, color: '#409eff' },
    { label: '库存不足', value: res.data.low_stock_count, color: '#f56c6c' },
    { label: '库存过多', value: res.data.over_stock_count, color: '#e6a23c' },
    { label: '库存正常', value: res.data.normal_stock_count, color: '#67c23a' }
  ]
}

const loadFinance = async () => {
  const params = {}
  if (financeStart.value) params.start_date = financeStart.value.toISOString().slice(0, 10)
  if (financeEnd.value) params.end_date = financeEnd.value.toISOString().slice(0, 10)
  const res = await statsApi.finance(params)
  financeData.value = res.data
}

onMounted(async () => {
  await Promise.all([loadSales(), loadTopProducts(), loadInventory(), loadFinance()])
})
</script>
