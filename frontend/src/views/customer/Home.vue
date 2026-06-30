<template>
  <div class="shop-container">
    <!-- Banner -->
    <div class="banner">
      <div class="banner-content">
        <h1>优选超市，新鲜每一天</h1>
        <p>品质生活，从这里开始</p>
      </div>
    </div>

    <!-- 分类导航 -->
    <div class="section">
      <h2 class="section-title">商品分类</h2>
      <el-row :gutter="16">
        <el-col :span="4" v-for="cat in categories" :key="cat.id">
          <el-card shadow="hover" class="cat-card" @click="router.push('/shop/products?cat=' + cat.id)">
            <div style="text-align:center;padding:12px">
              <el-icon :size="36" color="#409eff"><Goods /></el-icon>
              <p style="margin-top:8px;font-size:14px">{{ cat.name }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 热销商品 -->
    <div class="section">
      <h2 class="section-title">热销推荐</h2>
      <el-row :gutter="16">
        <el-col :span="6" v-for="p in products" :key="p.id" style="margin-bottom:16px">
          <el-card shadow="hover" class="product-card" @click="router.push('/shop/product/' + p.id)">
            <div style="height:180px;background:#f5f5f5;display:flex;align-items:center;justify-content:center;color:#909399">
              <el-icon :size="48"><Picture /></el-icon>
            </div>
            <div style="padding:8px 0">
              <p style="font-size:14px;font-weight:bold;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ p.name }}</p>
              <p style="color:#f56c6c;font-size:18px;font-weight:bold;margin-top:4px">&yen;{{ p.selling_price }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { categoryApi, productApi } from '@/api'

const router = useRouter()
const categories = ref([])
const products = ref([])

onMounted(async () => {
  const [catRes, prodRes] = await Promise.all([
    categoryApi.list(),
    productApi.list({ status: '上架', page: 1, page_size: 8 })
  ])
  categories.value = (catRes.data || []).slice(0, 6)
  products.value = prodRes.data.data || []
})
</script>

<style scoped>
.shop-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.banner {
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  border-radius: 12px; padding: 60px 40px; color: #fff; margin-bottom: 30px;
}
.banner h1 { font-size: 36px; margin-bottom: 12px; }
.banner p { font-size: 18px; opacity: 0.9; }
.section { margin-bottom: 30px; }
.section-title { font-size: 22px; margin-bottom: 16px; color: #303133; }
.cat-card { cursor: pointer; transition: transform 0.2s; }
.cat-card:hover { transform: translateY(-4px); }
.product-card { cursor: pointer; transition: transform 0.2s; }
.product-card:hover { transform: translateY(-4px); }
</style>
