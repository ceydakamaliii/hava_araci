import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import ClientLayout from "@/components/client-layout";
import { AuthProvider } from "@/context/AuthContext";
import { Footer } from "@/components/footer";

const geist = Geist({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Aircraft Works",
  description: "Aircraft Works Application",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geist.className} min-h-screen bg-background`}>
        <AuthProvider>
          <div className="min-h-screen flex flex-col">
            <main className="flex-1">
              <ClientLayout>{children}</ClientLayout>
            </main>
            <Footer />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
