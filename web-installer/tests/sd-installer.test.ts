import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  FRAGMENT_CONTENT,
  MARKER_BEGIN,
  buildManagedConfig,
  findConflicts,
  parseActiveValue,
  parseIncludes,
  stripManagedBlock,
  timestampForFilename,
} from '../lib/sd-installer.ts';

void test('embedded browser fragment matches the reviewed installer fragment', async () => {
  const reviewed = await readFile(new URL('../../config/mzp351hv00tr-kms.txt', import.meta.url), 'utf8');
  assert.equal(FRAGMENT_CONTENT, reviewed);
});

void test('fresh install preserves settings and adds one complete managed block', () => {
  const result = buildManagedConfig('# customer config\ndtparam=audio=on\n', false, false);
  assert.match(result, /dtparam=audio=on/);
  assert.match(result, /dtoverlay=vc4-kms-v3d/);
  assert.match(result, /max_framebuffers=2/);
  assert.equal(result.match(new RegExp(MARKER_BEGIN, 'g'))?.length, 1);
});

void test('repeated install is idempotent and keeps existing KMS settings', () => {
  const source = 'dtoverlay=vc4-kms-v3d\nmax_framebuffers=2\n';
  const first = buildManagedConfig(source, true, true);
  const second = buildManagedConfig(first, true, true);
  assert.equal(second.match(new RegExp(MARKER_BEGIN, 'g'))?.length, 1);
  assert.equal(second.match(/dtoverlay=vc4-kms-v3d/g)?.length, 1);
  assert.equal(second.match(/max_framebuffers=2/g)?.length, 1);
});

void test('CRLF input keeps CRLF line endings', () => {
  const result = buildManagedConfig('dtparam=audio=on\r\n', false, false);
  assert.equal(result.replace(/\r\n/g, '').includes('\n'), false);
});

void test('managed block removal detects malformed and missing blocks', () => {
  assert.equal(stripManagedBlock('dtparam=audio=on\n').found, false);
  assert.throws(() => stripManagedBlock(`${MARKER_BEGIN}\n`), /incomplete/);
});

void test('conflicts, includes, and active prefix values are parsed safely', () => {
  const source = `# dtoverlay=ads7846\ninclude usercfg.txt\nos_prefix=vendor/\noverlay_prefix=overlays/\ndtoverlay=vc4-fkms-v3d\n`;
  assert.deepEqual(parseIncludes(source), ['usercfg.txt']);
  assert.equal(parseActiveValue(source, 'os_prefix'), 'vendor/');
  assert.deepEqual(findConflicts(source), ['the legacy FKMS graphics stack is enabled']);
});

void test('backup timestamp is deterministic and filename-safe', () => {
  const date = new Date(2026, 8, 1, 12, 3, 4, 5);
  assert.equal(timestampForFilename(date), '20260901-120304-005');
});
