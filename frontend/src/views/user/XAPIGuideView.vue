<template>
  <AppLayout>
    <div class="mx-auto max-w-4xl space-y-6">
      <header><p class="mb-2 text-xs font-semibold tracking-widest text-primary-600 dark:text-primary-300">X-API / QUICK START</p><h1 class="text-2xl font-semibold">发送你的第一次请求</h1><p class="mt-3 text-sm text-gray-500">先获得额度，再创建密钥，最后选择模型。</p></header>
      <section class="grid gap-4 sm:grid-cols-3"><div v-for="(step, index) in steps" :key="step.title" class="card p-5"><span class="text-xs font-semibold text-primary-600 dark:text-primary-300">0{{ index + 1 }}</span><h2 class="mt-3 font-medium">{{ step.title }}</h2><p class="mt-2 text-sm leading-7 text-gray-500">{{ step.body }}</p></div></section>
      <section class="card space-y-4 p-6"><h2 class="text-lg font-semibold">客户端连接信息</h2><dl class="space-y-3 text-sm"><div><dt class="text-gray-500">Base URL</dt><dd class="mt-1 break-all font-mono">{{ baseURL }}</dd></div><div><dt class="text-gray-500">API Key</dt><dd class="mt-1">在「<router-link to="/keys" class="text-primary-600 dark:text-primary-300 underline">API 密钥</router-link>」页面创建的密钥</dd></div><div><dt class="text-gray-500">模型 ID</dt><dd class="mt-1">从「<router-link to="/models" class="text-primary-600 dark:text-primary-300 underline">可用模型</router-link>」复制，并选择相同分组的密钥</dd></div></dl></section>
      <section class="overflow-hidden rounded-xl border border-gray-200 bg-white text-gray-800 dark:border-dark-700 dark:bg-dark-900 dark:text-dark-200"><div class="border-b border-gray-200 dark:border-dark-700 px-6 py-4 text-sm">终端调用示例 · 替换环境变量后执行</div><pre class="overflow-x-auto p-6 text-xs leading-7 sm:text-sm"><code>{{ example }}</code></pre></section>
      <section class="card p-6"><h2 class="font-semibold">调用遇到问题？</h2><ul class="mt-4 space-y-3 text-sm leading-7 text-gray-500"><li><strong>401：</strong>检查密钥是否正确、是否已停用。</li><li><strong>403 / 额度不足：</strong>联系管理员分配额度，检查密钥限额和有效期。</li><li><strong>模型不可用：</strong>核对模型 ID 和密钥分组，确认管理员已启用对应上游。</li><li><strong>429：</strong>降低请求频率或并发，稍后重试。</li></ul></section>
      <p class="text-xs leading-6 text-gray-500">X-API 的账户额度是站内记账额度，与火山方舟赠送的 token 数量分别管理；密钥限额是额外的使用上限，不会给账户增加额度。登录后可在个人资料中修改密码。</p>
    </div>
  </AppLayout>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAppStore } from '@/stores/app'
const app = useAppStore()
const baseURL = computed(() => `${(app.cachedPublicSettings?.api_base_url || window.location.origin).replace(/\/$/, '').replace(/\/v1$/, '')}/v1`)
const steps = [
  { title: '联系管理员分配额度', body: '新注册账号默认额度为 0。管理员分配后，可在控制台查看剩余额度。' },
  { title: '创建专属密钥', body: '选择模型所属分组，设置名称与可选限额。妥善保管密钥。' },
  { title: '选择模型并调用', body: '填写接口地址、密钥和实际模型 ID。调用后在用量记录中查看结果。' }
]
const example = computed(() => `export X_API_KEY='替换为你的密钥'
export X_API_MODEL='替换为可用模型ID'

curl '${baseURL.value}/chat/completions' --header "Authorization: Bearer $X_API_KEY" --header 'Content-Type: application/json' --data-binary @- <<EOF
{"model":"$X_API_MODEL","messages":[{"role":"user","content":"你好"}],"stream":false}
EOF`)
</script>
