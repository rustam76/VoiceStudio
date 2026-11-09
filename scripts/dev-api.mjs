import { spawnSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { DEFAULT_BACKEND_PORT } from '../config/app-config.mjs';

export function apiArgs(env = process.env) {
  const port = Number(env.OMNIVOICE_PORT || DEFAULT_BACKEND_PORT);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new TypeError('Invalid backend port');
  return ['run', '--project', 'deploy/online', '--no-sync', 'python', '-m', 'uvicorn',
    'backend.main:app', '--host', '127.0.0.1', '--port', String(port), '--workers', '1'];
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const result = spawnSync('uv', apiArgs(), {
    cwd: resolve(dirname(fileURLToPath(import.meta.url)), '..'), stdio: 'inherit', env: { ...process.env, OMNIVOICE_STUDIO_LITE: '1', OMNIVOICE_TTS_BACKEND: 'supertonic3', OMNIVOICE_MCP_DISABLE: '1', OMNIVOICE_PRELOAD_CAPTURE_ASR: '0', OMNIVOICE_PRELOAD_WATERMARK: '0' },
  });
  if (result.error) throw result.error;
  process.exitCode = result.status ?? 1;
}
