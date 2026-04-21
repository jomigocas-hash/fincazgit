"use client";

import { useState } from "react";
import axios from "axios";
import PropertyCard from "@/components/PropertyCard";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const INITIAL = {
  city: "bogota", operation_type: "venta", property_type: "apartamento",
  max_price: "", min_bedrooms: "1", min_area_m2: "",
  stratum: "", locality: "", neighborhood: "", parking: "", covered_garage: false,
};

function ScoreBadge({ score }) {
  const color = score >= 80 ? "bg-green-500" : score >= 60 ? "bg-blue-500" : score >= 40 ? "bg-yellow-500" : "bg-slate-500";
  return (
    <span className={`${color} text-white text-xs font-bold px-2 py-1 rounded-full`}>
      {score}%
    </span>
  );
}

export default function MatchingPage() {
  const [form, setForm]           = useState(INITIAL);
  const [results, setResults]     = useState(null);
  const [loading, setLoading]     = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError]         = useState(null);

  const handle = (e) => {
    const val = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setForm({ ...form, [e.target.name]: val });
  };

  const buildPayload = () => ({
    ...form,
    max_price:    parseFloat(form.max_price),
    min_bedrooms: parseInt(form.min_bedrooms),
    min_area_m2:  parseFloat(form.min_area_m2),
    stratum:      form.stratum  ? parseInt(form.stratum)  : null,
    parking:      form.parking  ? parseInt(form.parking)  : null,
  });

  const search = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const { data } = await axios.post(`${API}/matching/search?limit=30`, buildPayload());
      setResults(data);
      if (data.results.length === 0)
        setError("No se encontraron inmuebles. Intenta ampliar el precio o el área.");
    } catch (e) {
      setError(e.code === "ERR_NETWORK"
        ? "No se pudo conectar con la API en " + API
        : "Error: " + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const downloadExcel = async () => {
    setDownloading(true);
    try {
      const response = await axios.post(
        `${API}/matching/export/excel?limit=100`,
        buildPayload(),
        { responseType: "blob" }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `matching_${form.city}_${form.operation_type}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      setError("Error al generar el Excel.");
    } finally {
      setDownloading(false);
    }
  };

  const canSearch = form.max_price && form.min_area_m2;

  return (
    <>
      {/* Formulario — mismo estilo que Filters.js */}
      <div className="bg-slate-800 rounded-xl p-4 mb-6 flex flex-wrap gap-3 items-end">

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Ciudad</label>
          <select name="city" value={form.city} onChange={handle}
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm">
            <option value="bogota">Bogotá</option>
            <option value="medellin">Medellín</option>
            <option value="cali">Cali</option>
            <option value="barranquilla">Barranquilla</option>
            <option value="bucaramanga">Bucaramanga</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Operación</label>
          <select name="operation_type" value={form.operation_type} onChange={handle}
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm">
            <option value="venta">Venta</option>
            <option value="arriendo">Arriendo</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Tipo</label>
          <select name="property_type" value={form.property_type} onChange={handle}
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm">
            <option value="apartamento">Apartamento</option>
            <option value="casa">Casa</option>
            <option value="lote">Lote</option>
            <option value="oficina">Oficina</option>
            <option value="local_comercial">Local</option>
            <option value="apartamento_estudio">Apartaestudio</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Precio máximo *</label>
          <input name="max_price" type="number" value={form.max_price} onChange={handle}
            placeholder="Ej: 500000000"
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm w-36" />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Habitaciones mín.</label>
          <select name="min_bedrooms" value={form.min_bedrooms} onChange={handle}
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm">
            {[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Área mínima m² *</label>
          <input name="min_area_m2" type="number" value={form.min_area_m2} onChange={handle}
            placeholder="Ej: 60"
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm w-28" />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Localidad</label>
          <input name="locality" type="text" value={form.locality} onChange={handle}
            placeholder="Ej: Chapinero"
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm w-32" />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Barrio</label>
          <input name="neighborhood" type="text" value={form.neighborhood} onChange={handle}
            placeholder="Ej: Rosales"
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm w-32" />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Estrato</label>
          <select name="stratum" value={form.stratum} onChange={handle}
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm">
            <option value="">Cualquiera</option>
            {[1,2,3,4,5,6].map(n => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-400 text-xs">Parqueaderos</label>
          <select name="parking" value={form.parking} onChange={handle}
            className="bg-slate-700 text-white rounded px-3 py-2 text-sm">
            <option value="">No importa</option>
            {[1,2,3].map(n => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>

        <div className="flex items-center gap-2 pb-1">
          <input type="checkbox" name="covered_garage" id="covered_garage"
            checked={form.covered_garage} onChange={handle}
            className="w-4 h-4 accent-blue-500" />
          <label htmlFor="covered_garage" className="text-slate-300 text-sm">Garaje cubierto</label>
        </div>

        <button onClick={search} disabled={loading || !canSearch}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white px-5 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2">
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              Buscando...
            </>
          ) : "Buscar"}
        </button>
      </div>

      {!canSearch && (
        <p className="text-yellow-400 text-xs mb-4">
          * Completa precio máximo y área mínima para activar la búsqueda
        </p>
      )}

      {error && (
        <div className="bg-red-900/40 border border-red-700 text-red-300 rounded-xl px-4 py-3 mb-6 text-sm">
          {error}
        </div>
      )}

      {/* Resultados */}
      {results && results.results.length > 0 && (
        <>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-semibold">
              {loading ? "Cargando..." : `${results.results.length} inmuebles encontrados`}
            </h2>
            <button onClick={downloadExcel} disabled={downloading}
              className="bg-green-700 hover:bg-green-600 disabled:opacity-40 text-white px-4 py-1 rounded text-sm font-medium transition-colors">
              {downloading ? "Generando..." : "⬇ Descargar Excel"}
            </button>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="bg-slate-800 rounded-xl h-72 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {results.results.map((p) => (
                <div key={p.id} className="relative">
                  <div className="absolute top-2 left-2 z-10">
                    <ScoreBadge score={p.match_score} />
                  </div>
                  <PropertyCard property={p} />
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </>
  );
}
