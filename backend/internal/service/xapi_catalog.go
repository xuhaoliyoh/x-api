package service

import (
	"context"
	"sort"
	"strings"
)

// ConfiguredModelIDs returns concrete, identity-mapped model IDs only. No
// provider defaults or wildcard patterns are advertised as available models.
func ConfiguredModelIDs(accounts []Account, platform string) []string {
	set := make(map[string]struct{})
	for _, account := range accounts {
		if account.Status != StatusActive || !account.Schedulable || (platform != "" && account.Platform != platform) {
			continue
		}
		for name, target := range stringMappingFromRaw(account.Credentials["model_mapping"]) {
			name = strings.TrimSpace(name)
			if name == "" || strings.ContainsAny(name, "*?") || name != strings.TrimSpace(target) {
				continue
			}
			set[name] = struct{}{}
		}
	}
	models := make([]string, 0, len(set))
	for name := range set {
		models = append(models, name)
	}
	sort.Strings(models)
	return models
}

func (s *GatewayService) XAPIConfiguredModels(ctx context.Context, group *Group) ([]string, error) {
	if group == nil {
		return []string{}, nil
	}
	accounts, err := s.accountRepo.ListSchedulableByGroupID(ctx, group.ID)
	if err != nil {
		return nil, err
	}
	models := ConfiguredModelIDs(accounts, group.Platform)
	if group.ModelAllowlistEnabled() {
		models = group.ModelAllowlist.FilterForListing(models)
	}
	return models, nil
}
