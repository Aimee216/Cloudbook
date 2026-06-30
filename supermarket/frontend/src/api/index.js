import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器 - 添加token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = 'Bearer ' + token
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器 - 统一处理错误
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(msg)
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      window.location.href = '/admin/login'
    }
    return Promise.reject(error)
  }
)

export default request

// ========== 认证接口 ==========
export const authApi = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/auth/register', data),
  getMe: () => request.get('/auth/me')
}

// ========== 分类接口 ==========
export const categoryApi = {
  list: () => request.get('/categories'),
  create: (data) => request.post('/categories', data),
  update: (id, data) => request.put('/categories/' + id, data),
  delete: (id) => request.delete('/categories/' + id)
}

// ========== 商品接口 ==========
export const productApi = {
  list: (params) => request.get('/products', { params }),
  get: (id) => request.get('/products/' + id),
  create: (data) => request.post('/products', data),
  update: (id, data) => request.put('/products/' + id, data),
  delete: (id) => request.delete('/products/' + id)
}

// ========== 库存接口 ==========
export const stockApi = {
  list: (params) => request.get('/stock', { params }),
  inbound: (data) => request.post('/stock/inbound', data),
  outbound: (data) => request.post('/stock/outbound', data),
  records: (params) => request.get('/stock/records', { params }),
  createCheck: () => request.post('/stock/check'),
  finishCheck: (id) => request.put('/stock/check/' + id)
}

// ========== 订单接口 ==========
export const orderApi = {
  list: (params) => request.get('/orders', { params }),
  get: (id) => request.get('/orders/' + id),
  create: (data) => request.post('/orders', data),
  updateStatus: (id, status) => request.put('/orders/' + id + '/status', { status })
}

// ========== 顾客接口 ==========
export const customerApi = {
  list: (params) => request.get('/customers', { params }),
  get: (id) => request.get('/customers/' + id),
  register: (data) => request.post('/customers/register', data),
  login: (data) => request.post('/customers/login', data)
}

// ========== 供应商接口 ==========
export const supplierApi = {
  list: (params) => request.get('/suppliers', { params }),
  get: (id) => request.get('/suppliers/' + id),
  create: (data) => request.post('/suppliers', data),
  update: (id, data) => request.put('/suppliers/' + id, data),
  delete: (id) => request.delete('/suppliers/' + id)
}

// ========== 员工接口 ==========
export const employeeApi = {
  list: (params) => request.get('/employees', { params }),
  get: (id) => request.get('/employees/' + id),
  create: (data) => request.post('/employees', data),
  update: (id, data) => request.put('/employees/' + id, data),
  delete: (id) => request.delete('/employees/' + id),
  logs: (params) => request.get('/employees/logs/all', { params })
}

// ========== 报表接口 ==========
export const statsApi = {
  sales: (params) => request.get('/stats/sales', { params }),
  topProducts: (params) => request.get('/stats/top-products', { params }),
  inventoryAnalysis: () => request.get('/stats/inventory-analysis'),
  finance: (params) => request.get('/stats/finance', { params })
}
