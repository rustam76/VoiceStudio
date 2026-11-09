import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';

const root = new URL('../../', import.meta.url);
const read = (path) => readFileSync(new URL(path, root), 'utf8');

test('latest application retains the full browser UI without native apps', () => {
  assert.deepEqual(JSON.parse(read('package.json')).workspaces, ['frontend']);
  for (const path of ['electron', 'mobile', 'native', 'store', 'snap']) {
    assert.equal(existsSync(new URL(path, root)), false, `${path} must not be shipped`);
  }
  const html = read('frontend/src/renderer/index.html');
  assert.match(html, /src="\/src\/main\.tsx"/);
  assert.match(read('frontend/src/renderer/src/main.tsx'), /<App\s*\/>/);
  assert.match(read('frontend/src/renderer/src/app.tsx'), /RouterProvider/);
  assert.doesNotMatch(read('frontend/vite.web.config.ts'), /online\/main|ONLINE_BUILD/);
  const pkg = JSON.parse(read('frontend/package.json'));
  assert.doesNotMatch(JSON.stringify([pkg.dependencies, pkg.devDependencies]), /electron|tauri/);
});

test('hosting serves the full authenticated backend and preserves persistent storage', () => {
  const docker = read('deploy/online/Dockerfile');
  assert.doesNotMatch(docker, /electron\/|online:app/);
  assert.match(docker, /backend\.main:app/);
  assert.match(docker, /--group cpu/);
  assert.match(docker, /USER studio/);
  assert.match(docker, /COPY frontend\/src frontend\/src/);
  const compose = read('docker-compose.yml');
  assert.match(compose, /studio-data:\/data/);
  assert.match(compose, /OMNIVOICE_API_KEY.*\:\?/);
  assert.match(compose, /OMNIVOICE_SERVER_MODE/);
  assert.doesNotMatch(compose, /OMNIVOICE_ONLINE/);
});
