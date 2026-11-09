import test from 'node:test';
import assert from 'node:assert/strict';
import { setupApi } from '../../scripts/setup-api.mjs';
import { prepareDev } from '../../scripts/prepare-dev.mjs';

test('API setup installs only the frozen CPU environment', () => {
  const calls = [];
  const env = { EXAMPLE: 'value' };
  const status = setupApi({ env, run: (...args) => { calls.push(args); return { status: 0 }; } });
  assert.equal(status, 0);
  assert.equal(calls[0][0], 'uv');
  assert.deepEqual(calls[0][1], ['sync', '--project', 'deploy/online', '--frozen', '--no-default-groups']);
  assert.equal(calls[0][2].env, env);
});

test('API setup propagates failed install status and process errors', () => {
  assert.equal(setupApi({ run: () => ({ status: 9 }) }), 9);
  assert.equal(setupApi({ run: () => ({ status: null }) }), 1);
  assert.throws(() => setupApi({ run: () => ({ error: new Error('uv missing') }) }), /uv missing/);
});

test('development installs browser and Online dependencies', () => {
  const calls = [];
  assert.equal(prepareDev({ env: {}, run: (cmd, args) => { calls.push([cmd, args]); return { status: 0 }; } }), 0);
  assert.deepEqual(calls, [['bun', ['install']], ['bun', ['run', 'setup:api']]]);
});

test('development supports explicitly skipping backend setup and stops on failure', () => {
  const calls = [];
  prepareDev({ env: { VOICESTUDIO_SKIP_BACKEND: '1' }, run: (cmd, args) => { calls.push(args); return { status: 0 }; } });
  assert.deepEqual(calls, [['install']]);
  assert.equal(prepareDev({ run: () => ({ status: 5 }) }), 5);
});
