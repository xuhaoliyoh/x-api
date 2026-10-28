<template>
  <div class="min-h-screen bg-brand-canvas text-gray-900 dark:bg-dark-950 dark:text-white">
    <header class="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
      <router-link to="/home" class="flex items-center gap-3 text-xl font-bold tracking-tight"><img src="/psyduck-logo.jpg" alt="X-API 可达鸭" class="h-10 w-10 rounded-xl bg-white object-contain" />X-API</router-link>
      <nav class="flex items-center gap-5 text-sm">
        <router-link to="/guide" class="hidden text-gray-500 hover:text-primary-600 dark:text-primary-300 sm:block">接入指南</router-link>
        <router-link :to="auth.isAuthenticated ? dashboard : '/login'" class="rounded-full border border-gray-200 px-5 py-2.5 dark:border-dark-700">{{ auth.isAuthenticated ? '进入控制台' : '登录' }}</router-link>
      </nav>
    </header>
    <main class="mx-auto max-w-6xl px-6 pb-20 pt-10 sm:pt-24">
      <div class="grid items-center gap-14 lg:grid-cols-2">
        <section>
          <p class="mb-6 text-xs font-semibold uppercase tracking-[0.25em] text-primary-700 dark:text-primary-400">YOUR MODELS. YOUR API.</p>
          <h1 class="text-4xl font-semibold leading-tight tracking-tight sm:text-6xl">连接模型，<br /><span class="text-gray-900 underline decoration-primary-200 decoration-8 underline-offset-8 dark:text-gray-100 dark:decoration-primary-800">从这里开始。</span></h1>
          <p class="mt-7 max-w-lg text-lg leading-8 text-gray-500 dark:text-gray-400">一个地址，一枚密钥。通过 X-API 接入管理员提供的模型，让每一次调用都有清晰的记录。</p>
          <div class="mt-9 flex flex-wrap gap-3">
            <router-link :to="auth.isAuthenticated ? '/keys' : (registrationEnabled ? '/register' : '/login')" class="btn btn-primary px-6 py-3.5">{{ auth.isAuthenticated ? '管理我的密钥' : (registrationEnabled ? '创建账号 →' : '登录控制台 →') }}</router-link>
            <router-link to="/models" class="btn btn-secondary px-6 py-3.5">查看可用模型</router-link>
          </div>
          <p class="mt-5 text-xs text-gray-500">注册后由管理员分配额度，即可创建密钥开始调用。</p>
        </section>
        <section class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-lg shadow-gray-900/5 dark:border-dark-700 dark:bg-dark-900" aria-label="API 接入示例">
          <div class="flex items-center justify-between border-b border-gray-200 dark:border-dark-700 px-6 py-4"><span class="font-mono text-xs text-gray-600 dark:text-dark-300">POST /v1/chat/completions</span><span class="rounded-full bg-primary-100 px-2.5 py-1 text-xs text-primary-700 dark:bg-primary-900 dark:text-primary-200">OpenAI 兼容</span></div>
          <pre class="overflow-x-auto bg-primary-50/40 p-6 text-sm leading-8 text-gray-700 dark:bg-dark-800/40 dark:text-dark-200"><code><span class="text-primary-700 dark:text-primary-300">{</span>
  "model": "后台配置的实际模型 ID",
  "messages": [
    { "role": "user",
      "content": "你好，X-API" }
  ],
  "stream": true
<span class="text-primary-700 dark:text-primary-300">}</span></code></pre>
          <div class="border-t border-gray-200 dark:border-dark-700 px-6 py-4 text-xs text-gray-500 dark:text-dark-400">模型范围与访问权限由管理员配置</div>
        </section>
      </div>
      <section class="mt-24 grid gap-8 border-t border-gray-200 pt-10 sm:grid-cols-3 dark:border-dark-800">
        <article v-for="item in features" :key="item.title"><p class="mb-4 font-mono text-xs text-primary-600 dark:text-primary-300">{{ item.number }}</p><h2 class="text-lg font-semibold">{{ item.title }}</h2><p class="mt-3 text-sm leading-7 text-gray-500 dark:text-gray-400">{{ item.body }}</p></article>
      </section>
    </main>
    <footer class="mx-auto max-w-6xl border-t border-gray-200 px-6 py-6 text-xs text-gray-500 dark:border-dark-800">
      <div class="flex flex-wrap items-center justify-center gap-x-6 gap-y-3 sm:justify-between">
        <span>© {{ new Date().getFullYear() }} X-API</span>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" class="transition-colors hover:text-primary-700 dark:hover:text-primary-300">京ICP备2026072941号-1</a>
        <a href="https://github.com/Wei-Shaw/sub2api" target="_blank" rel="noopener noreferrer" class="transition-colors hover:text-primary-700 dark:hover:text-primary-300">基于 Sub2API · LGPL-3.0</a>
      </div>
    </footer>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
const auth = useAuthStore()
const app = useAppStore()
const dashboard = computed(() => auth.isAdmin ? '/admin/dashboard' : '/dashboard')
const registrationEnabled = computed(() => app.cachedPublicSettings?.registration_enabled === true)
const features = [
  { number: '01 / ACCESS', title: '统一接入', body: '使用统一的 API 地址，在兼容客户端中填写你的密钥和模型 ID。' },
  { number: '02 / CONTROL', title: '额度可控', body: '管理员分配使用额度，密钥可单独设置限额，也可以随时停用。' },
  { number: '03 / VISIBILITY', title: '用量清晰', body: '查看请求记录、模型消耗和剩余额度，轻松定位调用中的问题。' }
]
onMounted(() => { void app.fetchPublicSettings() })
</script>
