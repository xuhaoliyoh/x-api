-- X-API fresh-install defaults. Never overwrite an administrator's settings.
-- The upstream initializer is not invoked by the runtime provider. Apply the
-- first-run settings in both automatic and interactive installation modes.
INSERT INTO settings (key, value) VALUES
  ('site_name', 'X-API'),
  ('site_subtitle', '你的模型，你的 API 入口'),
  ('doc_url', '/guide'),
  ('registration_enabled', 'true'),
  ('email_verify_enabled', 'false'),
  ('default_balance', '0'),
  ('promo_code_enabled', 'false'),
  ('subscription_enabled', 'false'),
  ('purchase_subscription_enabled', 'false'),
  ('affiliate_enabled', 'false')
ON CONFLICT (key) DO NOTHING;
