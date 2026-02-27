# Font Files Required

To complete the Niyati hero section setup, you need to download and place the following font files in this directory:

## Required Fonts

1. **Arsenica Antiqua** (for serif headings)
   - File needed: `ArsenicaAntiqua-Regular.woff2`
   - This font gives the authoritative, legal/forensic weight to main headings

2. **HK Grotesk** (for body text)
   - File needed: `HKGrotesk-Regular.woff2`
   - Provides high legibility for complex ML and GST concepts
   - Alternative: You can use Google Fonts "Hanken Grotesk" as a substitute

## Where to Get These Fonts

- **Arsenica Antiqua**: Search for this font on font marketplaces or use a similar serif alternative
- **HK Grotesk**: Available on various font platforms, or use "Hanken Grotesk" from Google Fonts

## Alternative: Use Google Fonts

If you prefer to use Google Fonts instead of local fonts, you can modify `frontend/src/app/layout.tsx` to import fonts like this:

```typescript
import { Hanken_Grotesk } from "next/font/google";

const hkGrotesk = Hanken_Grotesk({
  variable: "--font-hk-grotesk",
  subsets: ["latin"],
});
```

## File Format

Make sure the font files are in `.woff2` format for optimal web performance.
