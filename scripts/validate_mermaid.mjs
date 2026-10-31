// Validate actual Mermaid syntax, not just README/source text equality.
// Run in CI after installing a pinned Mermaid package into RUNNER_TEMP.
// This does not need a browser/Chromium because it uses mermaid.parse().
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const modulePath = process.env.MERMAID_MODULE;
if (!modulePath || !fs.existsSync(modulePath)) {
  throw new Error('MERMAID_MODULE must point to an installed Mermaid ESM package');
}
const { default: mermaid } = await import(pathToFileURL(path.resolve(modulePath)).href);
mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });

const diagramFiles = [
  'docs/diagrams/c4-containers.mmd',
  'docs/diagrams/data-flow-trust-boundaries.mmd',
  'docs/diagrams/agent-workflow.mmd',
  'docs/diagrams/feedback-sequence.mmd',
];
let errors = 0;
for (const file of diagramFiles) {
  const source = fs.readFileSync(file, 'utf8');
  try {
    const result = await mermaid.parse(source);
    if (!result || typeof result.diagramType !== 'string') {
      throw new Error('Mermaid parser produced no diagram type');
    }
    console.log(`PASS: Mermaid parser accepted ${file} (${result.diagramType})`);
  } catch (error) {
    errors++;
    console.error(`FAIL: Mermaid parser rejected ${file}\n${error.stack ?? error}`);
  }
}
if (errors) process.exit(1);
