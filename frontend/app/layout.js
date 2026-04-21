import "./globals.css";
import "leaflet/dist/leaflet.css";
import Link from "next/link";

export const metadata = {
  title: "Inmuebles Colombia",
  description: "Datos inmobiliarios normalizados y deduplicados",
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body className="bg-slate-900 text-white min-h-screen">
        <header className="border-b border-slate-700 px-6 py-4 flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-sm">
              IC
            </div>
            <span className="font-semibold text-lg tracking-tight">Inmuebles Colombia</span>
          </div>
          <nav className="flex gap-4 text-sm">
            <Link href="/" className="text-slate-300 hover:text-white transition-colors">
              Explorar
            </Link>
            <Link href="/matching" className="text-slate-300 hover:text-white transition-colors">
              Matching
            </Link>
            <Link href="/buscar" className="text-slate-300 hover:text-white transition-colors">
              Buscar por ID
            </Link>
          </nav>
        </header>
        <main className="px-6 py-6 max-w-7xl mx-auto">{children}</main>
      </body>
    </html>
  );
}
