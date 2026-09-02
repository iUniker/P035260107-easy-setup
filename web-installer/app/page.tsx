'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  ChevronRight,
  Clipboard,
  FolderOpen,
  HardDrive,
  LockKeyhole,
  Monitor,
  RotateCcw,
  ShieldCheck,
  Terminal,
  Wifi,
} from 'lucide-react';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  FRAGMENT_CONTENT,
  FRAGMENT_NAME,
  buildManagedConfig,
  findConflicts,
  parseActiveValue,
  parseIncludes,
  stripManagedBlock,
  timestampForFilename,
} from '@/lib/sd-installer';

declare global {
  interface Window {
    showDirectoryPicker?: (options?: {
      id?: string;
      mode?: 'read' | 'readwrite';
      startIn?: string;
    }) => Promise<FileSystemDirectoryHandle>;
  }

  interface Document {
    modelContext?: {
      registerTool: (
        tool: {
          name: string;
          title?: string;
          description: string;
          inputSchema: object;
          annotations?: {
            readOnlyHint?: boolean;
            untrustedContentHint?: boolean;
          };
          execute: (input: unknown) => Record<string, unknown> | Promise<unknown>;
        },
        options?: { signal?: AbortSignal },
      ) => void | Promise<void>;
    };
  }
}

type Method = 'online' | 'sd-card';
type Notice = {
  kind: 'idle' | 'ready' | 'working' | 'success' | 'error';
  title: string;
  detail: string;
  items?: string[];
};

const ONLINE_COMMAND =
  'curl -fsSL https://raw.githubusercontent.com/iUniker/P035260107-easy-setup/main/install.sh | sudo bash -s -- --reboot';
const REQUIRED_OVERLAYS = [
  'spi0-0cs.dtbo',
  'ads7846.dtbo',
  'vc4-kms-dpi-generic.dtbo',
];

async function readTextFile(
  root: FileSystemDirectoryHandle,
  path: string,
): Promise<string> {
  const parts = path.split('/').filter(Boolean);
  const fileName = parts.pop();
  if (!fileName) throw new Error('Invalid file path.');

  let directory = root;
  for (const part of parts) {
    if (part === '..') throw new Error('A configuration include leaves the boot partition.');
    directory = await directory.getDirectoryHandle(part);
  }
  const handle = await directory.getFileHandle(fileName);
  return (await handle.getFile()).text();
}

async function writeTextFile(
  root: FileSystemDirectoryHandle,
  path: string,
  content: string,
): Promise<void> {
  const handle = await root.getFileHandle(path, { create: true });
  const writable = await handle.createWritable();
  await writable.write(content);
  await writable.close();
}

async function fileExists(
  root: FileSystemDirectoryHandle,
  path: string,
): Promise<boolean> {
  try {
    await readTextFile(root, path);
    return true;
  } catch {
    return false;
  }
}

async function collectConfigFiles(
  root: FileSystemDirectoryHandle,
  mainConfig: string,
): Promise<{ path: string; content: string }[]> {
  const collected = [{ path: 'config.txt', content: mainConfig }];
  const seen = new Set(['config.txt']);

  const visit = async (content: string, depth: number) => {
    if (depth > 12) throw new Error('Configuration include depth exceeds 12.');

    for (const include of parseIncludes(content)) {
      const normalized = include.replace(/^\/+/, '');
      if (!normalized || normalized.split('/').includes('..')) {
        throw new Error(`Unsafe include path: ${include}`);
      }
      if (seen.has(normalized)) continue;
      seen.add(normalized);

      try {
        const nested = await readTextFile(root, normalized);
        collected.push({ path: normalized, content: nested });
        await visit(nested, depth + 1);
      } catch (error) {
        if (error instanceof DOMException && error.name === 'NotFoundError') continue;
        throw error;
      }
    }
  };

  await visit(mainConfig, 0);
  return collected;
}

async function directoryExists(
  root: FileSystemDirectoryHandle,
  path: string,
): Promise<boolean> {
  try {
    let directory = root;
    for (const part of path.split('/').filter(Boolean)) {
      if (part === '..') return false;
      directory = await directory.getDirectoryHandle(part);
    }
    for (const overlay of REQUIRED_OVERLAYS) {
      await directory.getFileHandle(overlay);
    }
    return true;
  } catch {
    return false;
  }
}

async function findOverlayDirectory(
  root: FileSystemDirectoryHandle,
  configs: { path: string; content: string }[],
): Promise<string | null> {
  const content = configs.map((config) => config.content).join('\n');
  const osPrefix = (parseActiveValue(content, 'os_prefix') ?? '').replace(/^\/+|\/+$/g, '');
  const overlayPrefix = (
    parseActiveValue(content, 'overlay_prefix') ?? 'overlays'
  ).replace(/^\/+|\/+$/g, '');
  const candidates = [
    [osPrefix, overlayPrefix].filter(Boolean).join('/'),
    overlayPrefix,
    'overlays',
  ].filter((path, index, values) => path && values.indexOf(path) === index);

  for (const candidate of candidates) {
    if (await directoryExists(root, candidate)) return candidate;
  }
  return null;
}

function customerError(error: unknown): string {
  if (error instanceof DOMException && error.name === 'AbortError') {
    return 'Folder selection was canceled. No files were changed.';
  }
  if (error instanceof DOMException && error.name === 'NotFoundError') {
    return 'config.txt was not found. Select the small Raspberry Pi boot partition (usually named bootfs).';
  }
  if (error instanceof Error) return error.message;
  return 'The operation could not be completed. No boot settings were intentionally removed.';
}

export default function Home() {
  const [method, setMethod] = useState<Method>('online');
  const [directory, setDirectory] = useState<FileSystemDirectoryHandle | null>(null);
  const [notice, setNotice] = useState<Notice>({
    kind: 'idle',
    title: 'No SD card selected',
    detail: 'Select the boot partition only when you are ready to use the SD-card method.',
  });
  const [copied, setCopied] = useState(false);
  const browserSupported = useMemo(
    () => typeof window !== 'undefined' && Boolean(window.showDirectoryPicker) && window.isSecureContext,
    [],
  );
  const busy = notice.kind === 'working';

  useEffect(() => {
    const context = document.modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();

    void Promise.resolve(
      context.registerTool(
        {
          name: 'start_display_setup_method',
          title: 'Open display setup method',
          description:
            'Open either the online Raspberry Pi command or the offline SD-card setup panel. This only changes the visible setup panel and does not modify any files.',
          inputSchema: {
            type: 'object',
            properties: {
              method: { type: 'string', enum: ['online', 'sd-card'] },
            },
            required: ['method'],
            additionalProperties: false,
          },
          annotations: { readOnlyHint: true, untrustedContentHint: false },
          execute(input) {
            const value = input as { method?: unknown };
            if (value.method !== 'online' && value.method !== 'sd-card') {
              throw new Error('method must be online or sd-card');
            }
            setMethod(value.method);
            return {
              method: value.method,
              status: 'opened',
              requiresUserConfirmation: value.method === 'sd-card',
            };
          },
        },
        { signal: lifecycle.signal },
      ),
    ).catch(() => undefined);

    return () => lifecycle.abort();
  }, []);

  const copyCommand = async () => {
    await navigator.clipboard.writeText(ONLINE_COMMAND);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  };

  const chooseBootPartition = async () => {
    if (!window.showDirectoryPicker) return;
    setNotice({
      kind: 'working',
      title: 'Checking the selected partition',
      detail: 'Reading boot files only. Nothing has been changed yet.',
    });

    try {
      const selected = await window.showDirectoryPicker({
        id: 'mzp351-bootfs',
        mode: 'readwrite',
      });
      const config = await readTextFile(selected, 'config.txt');
      stripManagedBlock(config);
      setDirectory(selected);
      setNotice({
        kind: 'ready',
        title: `${selected.name} is ready to check`,
        detail: 'Confirm that this is the Raspberry Pi boot partition, then click Install display setup.',
      });
    } catch (error) {
      setDirectory(null);
      setNotice({ kind: 'error', title: 'Boot partition not selected', detail: customerError(error) });
    }
  };

  const installToCard = async () => {
    if (!directory) return;
    setNotice({
      kind: 'working',
      title: 'Checking compatibility',
      detail: 'Looking for existing display settings and required Raspberry Pi overlays.',
    });

    try {
      const originalConfig = await readTextFile(directory, 'config.txt');
      const stripped = stripManagedBlock(originalConfig);
      const configs = await collectConfigFiles(directory, stripped.content);
      const conflicts = configs.flatMap((config) =>
        findConflicts(config.content).map((message) => `${config.path}: ${message}`),
      );
      if (conflicts.length) {
        throw new Error(`Conflicting settings found. ${conflicts.join(' ')}`);
      }

      const overlayDirectory = await findOverlayDirectory(directory, configs);
      if (!overlayDirectory) {
        throw new Error(
          'Required Raspberry Pi overlays were not found. Update Raspberry Pi OS before installing this display.',
        );
      }

      const combined = configs.map((config) => config.content).join('\n');
      const hasKms = /^\s*dtoverlay=vc4-kms-v3d(?:[,\s]|$)/im.test(combined);
      const hasMaxFramebuffers = /^\s*max_framebuffers\s*=\s*(?:[2-9]|[1-9]\d+)\s*(?:#.*)?$/im.test(combined);
      const updatedConfig = buildManagedConfig(originalConfig, hasKms, hasMaxFramebuffers);
      const stamp = timestampForFilename(new Date());

      await writeTextFile(directory, `config.txt.backup-${stamp}-web`, originalConfig);
      if (await fileExists(directory, FRAGMENT_NAME)) {
        const oldFragment = await readTextFile(directory, FRAGMENT_NAME);
        await writeTextFile(directory, `${FRAGMENT_NAME}.backup-${stamp}-web`, oldFragment);
      }
      await writeTextFile(directory, FRAGMENT_NAME, FRAGMENT_CONTENT);
      await writeTextFile(directory, 'config.txt', updatedConfig);

      setNotice({
        kind: 'success',
        title: 'Display setup installed',
        detail: 'Safely eject the SD card, insert it into the powered-off Raspberry Pi, attach the LCD, and power on.',
        items: [
          `Backup created: config.txt.backup-${stamp}-web`,
          `Required overlays found in: ${overlayDirectory}`,
          'Your Linux system partition and personal files were not opened.',
        ],
      });
    } catch (error) {
      setNotice({ kind: 'error', title: 'Setup stopped safely', detail: customerError(error) });
    }
  };

  const uninstallFromCard = async () => {
    if (!directory) return;
    setNotice({
      kind: 'working',
      title: 'Removing managed setup',
      detail: 'Creating a backup before removing only the block added by this installer.',
    });

    try {
      const originalConfig = await readTextFile(directory, 'config.txt');
      const stripped = stripManagedBlock(originalConfig);
      if (!stripped.found) {
        throw new Error('The managed MZP351 setup block was not found. No files were changed.');
      }
      const stamp = timestampForFilename(new Date());
      await writeTextFile(directory, `config.txt.backup-${stamp}-web`, originalConfig);
      await writeTextFile(directory, 'config.txt', stripped.content);
      if (await fileExists(directory, FRAGMENT_NAME)) {
        const fragment = await readTextFile(directory, FRAGMENT_NAME);
        await writeTextFile(directory, `${FRAGMENT_NAME}.disabled-${stamp}-web`, fragment);
        await directory.removeEntry(FRAGMENT_NAME);
      }
      setNotice({
        kind: 'success',
        title: 'Managed setup removed',
        detail: 'The original customer configuration remains in place. Safely eject the SD card before removing it.',
      });
    } catch (error) {
      setNotice({ kind: 'error', title: 'Removal stopped', detail: customerError(error) });
    }
  };

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b border-white/8 bg-[#081312] text-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5 sm:px-8">
          <div className="flex items-center gap-3">
            <span className="grid size-9 place-items-center rounded-xl bg-[#e9ff77] text-[#10201d] shadow-[0_0_24px_rgba(233,255,119,.18)]">
              <Monitor className="size-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold tracking-wide">MAZERPI</p>
              <p className="text-[11px] text-white/55">DISPLAY SETUP</p>
            </div>
          </div>
          <Badge className="border-white/15 bg-white/8 text-white" variant="outline">
            Engineering preview
          </Badge>
        </div>
      </header>

      <section className="border-b bg-[#0c1b19] text-white">
        <div className="mx-auto grid max-w-6xl gap-10 px-5 py-12 sm:px-8 lg:grid-cols-[1.08fr_.92fr] lg:py-16">
          <div className="max-w-2xl">
            <Badge className="mb-5 bg-[#e9ff77] text-[#10201d]">MZP351HV00TR · 480×320</Badge>
            <h1 className="max-w-xl text-balance text-4xl font-semibold leading-[1.05] tracking-[-0.035em] sm:text-5xl">
              Keep your Raspberry Pi system. Add the display in minutes.
            </h1>
            <p className="mt-5 max-w-xl text-pretty text-base leading-7 text-white/66">
              No replacement image, custom kernel, or application reset. This setup adds only the boot settings needed by the LCD and resistive touchscreen.
            </p>
            <div className="mt-7 flex flex-wrap gap-x-6 gap-y-3 text-sm text-white/72">
              <span className="inline-flex items-center gap-2"><ShieldCheck className="size-4 text-[#e9ff77]" />Backs up config.txt</span>
              <span className="inline-flex items-center gap-2"><LockKeyhole className="size-4 text-[#e9ff77]" />Files stay on your device</span>
              <span className="inline-flex items-center gap-2"><RotateCcw className="size-4 text-[#e9ff77]" />Removable setup</span>
            </div>
          </div>

          <div className="self-end rounded-2xl border border-white/10 bg-white/[.055] p-5 shadow-2xl shadow-black/15 backdrop-blur">
            <p className="text-xs font-semibold uppercase tracking-[.16em] text-[#e9ff77]">Before power-on</p>
            <ol className="mt-4 space-y-3 text-sm text-white/72">
              {[
                'Shut down and unplug the Raspberry Pi.',
                'Align the 40-pin header carefully.',
                'Remove other GPIO HATs for the first test.',
                'Disconnect HDMI and use a stable 5V supply.',
              ].map((item, index) => (
                <li className="flex gap-3" key={item}>
                  <span className="grid size-5 shrink-0 place-items-center rounded-full border border-white/15 text-[11px] text-white/65">{index + 1}</span>
                  {item}
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
        <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[.14em] text-primary">Choose your setup</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight">Start with the easiest method</h2>
          </div>
          <p className="max-w-md text-sm leading-6 text-muted-foreground">Online setup is fastest when Terminal or SSH already works. Use the SD-card method when the LCD is blank and the Pi is otherwise inaccessible.</p>
        </div>

        <div className="mb-5 grid gap-3 sm:grid-cols-2" role="tablist" aria-label="Setup method">
          <button
            type="button"
            role="tab"
            aria-selected={method === 'online'}
            onClick={() => setMethod('online')}
            className={`method-tab ${method === 'online' ? 'method-tab-active' : ''}`}
          >
            <span className="method-icon"><Wifi /></span>
            <span><strong>Online install</strong><small>One Terminal command · Recommended</small></span>
            <ChevronRight className="ml-auto size-4" />
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={method === 'sd-card'}
            onClick={() => setMethod('sd-card')}
            className={`method-tab ${method === 'sd-card' ? 'method-tab-active' : ''}`}
          >
            <span className="method-icon"><HardDrive /></span>
            <span><strong>SD-card install</strong><small>Chrome or Edge on a computer</small></span>
            <ChevronRight className="ml-auto size-4" />
          </button>
        </div>

        {method === 'online' ? (
          <Card className="border-0 bg-[#f7f8f3] ring-[#dfe4d0]">
            <CardHeader className="border-b border-[#dfe4d0] sm:grid-cols-[1fr_auto]">
              <div>
                <CardTitle className="flex items-center gap-2 text-lg"><Terminal className="size-5 text-primary" />Run on your Raspberry Pi</CardTitle>
                <CardDescription className="mt-1">Open Terminal or connect by SSH, then paste this command.</CardDescription>
              </div>
              <Badge className="mt-2 self-start bg-amber-100 text-amber-900 sm:mt-0" variant="secondary">Engineering test command</Badge>
            </CardHeader>
            <CardContent className="pt-1">
              <div className="command-box">
                <code>{ONLINE_COMMAND}</code>
                <Button variant="secondary" size="lg" onClick={copyCommand} aria-label="Copy install command">
                  {copied ? <Check /> : <Clipboard />}{copied ? 'Copied' : 'Copy'}
                </Button>
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                {[
                  ['1', 'Checks', 'Pi model, overlays, and conflicts'],
                  ['2', 'Backs up', 'Your existing config.txt first'],
                  ['3', 'Installs', 'Managed settings, then reboots'],
                ].map(([number, title, detail]) => (
                  <div className="step-card" key={number}>
                    <span>{number}</span><div><strong>{title}</strong><p>{detail}</p></div>
                  </div>
                ))}
              </div>
              <Alert className="mt-5 border-sky-200 bg-sky-50 text-sky-950">
                <ShieldCheck />
                <AlertTitle>Your configured system stays in place</AlertTitle>
                <AlertDescription>The installer does not replace Raspberry Pi OS, install a custom kernel, or touch applications, network settings, or user files.</AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-0 bg-[#f7f8f3] ring-[#dfe4d0]">
            <CardHeader className="border-b border-[#dfe4d0]">
              <CardTitle className="flex items-center gap-2 text-lg"><HardDrive className="size-5 text-primary" />Install directly to the SD card</CardTitle>
              <CardDescription>Insert the card into this computer and select its small boot partition, usually named bootfs.</CardDescription>
            </CardHeader>
            <CardContent>
              {!browserSupported && (
                <Alert className="mb-5 border-amber-200 bg-amber-50 text-amber-950">
                  <AlertTriangle />
                  <AlertTitle>Chrome or Edge is required</AlertTitle>
                  <AlertDescription>This browser cannot safely write the selected SD-card folder. Open this page in a current desktop version of Chrome or Microsoft Edge.</AlertDescription>
                </Alert>
              )}

              <div className={`status-panel status-${notice.kind}`} aria-live="polite">
                <span className="status-icon">
                  {notice.kind === 'success' ? <CheckCircle2 /> : notice.kind === 'error' ? <AlertTriangle /> : <FolderOpen />}
                </span>
                <div>
                  <strong>{notice.title}</strong>
                  <p>{notice.detail}</p>
                  {notice.items && <ul>{notice.items.map((item) => <li key={item}>{item}</li>)}</ul>}
                </div>
              </div>

              <div className="mt-5 flex flex-wrap gap-3">
                <Button size="lg" onClick={chooseBootPartition} disabled={!browserSupported || busy}>
                  <FolderOpen />{directory ? 'Choose a different card' : 'Select boot partition'}
                </Button>
                <Button size="lg" onClick={installToCard} disabled={!directory || busy} className="bg-[#1d6d5d] text-white hover:bg-[#155447]">
                  <ShieldCheck />Install display setup
                </Button>
                {directory && (
                  <Button size="lg" variant="outline" onClick={uninstallFromCard} disabled={busy}>
                    <RotateCcw />Remove managed setup
                  </Button>
                )}
              </div>
              <p className="mt-4 flex items-center gap-2 text-xs text-muted-foreground"><LockKeyhole className="size-3.5" />The browser reads and writes only the folder you explicitly select. Nothing is uploaded.</p>
            </CardContent>
          </Card>
        )}

        <div className="mt-8 grid gap-4 lg:grid-cols-3">
          <Card size="sm"><CardHeader><CardTitle>Supported target</CardTitle><CardDescription>Pi Zero, Zero W/WH, and Zero 2 W/2 WH with current Raspberry Pi OS overlays.</CardDescription></CardHeader></Card>
          <Card size="sm"><CardHeader><CardTitle>GPIO warning</CardTitle><CardDescription>The LCD uses 25 GPIOs, including SPI0, GPIO18, and GPIO27. Remove other HATs for the first test.</CardDescription></CardHeader></Card>
          <Card size="sm"><CardHeader><CardTitle>Resistive touch</CardTitle><CardDescription>Use light pressure from a fingertip, fingernail, or stylus. Multi-touch is not supported.</CardDescription></CardHeader></Card>
        </div>

        <footer className="mt-12 flex flex-col gap-2 border-t pt-6 text-xs leading-5 text-muted-foreground sm:flex-row sm:justify-between">
          <p>MazerPi MZP351HV00TR / P035260107 · Engineering preview 0.3</p>
          <p>Keep the original TXT setup as the support fallback until hardware validation is complete.</p>
        </footer>
      </section>
    </main>
  );
}
