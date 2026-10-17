import { describe, expect, it, vi } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import HomeView from '../HomeView.vue'
const { app, auth } = vi.hoisted(() => ({
  app: { cachedPublicSettings: { registration_enabled: false }, fetchPublicSettings: vi.fn() },
  auth: { isAuthenticated: false, isAdmin: false }
}))
vi.mock('@/stores/app', () => ({ useAppStore: () => app }))
vi.mock('@/stores/auth', () => ({ useAuthStore: () => auth }))
describe('X-API entry points', () => {
  it('honors registration policy and keeps the upstream attribution', () => {
    app.cachedPublicSettings.registration_enabled = false
    const wrapper = mount(HomeView, { global: { stubs: { RouterLink: RouterLinkStub } } })
    expect(wrapper.findAllComponents(RouterLinkStub).some(x => x.props('to') === '/register')).toBe(false)
    expect(wrapper.text()).toContain('基于 Sub2API')
    wrapper.unmount()
  })
  it('offers registration when enabled', () => {
    app.cachedPublicSettings.registration_enabled = true
    const wrapper = mount(HomeView, { global: { stubs: { RouterLink: RouterLinkStub } } })
    expect(wrapper.findAllComponents(RouterLinkStub).some(x => x.props('to') === '/register')).toBe(true)
    wrapper.unmount()
  })
})
