"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getPropertyById } from "@/lib/api";
import PropertyCard from "@/components/PropertyCard";

export default function BuscarPage() {
  const [query, setQuery]     = useState("");
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const router = useRouter();

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await getPropertyById(query.trim());
      setResult(data);
    } catch (e) {
      setError(`No se encontró ningún inmueble con ID "${query}".`);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") search();
  };

  return (
    <>
      <div className="mb-6">
        <h1 className="text-white text-2xl font-bold">Buscar por ID</h1>
        <p className="text-slate-400 text-sm mt-1">
          Ingresa el ID interno del inmueble para encontrarlo directamente.
        </p>
      </div>

      <div className="bg-slate-800 rounded-xl p-4 mb-6 flex gap-3 items-end">
        <div className="flex flex-col gap-1 flex-1 max-w-xs">
          <label className="text-slate-400 text-xs">ID del inmueble</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ej: 483"
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm"
          />
        </div>
        <button
          onClick={search}
          disabled={loading || !query.trim()}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white px-5 py-2 rounded text-sm font-medium transition-colors"
        >
          {loading ? "Buscando..." : "Buscar"}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/40 border border-red-700 text-red-300 rounded-xl px-4 py-3 mb-6 text-sm">
          {error}
        </div>
      )}

      {result && (
        <>
          <div className="mb-4">
            <span className="text-slate-400 text-sm">
              Inmueble encontrado — ID <span className="text-white font-mono">{result.id}</span>
              {result.canonical_id && (
                <span className="ml-3 text-slate-500 text-xs font-mono">
                  canonical: {result.canonical_id}
                </span>
              )}
            </span>
          </div>
          <div className="max-w-xs">
            <PropertyCard property={result} />
          </div>
          <button
            onClick={() => router.push(`/properties/${result.id}`)}
            className="mt-4 bg-slate-700 hover:bg-slate-600 text-white px-5 py-2 rounded text-sm transition-colors"
          >
            Ver detalle completo →
          </button>
        </>
      )}
    </>
  );
}
