import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  metadataBase: new URL('https://iuniker-mzp351-setup.kiki19890901.chatgpt.site'),
  title: 'iUniker 3.51-inch LCD Setup',
  description:
    'Install the iUniker MZP351HV00TR display without replacing your Raspberry Pi operating system.',
  openGraph: {
    title: 'iUniker 3.51-inch LCD Setup',
    description:
      'Keep your Raspberry Pi system and add the display in minutes.',
    type: 'website',
    images: [
      {
        url: '/og.png',
        width: 1200,
        height: 630,
        alt: 'iUniker 3.51-inch LCD setup: install online or from ZIP',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'iUniker 3.51-inch LCD Setup',
    description:
      'Keep your Raspberry Pi system and add the display in minutes.',
    images: ['/og.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
