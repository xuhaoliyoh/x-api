package handler

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"slices"

	"github.com/Wei-Shaw/sub2api/internal/pkg/response"
	middleware2 "github.com/Wei-Shaw/sub2api/internal/server/middleware"
	"github.com/gin-gonic/gin"
)

// XAPICatalog is authenticated and uses the same group visibility as key creation.
func (h *GatewayHandler) XAPICatalog(c *gin.Context) {
	subject, ok := middleware2.GetAuthSubjectFromContext(c)
	if !ok {
		response.Unauthorized(c, "User not authenticated")
		return
	}
	groups, err := h.apiKeyService.GetAvailableGroups(c.Request.Context(), subject.UserID)
	if err != nil {
		response.ErrorFrom(c, err)
		return
	}
	out := make([]gin.H, 0, len(groups))
	for _, group := range groups {
		models, err := h.gatewayService.XAPIConfiguredModels(c.Request.Context(), &group)
		if err != nil {
			response.ErrorFrom(c, err)
			return
		}
		if len(models) > 0 {
			out = append(out, gin.H{"group_id": group.ID, "group_name": group.Name, "platform": group.Platform, "models": models, "rate_multiplier": group.RateMultiplier})
		}
	}
	response.Success(c, out)
}

// RequireConfiguredChatModel enforces the same concrete catalog used by the UI
// and /v1/models. It runs after authentication and the existing body-size limit.
func (h *GatewayHandler) RequireConfiguredChatModel(c *gin.Context) {
	key, ok := middleware2.GetAPIKeyFromContext(c)
	if !ok || key == nil || key.Group == nil {
		c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": gin.H{"message": "请为密钥绑定模型分组", "type": "permission_error"}})
		return
	}
	body, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.AbortWithStatusJSON(400, gin.H{"error": gin.H{"message": "无法读取请求体", "type": "invalid_request_error"}})
		return
	}
	c.Request.Body = io.NopCloser(bytes.NewReader(body))
	var req struct {
		Model string `json:"model"`
	}
	if json.Unmarshal(body, &req) != nil || req.Model == "" {
		c.AbortWithStatusJSON(400, gin.H{"error": gin.H{"message": "请提供有效的 model", "type": "invalid_request_error"}})
		return
	}
	models, err := h.gatewayService.XAPIConfiguredModels(c.Request.Context(), key.Group)
	if err != nil {
		c.AbortWithStatusJSON(503, gin.H{"error": gin.H{"message": "模型目录暂时不可用", "type": "server_error"}})
		return
	}
	if !slices.Contains(models, req.Model) {
		c.AbortWithStatusJSON(400, gin.H{"error": gin.H{"message": "模型未配置、已停用或不在当前密钥分组中，请查看可用模型列表", "type": "invalid_request_error", "code": "model_not_available"}})
		return
	}
	c.Next()
}

// XAPIModels serves the standard model endpoints without provider defaults.
func (h *GatewayHandler) XAPIModels(c *gin.Context) {
	apiKey, _ := middleware2.GetAPIKeyFromContext(c)
	if apiKey == nil || apiKey.Group == nil {
		writeModelsList(c, "", []string{})
		return
	}
	models, err := h.gatewayService.XAPIConfiguredModels(c.Request.Context(), apiKey.Group)
	if err != nil {
		c.JSON(503, gin.H{"error": gin.H{"message": "模型目录暂时不可用", "type": "server_error"}})
		return
	}
	writeModelsList(c, apiKey.Group.Platform, models)
}
