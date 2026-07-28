#!/usr/bin/env node
/**
 * COMPUTEX.md .mcpb entry stub.
 *
 * The manifest's mcp_config runs `npx -y taiwanmd@latest mcp serve` directly
 * for a zero-install, always-latest experience. This file satisfies the
 * manifest `entry_point` requirement and makes `node server/index.js` behave
 * identically (both paths launch the same published MCP server over stdio),
 * so the bundle works whether a host invokes the command or the entry point.
 *
 * No API key, no config — COMPUTEX.md knowledge is a public good.
 */

import { spawn } from 'node:child_process';

const child = spawn('npx', ['-y', 'taiwanmd@latest', 'mcp', 'serve'], {
  stdio: 'inherit',
});

child.on('exit', (code) => process.exit(code ?? 0));
child.on('error', (err) => {
  // stderr only — stdout must stay pristine for the MCP protocol.
  console.error(`[taiwanmd] failed to launch MCP server: ${err.message}`);
  process.exit(1);
});
