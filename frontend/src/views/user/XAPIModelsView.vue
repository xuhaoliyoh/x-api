<template>
  <AppLayout>
    <div class="mx-auto max-w-5xl space-y-6">
      <div class="flex flex-wrap items-center justify-between gap-4"><div><h1 class="text-2xl font-semibold">可用模型</h1><p class="mt-2 text-sm text-gray-500">来自后台启用的上游配置。创建密钥时，请选择对应分组。</p></div><button class="btn btn-secondary" :disabled="loading" @click="load">{{ loading ? '加载中…' : '刷新列表' }}</button></div>
      <div v-if="error" role="alert" class="rounded-xl bg-red-50 p-5 text-red-700">{{ error }}<button class="ml-3 underline" @click="load">重试</button></div>
      <div v-else-if="loading" class="card p-10 text-center text-gray-500">正在读取模型配置…</div>
      <div v-else-if="groups.length === 0" class="card px-6 py-16 text-center"><h2 class="text-lg font-medium">暂时没有可用模型</h2><p class="mx-auto mt-3 max-w-lg text-sm leading-7 text-gray-500">管理员尚未配置可用上游，或你的账号还没有对应分组权限。配置完成后，真实模型 ID 会出现在这里。</p><router-link v-if="auth.isAdmin" to="/admin/accounts" class="btn btn-primary mt-6">配置上游账号</router-link></div>
      <section v-for="group in groups" :key="group.group_id" class="card overflow-hidden">
        <div class="flex items-center justify-between border-b border-gray-100 p-5 dark:border-dark-700"><div><h2 class="font-semibold">{{ group.group_name }}</h2><p class="mt-1 text-xs text-gray-500">创建密钥时选择此分组</p></div><span class="rounded-full bg-primary-50 px-3 py-1 text-xs text-primary-700 dark:bg-primary-950 dark:text-primary-300">{{ group.models.length }} 个模型</span></div>
        <div v-for="model in group.models" :key="model" class="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 px-5 py-4 last:border-0 dark:border-dark-800"><code class="break-all text-sm">{{ model }}</code><button class="text-sm text-primary-600 dark:text-primary-300 hover:underline" @click="copy(model)">{{ copied === model ? '已复制' : '复制模型 ID' }}</button></div>
      </section>
      <p class="text-xs leading-6 text-gray-500">模型列表会随后台配置更新；实际上游是否可用以调用结果为准。额度由管理员分配，可在用量页面查看消耗。</p>
    </div>
  </AppLayout>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { apiClient } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
interface ModelGroup { group_id: number; group_name: string; platform: string; models: string[]; rate_multiplier: number }
const groups = ref<ModelGroup[]>([])
const loading = ref(false)
const error = ref('')
const copied = ref('')
async function load() {
  loading.value = true; error.value = ''
  try { const { data } = await apiClient.get<ModelGroup[]>('/x-api/models'); groups.value = data }
  catch { error.value = '模型列表加载失败，请稍后重试。' }
  finally { loading.value = false }
}
async function copy(model: string) {
  try { await navigator.clipboard.writeText(model); copied.value = model }
  catch { error.value = '复制失败，请手动选择模型 ID 复制。' }
}
onMounted(load)
</script>
