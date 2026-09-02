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
  title: 'MazerPi 3.51-inch LCD Setup',
  description:
    'Install the MazerPi MZP351HV00TR display without replacing your Raspberry Pi operating system.',
  openGraph: {
    title: 'MazerPi 3.51-inch LCD Setup',
    description:
      'Keep your Raspberry Pi system and add the display in minutes.',
    type: 'website',
  },
  twitter: {
    card: 'summary',
    title: 'MazerPi 3.51-inch LCD Setup',
    description:
      'Keep your Raspberry Pi system and add the display in minutes.',
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
