"use client";

import { useEffect, useRef } from "react";

export default function PropertyMap({ properties }) {
  const mapRef = useRef(null);
  const instanceRef = useRef(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    // Cargar Leaflet dinámicamente
    import("leaflet").then((L) => {
      // Evitar doble inicialización
      if (instanceRef.current) {
        instanceRef.current.remove();
      }

      // Fix icono por defecto de Leaflet con Next.js
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      // Filtrar propiedades con coordenadas válidas
      const valid = properties.filter(
        (p) => p.latitude && p.longitude &&
               Math.abs(p.latitude) < 90 && Math.abs(p.longitude) < 180
      );

      if (valid.length === 0) return;

      // Centro del mapa en el primer inmueble
      const map = L.map(mapRef.current).setView(
        [valid[0].latitude, valid[0].longitude], 12
      );

      instanceRef.current = map;

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      }).addTo(map);

      // Agregar marcadores
      valid.forEach((p) => {
        const fmt = (n) => n ? "$" + Number(n).toLocaleString("es-CO") : "—";
        const popup = `
          <div style="min-width:200px">
            <strong style="font-size:13px">${p.title}</strong><br/>
            <span style="color:#3b82f6;font-weight:bold">${fmt(p.price)}</span><br/>
            <small>${p.area_m2 ?? "—"} m² · ${p.bedrooms ?? 0} hab · Estrato ${p.stratum ?? "—"}</small><br/>
            <small>${p.neighborhood}</small><br/>
            <a href="${p.url}" target="_blank" style="color:#3b82f6">Ver inmueble →</a>
          </div>
        `;
        L.marker([p.latitude, p.longitude])
          .addTo(map)
          .bindPopup(popup);
      });
    });

    return () => {
      if (instanceRef.current) {
        instanceRef.current.remove();
        instanceRef.current = null;
      }
    };
  }, [properties]);

  return (
    <div className="bg-slate-800 rounded-xl overflow-hidden mb-6">
      <div className="px-4 py-3 border-b border-slate-700">
        <h2 className="text-white font-semibold text-sm">
          Mapa de inmuebles ({properties.filter(p => p.latitude && p.longitude).length} georreferenciados)
        </h2>
      </div>
      <div ref={mapRef} style={{ height: "400px", width: "100%" }} />
    </div>
  );
}
