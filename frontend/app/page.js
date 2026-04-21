"use client";

import { useState, useEffect, useCallback, lazy, Suspense } from "react";
import { getProperties, getMarketSummary, getByNeighborhood } from "@/lib/api";
import StatsBar from "@/components/StatsBar";
import Filters from "@/components/Filters";
import PropertyCard from "@/components/PropertyCard";
import MarketChart from "@/components/MarketChart";

const PropertyMap = lazy(() => import("@/components/PropertyMap"));

const DEFAULT_FILTERS = {
  city: "bogota",
  operation_type: "venta",
  property_type: "",
  bedrooms: "",
  min_price: "",
  max_price: "",
};

export default function Home() {
  const [filters, setFilters]         = useState(DEFAULT_FILTERS);
  const [properties, setProperties]   = useState([]);
  const [mapProperties, setMapProperties] = useState([]);
  const [stats, setStats]             = useState(null);
  const [neighborhoods, setNeighborhoods] = useState([]);
  const [loading, setLoading]         = useState(false);
  const [total, setTotal]             = useState(0);
  const [page, setPage]               = useState(1);
  const [apiError, setApiError]       = useState(false);

  const fetchAll = useCallback(async (f = filters, p = 1) => {
    setLoading(true);
    try {
      const [propsData, mapData, statsData, neighData] = await Promise.all([
        getProperties({ ...f, page: p, page_size: 20 }),
        getProperties({ ...f, page: 1, page_size: 100 }),
        getMarketSummary(f.city, f.operation_type),
        getByNeighborhood(f.city, f.operation_type),
      ]);
      setProperties(propsData.results);
      setMapProperties(mapData.results);
      setTotal(propsData.total);
      setStats(statsData);
      setNeighborhoods(neighData);
      setPage(p);
      setApiError(false);
    } catch (e) {
      console.error(e);
      setApiError(true);
      setProperties([]);
      setMapProperties([]);
      setStats(null);
      setNeighborhoods([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { fetchAll(); }, []);

  // Buscar automáticamente cuando cambian filtros clave
  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    const autoSearch = ["city", "operation_type", "property_type", "bedrooms"];
    const changed = Object.keys(newFilters).find(
      (k) => autoSearch.includes(k) && newFilters[k] !== filters[k]
    );
    if (changed) fetchAll(newFilters, 1);
  };

  const handleSearch = () => fetchAll(filters, 1);

  return (
    <>
      <Filters filters={filters} onChange={handleFilterChange} onSearch={handleSearch} />

      {apiError && (
        <div className="bg-red-900/40 border border-red-700 text-red-300 rounded-xl px-4 py-3 mb-6 text-sm">
          No se pudo conectar con la API. Verifica que el backend esté corriendo en{" "}
          <code className="text-red-200">{process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}</code>
        </div>
      )}

      <StatsBar stats={stats} />
      <MarketChart data={neighborhoods} />

      <Suspense fallback={<div className="bg-slate-800 rounded-xl h-96 animate-pulse mb-6" />}>
        <PropertyMap properties={mapProperties} />
      </Suspense>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-white font-semibold">
          {loading ? "Cargando..." : `${total} inmuebles encontrados`}
        </h2>
        <div className="flex gap-2">
          <button
            disabled={page <= 1 || loading}
            onClick={() => fetchAll(filters, page - 1)}
            className="px-3 py-1 bg-slate-700 rounded text-sm disabled:opacity-40"
          >
            ← Anterior
          </button>
          <span className="px-3 py-1 text-slate-400 text-sm">Página {page}</span>
          <button
            disabled={page * 20 >= total || loading}
            onClick={() => fetchAll(filters, page + 1)}
            className="px-3 py-1 bg-slate-700 rounded text-sm disabled:opacity-40"
          >
            Siguiente →
          </button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-slate-800 rounded-xl h-72 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {properties.map((p) => (
            <PropertyCard key={p.id} property={p} />
          ))}
        </div>
      )}

      {!loading && properties.length === 0 && (
        <div className="text-center text-slate-500 py-20">
          No se encontraron inmuebles con estos filtros.
        </div>
      )}
    </>
  );
}
