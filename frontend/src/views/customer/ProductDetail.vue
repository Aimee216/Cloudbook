<template>
  <div class="shop-container">
    <el-card v-if="product" class="detail-card">
      <el-row :gutter="30">
        <el-col :span="10">
          <div class="product-image">
            <el-icon :size="80" color="#c0c4cc"><Picture /></el-icon>
          </div>
        </el-col>
        <el-col :span="14">
          <h1 style="font-size:24px;margin-bottom:12px">{{ product.name }}</h1>
          <div style="background:#fdf6ec;padding:16px;border-radius:8px;margin-bottom:16px">
            <span style="color:#909399;font-size:14px">价格</span>
            <span style="color:#f56c6c;font-size:28px;font-weight:bold;margin-left:8px">&yen;{{ product.selling_price }}</span>
          </div>
          <p style="color:#606266;margin-bottom:8px"><strong>条形码：</strong>{{ product.barcode || '无' }}</p>
          <p style="color:#606266;margin-bottom:8px"><strong>分类：</strong>{{ product.category_name || '未分类' }}</p>
          <p style="color:#606266;margin-bottom:8px"><strong>库存：</strong>
            <el-tag :type="product.stock_quantity > 0 ? 'success' : 'danger'" size="small">
              {{ product.stock_quantity > 0 ? '有货 (' + product.stock_quantity + ')' : '缺货' }}
            </el-tag>
          </p>
          <p style="color:#606266;margin-bottom:16px"><strong>描述：</strong>{{ product.description || '暂无描述' }}</p>
          <div style="display:flex;align-items:center;gap:16px;margin-top:20px">
            <el-input-number v-model="quantity" :min="1" :max="product.stock_quantity" />
            <el-button type="primary" size="large" @click="addToCart" :disabled="product.stock_quantity <= 0">
              加入购物车
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { productApi } from '@/api'

const route = useRoute()
const product = ref(null)
const quantity = ref(1)

const addToCart = () => {
  const cart = JSON.parse(localStorage.getItem('cart') || '[]')
  const idx = cart.findIndex(i => i.product_id === product.value.id)
  if (idx >= 0) {
    cart[idx].quantity += quantity.value
  } else {
    cart.push({
      product_id: product.value.id,
      name: product.value.name,
      price: product.value.selling_price,
      quantity: quantity.value,
      image: product.value.image
    })
  }
  localStorage.setItem('cart', JSON.stringify(cart))
  window.dispatchEvent(new Event('storage'))
  ElMessage.success('已加入购物车')
}

onMounted(async () => {
  const res = await productApi.get(route.params.id)
  product.value = res.data
})
</script>

<style scoped>
.shop-container { max-width: 1000px; margin: 0 auto; padding: 20px; }
.product-image {
  height: 350px; background: #f5f5f5; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
}
</style>
