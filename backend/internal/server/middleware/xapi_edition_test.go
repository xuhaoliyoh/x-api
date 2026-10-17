package middleware

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestXAPIEditionGuard(t *testing.T) {
	gin.SetMode(gin.TestMode)
	for _, tc := range []struct {
		path   string
		status int
	}{
		{"/api/v1/payment/orders", 403}, {"/api/v1/redeem/", 403},
		{"/api/v1/user/aff/transfer", 403}, {"/api/v1/admin/subscriptions/assign", 403},
		{"/api/v1/admin/redeem-codes", 403}, {"/api/v1/auth/validate-promo-code", 403},
		{"/api/v1/admin/redeem-codes/create-and-redeem", 403},
		{"/api/v1/auth/register", 204}, {"/api/v1/keys", 204},
		{"/api/v1/admin/users/1/balance", 204}, {"/v1/chat/completions", 204},
	} {
		t.Run(tc.path, func(t *testing.T) {
			r := gin.New()
			r.Use(XAPIEditionGuard())
			r.POST(tc.path, func(c *gin.Context) { c.Status(204) })
			w := httptest.NewRecorder()
			r.ServeHTTP(w, httptest.NewRequest(http.MethodPost, tc.path, nil))
			if w.Code != tc.status {
				t.Fatalf("got %d, want %d", w.Code, tc.status)
			}
		})
	}
}
