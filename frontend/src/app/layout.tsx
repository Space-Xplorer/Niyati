import type { Metadata } from "next";
import { Hanken_Grotesk, Crimson_Text } from "next/font/google";
import { AuthProvider } from "@/context/AuthContext";
import "./globals.css";

// Using Google Fonts as they're readily available
// Hanken Grotesk is similar to HK Grotesk
// Crimson Text provides a serif alternative to Arsenica Antiqua

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
  title: "Niyati - GST Intelligence Platform",
  description: "Real-time GST compliance monitoring with multi-agent AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${arsenica.variable} ${hkGrotesk.variable}`} suppressHydrationWarning>
      <body suppressHydrationWarning className="font-sans bg-[#f7faf9] text-[#005b52] antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
