import { describe, expect, it } from 'vitest'
import { isXAPIPathEnabled } from '../xapi'
describe('manual quota edition navigation', () => {
  it('blocks deferred commerce paths including direct deep links', () => {
    for (const path of ['/redeem', '/purchase', '/orders/7', '/admin/payment/settings', '/admin/subscriptions']) expect(isXAPIPathEnabled(path)).toBe(false)
  })
  it('retains registration, quota administration and user access', () => {
    for (const path of ['/register', '/login', '/admin/users', '/admin/accounts', '/keys', '/models', '/guide', '/profile']) expect(isXAPIPathEnabled(path)).toBe(true)
  })
})
