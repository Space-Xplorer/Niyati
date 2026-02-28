import type { Metadata } from "next";
import { Hanken_Grotesk, Crimson_Text } from "next/font/google";
import "./globals.css";

const hkGrotesk = Hanken_Grotesk({
  variable: "--font-hk-grotesk",
  subsets: ["latin"],
  display: 'swap',
});

const arsenica = Crimson_Text({
  variable: "--font-arsenica",
  weight: ["400", "600", "700"],
  subsets: ["latin"],
  display: 'swap',
});

export const metadata: Metadata = {
  title: "GST e-Invoice | Simulated Portal",
  description: "Government filing terminal for live injection into Niyati.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${arsenica.variable} ${hkGrotesk.variable}`} suppressHydrationWarning>
      <body suppressHydrationWarning className="font-sans bg-[#f7faf9] text-[#005b52] antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
