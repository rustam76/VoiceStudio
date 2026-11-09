import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { apiArgs } from '../../scripts/dev-api.mjs';
import { DEFAULT_BACKEND_PORT } from '../../config/app-config.mjs';

test('Browser development uses the locked environment and configured backend port', () => {
  const args = apiArgs({});
  assert.deepEqual(args.slice(0, 4), ['run', '--project', 'deploy/online', '--no-sync']);
  assert.ok(args.includes('backend.main:app'));
  assert.equal(args[args.indexOf('--host') + 1], '127.0.0.1');
  assert.equal(args[args.indexOf('--port') + 1], String(DEFAULT_BACKEND_PORT));
  const custom = apiArgs({ OMNIVOICE_PORT: '4980' });
  assert.equal(custom[custom.indexOf('--port') + 1], '4980');
  assert.throws(() => apiArgs({ OMNIVOICE_PORT: '65536' }), /port/i);
  assert.throws(() => apiArgs({ OMNIVOICE_PORT: 'abc' }), /port/i);
});

test('API readiness polls the public backend health route', () => {
  const script = readFileSync(new URL('../../scripts/wait-app-port.mjs', import.meta.url), 'utf8');
  assert.match(script, /\/health/);
  assert.doesNotMatch(script, /\/system\/info/);
});
