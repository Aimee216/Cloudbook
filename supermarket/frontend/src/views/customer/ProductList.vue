<template>
  <div class="shop-container">
    <div style="display:flex;gap:12px;margin-bottom:20px">
      <el-input v-model="keyword" placeholder="搜索商品" clearable style="width:300px" @keyup.enter="search" />
      <el-select v-model="categoryId" placeholder="分类" clearable style="width:140px">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-button type="primary" @click="search">搜索</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="6" v-for="p in products" :key="p.id" style="margin-bottom:16px">
        <el-card shadow="hover" class="product-card" @click="router.push('/shop/product/' + p.id)">
          <div style="height:180px;background:#f5f5f5;display:flex;align-items:center;justify-content:center">
            <el-icon :size="48" color="#c0c4cc"><Picture /></el-icon>
          </div>
          <div style="padding:8px 0">
            <p style="font-size:14px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ p.name }}</p>
            <p style="color:#909399;font-size:12px;margin-top:4px">库存: {{ p.stock_quantity }}</p>
            <p style="color:#f56c6c;font-size:18px;font-weight:bold;margin-top:4px">&yen;{{ p.selling_price }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div style="display:flex;justify-content:center;margin-top:20px">
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev,pager,next" @current-change="loadProducts" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi, categoryApi } from '@/api'

const route = useRoute()
const router = useRouter()
const products = ref([])
const categories = ref([])
const keyword = ref('')
const categoryId = ref(Number(route.query.cat) || null)
const page = ref(1)
const total = ref(0)

const loadProducts = async () => {
  const res = await productApi.list({
    keyword: keyword.value, category_id: categoryId.value,
    status: '上架', page: page.value, page_size: 20
  })
  products.value = res.data.data || []
  total.value = res.data.total || 0
}

const search = () => { page.value = 1; loadProducts() }

onMounted(async () => {
  const catRes = await categoryApi.list()
  categories.value = catRes.data || []
  loadProducts()
})
</script>

<style scoped>
.shop-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.product-card { cursor: pointer; transition: transform 0.2s; }
.product-card:hover { transform: translateY(-4px); }
</style>
