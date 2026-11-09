import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");

export function prepareDev({
  env = process.env,
  run = spawnSync,
} = {}) {
  const commands = [['install']];
  if (env.VOICESTUDIO_SKIP_BACKEND !== '1') commands.push(['run', 'setup:api']);

  for (const args of commands) {
    const result = run("bun", args, { cwd: root, env, stdio: "inherit" });
    if (result.error) throw result.error;
    if (result.status !== 0) return result.status ?? 1;
  }
  return 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    process.exitCode = prepareDev();
  } catch (error) {
    console.error(`[dev] ${error.message}`);
    process.exitCode = 1;
  }
}
