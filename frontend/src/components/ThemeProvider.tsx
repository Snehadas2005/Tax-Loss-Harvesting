"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  // 1. defaultTheme="light" forces the website to start in day mode.
  // 2. enableSystem={false} tells it to completely ignore your Mac's dark mode settings.
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="light"
      enableSystem={false}
    >
      {children}
    </NextThemesProvider>
  );
}
