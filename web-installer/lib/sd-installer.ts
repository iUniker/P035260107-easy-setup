export const FRAGMENT_NAME = 'mzp351hv00tr.txt';
export const MARKER_BEGIN = '# BEGIN MZP351HV00TR MANAGED CONFIG';
export const MARKER_END = '# END MZP351HV00TR MANAGED CONFIG';

export const FRAGMENT_CONTENT = `# MazerPi MZP351HV00TR - 3.51-inch DPI LCD
#
# This file uses drivers and Device Tree overlays supplied by the OS kernel.
# The installer loads vc4-kms-v3d before including this file when necessary.

# The touchscreen is permanently selected, so free the SPI0 chip-select pins
# for the RGB565 DPI data bus.
dtoverlay=spi0-0cs
dtoverlay=ads7846,penirq=27,swapxy=1,xmin=180,xmax=3900,ymin=180,ymax=3900

# 480x320 RGB565 DPI panel.
dtoverlay=vc4-kms-dpi-generic
dtparam=hactive=480,hfp=20,hsync=10,hbp=10
dtparam=vactive=320,vfp=10,vsync=2,vbp=2
dtparam=clock-frequency=12000000
dtparam=hsync-invert,vsync-invert,pixclk-invert
dtparam=rgb565-padhi

# GPIO18 controls the backlight.
dtparam=backlight-gpio=18
gpio=18=op,dh,pd
`;

export function stripManagedBlock(input: string): {
  content: string;
  found: boolean;
} {
  const newline = input.includes('\r\n') ? '\r\n' : '\n';
  const lines = input.replace(/\r\n/g, '\n').split('\n');
  const kept: string[] = [];
  let inBlock = false;
  let found = false;

  for (const line of lines) {
    const comparable = line.trim();
    if (comparable === MARKER_BEGIN) {
      if (inBlock) throw new Error('Managed configuration contains a duplicate begin marker.');
      inBlock = true;
      found = true;
      continue;
    }
    if (comparable === MARKER_END) {
      if (!inBlock) throw new Error('Managed configuration has an end marker without a begin marker.');
      inBlock = false;
      continue;
    }
    if (!inBlock) kept.push(line);
  }
  if (inBlock) throw new Error('Managed configuration block is incomplete.');

  return { content: kept.join(newline), found };
}

export function parseIncludes(input: string): string[] {
  return input
    .replace(/\r\n/g, '\n')
    .split('\n')
    .map((line) => line.match(/^\s*include\s+([^#\s]+)/i)?.[1])
    .filter((value): value is string => Boolean(value));
}

export function parseActiveValue(input: string, key: string): string | null {
  let result: string | null = null;
  for (const rawLine of input.replace(/\r\n/g, '\n').split('\n')) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    const separator = line.indexOf('=');
    if (separator < 0 || line.slice(0, separator).trim() !== key) continue;
    result = line.slice(separator + 1).split('#')[0].trim();
  }
  return result;
}

export function findConflicts(input: string): string[] {
  const conflicts: string[] = [];
  const rules: [RegExp, string][] = [
    [/^\s*include\s+mzp351hv00tr-(?:new|old)\.txt(?:\s|$)/i, 'the original MZP351 TXT setup is already included'],
    [/^\s*dtoverlay=vc4-(?:f)?kms-dpi-/i, 'another DPI display overlay is enabled'],
    [/^\s*dtoverlay=vc4-fkms-v3d(?:[,\s]|$)/i, 'the legacy FKMS graphics stack is enabled'],
    [/^\s*dtoverlay=ads7846(?:[,\s]|$)/i, 'another ADS7846 touchscreen is enabled'],
    [/^\s*dtoverlay=spi0-0cs(?:[,\s]|$)/i, 'SPI0 chip-select settings are already enabled'],
    [/^\s*enable_dpi_lcd\s*=\s*1/i, 'legacy DPI output is enabled'],
    [/^\s*dpi_(?:group|mode|output_format|timings)\s*=/i, 'legacy DPI timings are present'],
    [/^\s*display_default_lcd\s*=\s*1/i, 'legacy default LCD output is enabled'],
  ];

  for (const rawLine of input.replace(/\r\n/g, '\n').split('\n')) {
    if (/^\s*#/.test(rawLine)) continue;
    for (const [pattern, message] of rules) {
      if (pattern.test(rawLine)) conflicts.push(message);
    }
  }
  return [...new Set(conflicts)];
}

export function buildManagedConfig(
  input: string,
  hasKms: boolean,
  hasMaxFramebuffers: boolean,
): string {
  const newline = input.includes('\r\n') ? '\r\n' : '\n';
  const stripped = stripManagedBlock(input).content.replace(/[\r\n]+$/g, '');
  const block = [
    MARKER_BEGIN,
    '[all]',
    ...(hasKms ? [] : ['dtoverlay=vc4-kms-v3d']),
    ...(hasMaxFramebuffers ? [] : ['max_framebuffers=2']),
    `include ${FRAGMENT_NAME}`,
    MARKER_END,
  ];
  return `${stripped}${stripped ? `${newline}${newline}` : ''}${block.join(newline)}${newline}`;
}

export function timestampForFilename(date: Date): string {
  const pad = (value: number, width = 2) => String(value).padStart(width, '0');
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}-${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}-${pad(date.getMilliseconds(), 3)}`;
}
