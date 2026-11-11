import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const projectDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const electronCli = path.join(projectDir, "node_modules", "electron", "cli.js");
const engineExecutable = process.env.QUANTT_ENGINE_EXECUTABLE;
const logs = [];

if (!engineExecutable || !fs.existsSync(engineExecutable)) {
  throw new Error(`Built engine executable not found: ${engineExecutable ?? "(unset)"}`);
}

const electron = spawn(process.execPath, [electronCli, "--no-sandbox", "--disable-gpu", projectDir], {
  cwd: projectDir,
  env: {
    ...process.env,
    QUANTT_ENGINE_EXECUTABLE: engineExecutable,
    QUANTT_TEST_MODE: "1",
  },
  stdio: ["ignore", "pipe", "pipe"],
});

for (const stream of [electron.stdout, electron.stderr]) {
  stream.setEncoding("utf8");
  stream.on("data", (chunk) => {
    logs.push(chunk);
    process.stdout.write(chunk);
  });
}

let exitResult;
electron.once("exit", (code, signal) => {
  exitResult = { code, signal };
});

try {
  await delay(15_000);

  if (exitResult) {
    throw new Error(`Electron exited before the smoke check (code ${exitResult.code}, signal ${exitResult.signal}).`);
  }

  let health;
  let lastError;
  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch("http://127.0.0.1:8000/test", { signal: AbortSignal.timeout(2_000) });
      health = await response.json();
      if (!response.ok || health.status !== "running") {
        throw new Error(`Unexpected /test response (${response.status}): ${JSON.stringify(health)}`);
      }
      break;
    } catch (error) {
      lastError = error;
      await delay(500);
    }
  }

  if (!health) {
    throw new Error(`Backend health check failed: ${lastError?.message ?? "no response"}`);
  }
  console.log(`Backend health check passed: ${health.message}`);

  const output = logs.join("");
  if (/\[(?:Electron|Renderer) error\]/i.test(output)) {
    throw new Error("Electron reported a JavaScript or renderer error during startup.");
  }
} finally {
  if (!exitResult && electron.pid) {
    if (process.platform === "win32") {
      const killer = spawn("taskkill", ["/pid", String(electron.pid), "/t", "/f"], { stdio: "ignore" });
      await new Promise((resolve) => killer.once("exit", resolve));
    } else {
      electron.kill("SIGTERM");
      await Promise.race([new Promise((resolve) => electron.once("exit", resolve)), delay(5_000)]);
      if (!exitResult) electron.kill("SIGKILL");
    }
  }
}
