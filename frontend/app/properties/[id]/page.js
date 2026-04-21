"use client";

import { useEffect, useState, Suspense, lazy } from "react";
import { useParams, useRouter } from "next/navigation";
import { getPropertyById } from "@/lib/api";
import axios from "axios";

const SingleMap = lazy(() => import("@/components/SingleMap"));
const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const fmt = (n) => n ? "$" + Number(n).toLocaleString("es-CO") : "—";

function PriceScoreBadge({ score }) {
  if (!score || score.score === null) return null;

  const styles = {
    green:  "bg-green-900/40 border-green-600 text-green-300",
    yellow: "bg-yellow-900/40 border-yellow-600 text-yellow-300",
    orange: "bg-orange-900/40 border-orange-600 text-orange-300",
    red:    "bg-red-900/40 border-red-600 text-red-300",
  };

  const icons = { green: "↓", yellow: "≈", orange: "↑", red: "↑↑" };
  const style = styles[score.color] || styles.yellow;
  const icon  = icons[score.color] || "≈";
  const sign  = score.diff_pct > 0 ? "+" : "";

  return (
    <div className={`border rounded-xl p-4 ${style}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="font-semibold text-sm">Score de Precio</span>
        <span className="text-2xl font-bold">{icon}</span>
      </div>
      <p className="font-bold text-lg">{score.label}</p>
      <p className="text-sm mt-1">
        {sign}{score.diff_pct}% vs promedio del {score.scope}
      </p>
      <div className="mt-3 pt-3 border-t border-current border-opacity-20 grid grid-cols-2 gap-2 text-xs">
        <div>
          <p className="opacity-70">Este inmueble</p>
          <p className="font-semibold">{fmt(score.price_per_m2)}/m²</p>
        </div>
        <div>
          <p className="opacity-70">Promedio {score.scope}</p>
          <p className="font-semibold">{fmt(score.market_avg_m2)}/m²</p>
        </div>
      </div>
      <p className="text-xs opacity-60 mt-2">
        Basado en {score.sample_size} inmuebles similares
      </p>
    </div>
  );
}

export default function PropertyDetail() {
  const { id } = useParams();
  const router = useRouter();
  const [property, setProperty]   = useState(null);
  const [priceScore, setPriceScore] = useState(null);
  const [activeImg, setActiveImg] = useState(0);
  const [loading, setLoading]     = useState(true);

  useEffect(() => {
    getPropertyById(id)
      .then(data => {
        setProperty(data);
        // Cargar score de precio en paralelo
        axios.get(`${API}/price-score/${id}`)
          .then(r => setPriceScore(r.data))
          .catch(() => null);
      })
      .catch(() => setProperty(null))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div className="animate-pulse space-y-4">
      <div className="h-96 bg-slate-800 rounded-xl" />
      <div className="h-8 bg-slate-800 rounded w-2/3" />
      <div className="h-4 bg-slate-800 rounded w-1/3" />
    </div>
  );

  if (!property) return (
    <div className="text-center text-slate-500 py-20">
      Inmueble no encontrado.
      <button onClick={() => router.back()} className="block mx-auto mt-4 text-blue-400">
        ← Volver
      </button>
    </div>
  );

  const images = property.image_urls || [];

  return (
    <div className="max-w-5xl mx-auto">
      <button
        onClick={() => router.back()}
        className="text-slate-400 hover:text-white text-sm mb-4 flex items-center gap-1"
      >
        ← Volver al listado
      </button>

      {/* Galería de fotos */}
      <div className="mb-6">
        <div className="h-96 bg-slate-800 rounded-xl overflow-hidden mb-2">
          {images[activeImg] ? (
            <img
              src={images[activeImg]}
              alt={property.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-slate-500">
              Sin imagen
            </div>
          )}
        </div>
        {images.length > 1 && (
          <div className="flex gap-2 overflow-x-auto pb-1">
            {images.map((img, i) => (
              <button
                key={i}
                onClick={() => setActiveImg(i)}
                className={`flex-shrink-0 w-20 h-16 rounded-lg overflow-hidden border-2 transition-colors ${
                  i === activeImg ? "border-blue-500" : "border-transparent"
                }`}
              >
                <img src={img} alt="" className="w-full h-full object-cover" />
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Info principal */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <h1 className="text-white text-2xl font-bold mb-1">{property.title}</h1>
            <p className="text-slate-400 capitalize">
              {property.neighborhood} · {property.city} · Estrato {property.stratum ?? "—"}
            </p>
            {property.address && (
              <p className="text-slate-500 text-sm mt-1">{property.address}</p>
            )}
          </div>

          {/* Características */}
          <div className="bg-slate-800 rounded-xl p-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: "Área", value: property.area_m2 ? `${property.area_m2} m²` : "—" },
              { label: "Habitaciones", value: property.bedrooms ?? "—" },
              { label: "Baños", value: property.bathrooms ?? "—" },
              { label: "Parqueaderos", value: property.parking ?? "—" },
              { label: "Piso", value: property.floor || "—" },
              { label: "Estrato", value: property.stratum ?? "—" },
              { label: "Precio/m²", value: fmt(property.price_per_m2) },
              { label: "Administración", value: fmt(property.admin_fee) },
            ].map((item) => (
              <div key={item.label} className="text-center">
                <p className="text-slate-400 text-xs mb-1">{item.label}</p>
                <p className="text-white font-semibold text-sm">{item.value}</p>
              </div>
            ))}
          </div>

          {/* Descripción */}
          {property.description && (
            <div className="bg-slate-800 rounded-xl p-4">
              <h2 className="text-white font-semibold mb-3">Descripción</h2>
              <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
                {property.description}
              </p>
            </div>
          )}

          {/* Mapa individual */}
          {property.latitude && property.longitude && (
            <div className="bg-slate-800 rounded-xl overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-700">
                <h2 className="text-white font-semibold text-sm">Ubicación</h2>
              </div>
              <Suspense fallback={<div className="h-64 animate-pulse bg-slate-700" />}>
                <SingleMap
                  latitude={property.latitude}
                  longitude={property.longitude}
                  title={property.title}
                />
              </Suspense>
            </div>
          )}
        </div>

        {/* Panel lateral */}
        <div className="space-y-4">
          <div className="bg-slate-800 rounded-xl p-5">
            <p className="text-blue-400 font-bold text-3xl mb-1">{fmt(property.price)}</p>
            <p className="text-slate-400 text-sm capitalize">
              {property.operation_type} · {property.property_type}
            </p>
            <hr className="border-slate-700 my-4" />
            <p className="text-slate-400 text-xs mb-1">Portal</p>
            <p className="text-white text-sm capitalize mb-4">{property.source_portal}</p>
            <p className="text-slate-400 text-xs mb-1">Publicado</p>
            <p className="text-white text-sm">
              {property.published_at
                ? new Date(property.published_at).toLocaleDateString("es-CO")
                : "—"}
            </p>
            <a
              href={property.url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-5 block w-full text-center bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Ver en {property.source_portal} →
            </a>
          </div>

          <PriceScoreBadge score={priceScore} />
        </div>
      </div>
    </div>
  );
}
