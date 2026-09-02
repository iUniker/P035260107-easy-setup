'use client';

import { useState } from 'react';
import {
  Archive,
  Check,
  Clipboard,
  Download,
  Monitor,
  RotateCcw,
  ShieldCheck,
  Wifi,
  WifiOff,
} from 'lucide-react';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button, buttonVariants } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

const ONLINE_COMMAND =
  'curl -fsSL https://raw.githubusercontent.com/iUniker/P035260107-easy-setup/main/install.sh | sudo bash -s -- --reboot';
const OFFLINE_COMMAND = 'sudo bash install.sh --reboot';
const OFFLINE_ZIP_URL =
  'https://github.com/iUniker/P035260107-easy-setup/archive/refs/heads/main.zip';

export default function Home() {
  const [copied, setCopied] = useState<'online' | 'offline' | null>(null);

  const copyCommand = async (kind: 'online' | 'offline', command: string) => {
    await navigator.clipboard.writeText(command);
    setCopied(kind);
    window.setTimeout(() => setCopied(null), 1800);
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
              Choose one of two supported methods. Both preserve your operating system, applications, network settings, and user files.
            </p>
            <div className="mt-7 flex flex-wrap gap-x-6 gap-y-3 text-sm text-white/72">
              <span className="inline-flex items-center gap-2"><ShieldCheck className="size-4 text-[#e9ff77]" />Backs up config.txt</span>
              <span className="inline-flex items-center gap-2"><RotateCcw className="size-4 text-[#e9ff77]" />Removable setup</span>
            </div>
          </div>

          <div className="self-end rounded-2xl border border-white/10 bg-white/[.055] p-5 shadow-2xl shadow-black/15 backdrop-blur">
            <p className="text-xs font-semibold uppercase tracking-[.16em] text-[#e9ff77]">Before you install</p>
            <ol className="mt-4 space-y-3 text-sm text-white/72">
              {[
                'Shut down and unplug the Raspberry Pi before attaching the LCD.',
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
        <div className="mb-7">
          <p className="text-xs font-semibold uppercase tracking-[.14em] text-primary">Two supported methods</p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight">Use online install when possible</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            Use the downloaded ZIP only when the Raspberry Pi cannot reach GitHub. No browser SD-card writer, Windows utility, or replacement system image is required.
          </p>
        </div>

        <div className="space-y-6">
          <Card className="overflow-hidden border-0 bg-[#f7f8f3] ring-[#dfe4d0]">
            <CardHeader className="border-b border-[#dfe4d0] sm:grid-cols-[1fr_auto]">
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <Badge className="bg-primary text-white">Method 1</Badge>
                  <Badge className="bg-[#e9ff77] text-[#10201d]" variant="secondary">Recommended</Badge>
                </div>
                <CardTitle className="flex items-center gap-2 text-lg"><Wifi className="size-5 text-primary" />Online install</CardTitle>
                <CardDescription className="mt-1">Open Terminal on the Raspberry Pi or connect by SSH, then paste this one command.</CardDescription>
              </div>
              <Badge className="mt-2 self-start bg-amber-100 text-amber-900 sm:mt-0" variant="secondary">Engineering test command</Badge>
            </CardHeader>
            <CardContent className="pt-1">
              <div className="command-box">
                <code>{ONLINE_COMMAND}</code>
                <Button variant="secondary" size="lg" onClick={() => copyCommand('online', ONLINE_COMMAND)} aria-label="Copy online install command">
                  {copied === 'online' ? <Check /> : <Clipboard />}{copied === 'online' ? 'Copied' : 'Copy'}
                </Button>
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                {[
                  ['1', 'Connect', 'Internet plus Terminal or SSH'],
                  ['2', 'Run', 'Paste the single command above'],
                  ['3', 'Restart', 'The Pi reboots automatically'],
                ].map(([number, title, detail]) => (
                  <div className="step-card" key={number}>
                    <span>{number}</span><div><strong>{title}</strong><p>{detail}</p></div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="overflow-hidden border-0 bg-white ring-[#dfe4d0]">
            <CardHeader className="border-b border-[#dfe4d0] sm:grid-cols-[1fr_auto]">
              <div>
                <div className="mb-3"><Badge variant="secondary">Method 2</Badge></div>
                <CardTitle className="flex items-center gap-2 text-lg"><WifiOff className="size-5 text-primary" />Install from downloaded ZIP</CardTitle>
                <CardDescription className="mt-1">Download the package on any connected device, transfer it to the Raspberry Pi, and extract it.</CardDescription>
              </div>
              <a className={buttonVariants({ size: 'lg' })} href={OFFLINE_ZIP_URL}>
                <Download />Download ZIP
              </a>
            </CardHeader>
            <CardContent className="pt-1">
              <div className="command-box">
                <code>{OFFLINE_COMMAND}</code>
                <Button variant="secondary" size="lg" onClick={() => copyCommand('offline', OFFLINE_COMMAND)} aria-label="Copy offline install command">
                  {copied === 'offline' ? <Check /> : <Clipboard />}{copied === 'offline' ? 'Copied' : 'Copy'}
                </Button>
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                {[
                  ['1', 'Download', 'Save the ZIP before going offline'],
                  ['2', 'Transfer', 'Move it to the Pi and extract it'],
                  ['3', 'Run', 'Open Terminal in that folder'],
                ].map(([number, title, detail]) => (
                  <div className="step-card" key={number}>
                    <span>{number}</span><div><strong>{title}</strong><p>{detail}</p></div>
                  </div>
                ))}
              </div>
              <Alert className="mt-5 border-sky-200 bg-sky-50 text-sky-950">
                <Archive />
                <AlertTitle>The ZIP still installs into the customer&apos;s existing system</AlertTitle>
                <AlertDescription>Run the command from inside the extracted folder. The installer does not replace Raspberry Pi OS or remove existing applications and settings.</AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </div>

        <Alert className="mt-7 border-emerald-200 bg-emerald-50 text-emerald-950">
          <ShieldCheck />
          <AlertTitle>What both methods do</AlertTitle>
          <AlertDescription>They check compatibility, create a timestamped config.txt backup, add one managed display configuration, and reboot. Re-running the installer does not add duplicate settings.</AlertDescription>
        </Alert>

        <div className="mt-8 grid gap-4 lg:grid-cols-3">
          <Card size="sm"><CardHeader><CardTitle>Supported target</CardTitle><CardDescription>Pi Zero, Zero W/WH, and Zero 2 W/2 WH with current Raspberry Pi OS overlays.</CardDescription></CardHeader></Card>
          <Card size="sm"><CardHeader><CardTitle>GPIO warning</CardTitle><CardDescription>The LCD uses 25 GPIOs, including SPI0, GPIO18, and GPIO27. Remove other HATs for the first test.</CardDescription></CardHeader></Card>
          <Card size="sm"><CardHeader><CardTitle>Expected result</CardTitle><CardDescription>Desktop OS shows the desktop; Raspberry Pi OS Lite shows a text console. Both are normal.</CardDescription></CardHeader></Card>
        </div>

        <footer className="mt-12 flex flex-col gap-2 border-t pt-6 text-xs leading-5 text-muted-foreground sm:flex-row sm:justify-between">
          <p>MazerPi MZP351HV00TR / P035260107 · Engineering preview 0.4</p>
          <p>Customer methods: online command or downloaded ZIP.</p>
        </footer>
      </section>
    </main>
  );
}
