import { spawnSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

export function setupApi({ env = process.env, run = spawnSync } = {}) {
  const result = run('uv', ['sync', '--frozen', '--no-default-groups', '--group', 'cpu', '--group', 'dev', '--extra', 'supertonic'], {
    cwd: root, env, stdio: 'inherit',
  });
  if (result.error) throw result.error;
  return result.status ?? 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try { process.exitCode = setupApi(); }
  catch (error) { console.error(`[setup] ${error.message}`); process.exitCode = 1; }
}
