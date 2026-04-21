"use client";

import { useEffect, useRef } from "react";

export default function SingleMap({ latitude, longitude, title }) {
  const mapRef = useRef(null);
  const instanceRef = useRef(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    import("leaflet").then((L) => {
      if (instanceRef.current) {
        instanceRef.current.remove();
      }

      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      const map = L.map(mapRef.current).setView([latitude, longitude], 15);
      instanceRef.current = map;

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      }).addTo(map);

      L.marker([latitude, longitude])
        .addTo(map)
        .bindPopup(title)
        .openPopup();
    });

    return () => {
      if (instanceRef.current) {
        instanceRef.current.remove();
        instanceRef.current = null;
      }
    };
  }, [latitude, longitude, title]);

  return <div ref={mapRef} style={{ height: "280px", width: "100%" }} />;
}
