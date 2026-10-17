package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

// XAPIEditionGuard keeps v0.1 quota grants administrator-only. Hiding UI alone
// must never leave self-service credit mutation endpoints accessible.
func XAPIEditionGuard() gin.HandlerFunc {
	return func(c *gin.Context) {
		path := strings.TrimRight(c.Request.URL.Path, "/")
		blocked := []string{
			"/api/v1/payment", "/api/v1/redeem", "/api/v1/subscriptions", "/api/v1/user/aff",
			"/api/v1/admin/payment", "/api/v1/admin/promo-codes", "/api/v1/admin/affiliates",
			"/api/v1/admin/subscriptions", "/api/v1/admin/redeem-codes", "/api/v1/auth/validate-promo-code",
		}
		for _, prefix := range blocked {
			if path == prefix || strings.HasPrefix(path, prefix+"/") {
				c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"code": 403, "reason": "MANUAL_QUOTA_ONLY", "message": "X-API 当前由管理员分配额度，暂不开放充值、兑换或套餐购买。"})
				return
			}
		}
		c.Next()
	}
}
