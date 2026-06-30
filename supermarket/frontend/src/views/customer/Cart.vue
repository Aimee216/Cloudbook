<template>
  <div class="shop-container">
    <h2 style="margin-bottom:20px">购物车</h2>
    <el-card v-if="cart.length > 0">
      <el-table :data="cart" stripe>
        <el-table-column label="商品" min-width="250">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:12px">
              <el-icon :size="32" color="#c0c4cc"><Goods /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="单价" width="100">
          <template #default="{ row }">&yen;{{ row.price }}</template>
        </el-table-column>
        <el-table-column label="数量" width="160">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="1" size="small" @change="saveCart" />
          </template>
        </el-table-column>
        <el-table-column label="小计" width="120">
          <template #default="{ row }">&yen;{{ (row.price * row.quantity).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button link type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="text-align:right;margin-top:16px">
        <span style="font-size:16px;margin-right:16px">合计: <strong style="color:#f56c6c;font-size:22px">&yen;{{ total }}</strong></span>
        <el-button type="primary" size="large" @click="checkout">去结算</el-button>
      </div>
    </el-card>
    <el-card v-else style="text-align:center;padding:40px">
      <el-icon :size="48" color="#c0c4cc"><ShoppingCart /></el-icon>
      <p style="color:#909399;margin-top:12px">购物车是空的，快去逛逛吧~</p>
      <el-button type="primary" style="margin-top:16px" @click="router.push('/shop/products')">去购物</el-button>
    </el-card>

    <!-- 结算对话框 -->
    <el-dialog v-model="showCheckout" title="确认订单" width="550px">
      <el-form :model="orderForm" label-width="100px">
        <el-form-item label="收货人" required><el-input v-model="orderForm.receiver_name" /></el-form-item>
        <el-form-item label="联系电话" required><el-input v-model="orderForm.receiver_phone" /></el-form-item>
        <el-form-item label="收货地址" required><el-input v-model="orderForm.receiver_address" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="支付方式">
          <el-radio-group v-model="orderForm.payment_method">
            <el-radio value="模拟支付">模拟支付</el-radio>
            <el-radio value="微信支付">微信支付</el-radio>
            <el-radio value="支付宝">支付宝</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="订单备注"><el-input v-model="orderForm.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <div style="text-align:right;padding:12px 0">
        合计: <strong style="color:#f56c6c;font-size:20px">&yen;{{ total }}</strong>
      </div>
      <template #footer>
        <el-button @click="showCheckout = false">取消</el-button>
        <el-button type="primary" @click="submitOrder" :loading="submitting">提交订单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orderApi } from '@/api'

const router = useRouter()
const cart = ref(JSON.parse(localStorage.getItem('cart') || '[]'))
const showCheckout = ref(false)
const submitting = ref(false)

const total = computed(() => cart.value.reduce((s, i) => s + i.price * i.quantity, 0).toFixed(2))

const orderForm = ref({
  receiver_name: '', receiver_phone: '', receiver_address: '',
  payment_method: '模拟支付', remark: ''
})

const saveCart = () => {
  localStorage.setItem('cart', JSON.stringify(cart.value))
  window.dispatchEvent(new Event('storage'))
}

const removeItem = (row) => {
  cart.value = cart.value.filter(i => i.product_id !== row.product_id)
  saveCart()
}

const checkout = () => {
  const customer = JSON.parse(localStorage.getItem('customer_info'))
  if (!customer) {
    ElMessage.warning('请先登录')
    router.push('/shop/login')
    return
  }
  showCheckout.value = true
}

const submitOrder = async () => {
  const customer = JSON.parse(localStorage.getItem('customer_info'))
  if (!customer) { ElMessage.warning('请先登录'); return }
  if (!orderForm.value.receiver_name || !orderForm.value.receiver_phone || !orderForm.value.receiver_address) {
    ElMessage.warning('请填写收货信息'); return
  }
  submitting.value = true
  try {
    const details = cart.value.map(i => ({
      product_id: i.product_id,
      quantity: i.quantity,
      unit_price: i.price
    }))
    const res = await orderApi.create({
      customer_id: customer.id,
      ...orderForm.value,
      details
    })
    ElMessage.success('下单成功！订单号: ' + res.data.order_no)
    localStorage.removeItem('cart')
    cart.value = []
    window.dispatchEvent(new Event('storage'))
    showCheckout.value = false
    router.push('/shop/orders')
  } finally { submitting.value = false }
}
</script>

<style scoped>
.shop-container { max-width: 1000px; margin: 0 auto; padding: 20px; }
</style>
