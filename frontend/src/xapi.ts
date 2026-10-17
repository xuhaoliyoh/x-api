// The first release uses administrator-assigned quota only.
export function isXAPIPathEnabled(path: string): boolean {
  const deferred = ['/purchase', '/orders', '/redeem', '/affiliate', '/subscriptions',
    '/payment', '/admin/orders', '/admin/payment', '/admin/redeem', '/admin/promo-codes',
    '/admin/affiliates', '/admin/subscriptions', '/batch-image', '/admin/plugins']
  return !deferred.some(prefix => path === prefix || path.startsWith(prefix + '/'))
}
