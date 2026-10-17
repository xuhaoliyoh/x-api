package service

import (
	"context"
	"errors"
	"reflect"
	"testing"
)

func TestXAPIConfiguredModelIDs(t *testing.T) {
	active := func(platform string, mapping map[string]any) Account {
		return Account{Platform: platform, Status: StatusActive, Schedulable: true, Credentials: map[string]any{"model_mapping": mapping}}
	}
	disabled := active(PlatformOpenAI, map[string]any{"hidden": "hidden"})
	disabled.Schedulable = false
	accounts := []Account{
		active(PlatformOpenAI, nil), // Never invent a GPT catalog for an empty provider.
		active(PlatformOpenAI, map[string]any{"doubao-test": "doubao-test", "gpt-fake": "doubao-test", "*": "*", "z-model": "z-model"}),
		active(PlatformOpenAI, map[string]any{"doubao-test": "doubao-test"}),
		active(PlatformAnthropic, map[string]any{"claude-test": "claude-test"}), disabled,
	}
	if got := ConfiguredModelIDs(accounts, PlatformOpenAI); !reflect.DeepEqual(got, []string{"doubao-test", "z-model"}) {
		t.Fatalf("unexpected catalog: %v", got)
	}
	if got := ConfiguredModelIDs(nil, PlatformOpenAI); got == nil || len(got) != 0 {
		t.Fatalf("empty catalog must be [], got %v", got)
	}
}

type xapiCatalogRepository struct {
	AccountRepository
	accounts       []Account
	err            error
	requestedGroup int64
}

func (r *xapiCatalogRepository) ListSchedulableByGroupID(_ context.Context, id int64) ([]Account, error) {
	r.requestedGroup = id
	return r.accounts, r.err
}
func TestXAPIGroupCatalogIsolation(t *testing.T) {
	repo := &xapiCatalogRepository{accounts: []Account{{Platform: PlatformOpenAI, Status: StatusActive, Schedulable: true, Credentials: map[string]any{"model_mapping": map[string]any{"model-a": "model-a", "model-b": "model-b"}}}}}
	svc := &GatewayService{accountRepo: repo}
	group := &Group{ID: 17, Platform: PlatformOpenAI, ModelAllowlist: GroupModelAllowlist{Enabled: true, Models: []string{"model-b"}}}
	got, err := svc.XAPIConfiguredModels(context.Background(), group)
	if err != nil || repo.requestedGroup != 17 || !reflect.DeepEqual(got, []string{"model-b"}) {
		t.Fatalf("group isolation failed: %v, %v", got, err)
	}
	repo.err = errors.New("database unavailable")
	if _, err = svc.XAPIConfiguredModels(context.Background(), group); err == nil {
		t.Fatal("must propagate errors instead of advertising fallback models")
	}
	got, err = svc.XAPIConfiguredModels(context.Background(), nil)
	if err != nil || len(got) != 0 {
		t.Fatal("unbound keys must have no catalog")
	}
}
