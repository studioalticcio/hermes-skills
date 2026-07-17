import { Client } from '/home/user/.npm-global/lib/node_modules/mcp-auchan-drive/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import { StdioClientTransport } from '/home/user/.npm-global/lib/node_modules/mcp-auchan-drive/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';
import { execFileSync } from 'node:child_process';

// Direct MCP tool caller for auchan-drive. Avoid guessing Hermes CLI invoke syntax;
// Hermes CLI exposes list/test/configure but not a stable "call tool" subcommand.
// Usage: node scripts/auchan-call.mjs search_product '{"query":"lait","limit":5}'
const cfgJson = execFileSync('/home/user/.hermes/hermes-agent/.venv/bin/python', ['-c', `import yaml,json; cfg=yaml.safe_load(open('/home/user/.hermes/config.yaml')); print(json.dumps(cfg['mcp_servers']['auchan-drive']['env']))`], { encoding: 'utf8' }).trim();
const cfgEnv = JSON.parse(cfgJson);
const tool = process.argv[2];
const args = process.argv[3] ? JSON.parse(process.argv[3]) : {};
if (!tool) throw new Error('usage: node auchan-call.mjs <tool> <json-args>');

const transport = new StdioClientTransport({
  command: 'node',
  args: ['/home/user/.npm-global/lib/node_modules/mcp-auchan-drive/dist/index.js'],
  env: { ...process.env, ...cfgEnv },
});
const client = new Client({ name: 'auchan-direct', version: '0.0.1' });
await client.connect(transport);
const res = await client.callTool({ name: tool, arguments: args });
const text = res.content?.map(c => c.text ?? '').join('\n') ?? '';
console.log(JSON.stringify({ isError: Boolean(res.isError), text }, null, 2));
await client.close();
