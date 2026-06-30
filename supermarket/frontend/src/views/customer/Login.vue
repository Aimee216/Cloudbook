<template>
  <div class="shop-container" style="max-width:400px;margin:80px auto">
    <el-card>
      <h2 style="text-align:center;margin-bottom:20px">顾客登录</h2>
      <el-tabs v-model="tab">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" label-width="0">
            <el-form-item><el-input v-model="loginForm.phone" placeholder="手机号" prefix-icon="Iphone" /></el-form-item>
            <el-form-item><el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password /></el-form-item>
            <el-form-item><el-button type="primary" @click="handleLogin" :loading="loading" style="width:100%">登录</el-button></el-form-item>
          </el-form>
          <p style="text-align:center;color:#909399;font-size:13px">没有账号？<el-button link type="primary" @click="tab = 'register'">立即注册</el-button></p>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" label-width="0">
            <el-form-item><el-input v-model="registerForm.name" placeholder="昵称（可选）" prefix-icon="User" /></el-form-item>
            <el-form-item><el-input v-model="registerForm.phone" placeholder="手机号" prefix-icon="Iphone" /></el-form-item>
            <el-form-item><el-input v-model="registerForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password /></el-form-item>
            <el-form-item><el-button type="primary" @click="handleRegister" :loading="loading" style="width:100%">注册</el-button></el-form-item>
          </el-form>
          <p style="text-align:center;color:#909399;font-size:13px">已有账号？<el-button link type="primary" @click="tab = 'login'">立即登录</el-button></p>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    <div style="text-align:center;margin-top:16px">
      <router-link to="/admin/login" style="color:#909399;font-size:13px">管理员入口</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { customerApi } from '@/api'

const router = useRouter()
const tab = ref('login')
const loading = ref(false)
const loginForm = ref({ phone: '', password: '' })
const registerForm = ref({ name: '', phone: '', password: '' })

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await customerApi.login(loginForm.value)
    localStorage.setItem('customer_token', res.data.token)
    localStorage.setItem('customer_info', JSON.stringify(res.data.customer))
    ElMessage.success('登录成功')
    router.push('/shop')
  } finally { loading.value = false }
}

const handleRegister = async () => {
  if (!registerForm.value.phone || !registerForm.value.password) {
    ElMessage.warning('请填写手机号和密码'); return
  }
  loading.value = true
  try {
    await customerApi.register(registerForm.value)
    ElMessage.success('注册成功，请登录')
    loginForm.value.phone = registerForm.value.phone
    tab.value = 'login'
  } finally { loading.value = false }
}
</script>
