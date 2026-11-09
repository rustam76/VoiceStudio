import { expect, it } from 'vitest';
import { extraSettingsFor } from './settings-page';

it('keeps API settings and excludes cloud and translation providers in the hosted studio', () => {
  const paths: string[] = extraSettingsFor(true).map((item) => item.to);
  expect(paths).toContain('/settings/openapi');
  expect(paths).toContain('/settings/privacy');
  expect(paths).not.toContain('/settings/account');
  expect(paths).not.toContain('/settings/credentials');
});
