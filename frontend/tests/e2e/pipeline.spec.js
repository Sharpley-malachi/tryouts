import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const API_BASE = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:8000/api/v1';

test('upload CSV ingest via API', async ({ request }) => {
  const csvPath = path.join(process.cwd(), '..', 'tmp', 'test_upload.csv');
  const csv = fs.existsSync(csvPath) ? fs.readFileSync(csvPath) : 'time,price\n2025-01-01T00:00:00,100';

  const response = await request.post(`${API_BASE}/pipeline/ingest/csv`, {
    multipart: {
      file: {
        name: 'file',
        mimeType: 'text/csv',
        buffer: Buffer.from(csv)
      }
    }
  });
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body.status).toBeTruthy();
});

test('submit feedback via API', async ({ request }) => {
  const payload = { prediction_id: 'test-123', result: 'WIN', notes: 'automated e2e' };
  const response = await request.post(`${API_BASE}/general/feedback`, { data: payload });
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body).toHaveProperty('status');
});
