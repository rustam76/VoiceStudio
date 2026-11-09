#!/usr/bin/env node

import waitOn from 'wait-on';
import { DEFAULT_BACKEND_PORT, DEFAULT_WEB_PORT } from '../config/app-config.mjs';

const target = process.argv[2];
const definitions = {
  api: {
    resource: `http-get://127.0.0.1:${process.env.OMNIVOICE_PORT || DEFAULT_BACKEND_PORT}/health`,
    timeout: 300_000,
  },
  web: { resource: `http://localhost:${process.env.OMNIVOICE_UI_PORT || process.env.VOICESTUDIO_UI_PORT || DEFAULT_WEB_PORT}`, timeout: 120_000 },
};
const selected = definitions[target];
if (!selected) throw new TypeError('Usage: node scripts/wait-app-port.mjs <api|web>');

await waitOn({ resources: [selected.resource], timeout: selected.timeout });
