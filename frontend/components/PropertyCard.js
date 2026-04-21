import Link from "next/link";

export default function PropertyCard({ property }) {
  const fmt = (n) => n ? "$" + Number(n).toLocaleString("es-CO") : "—";
  const img = property.image_urls?.[0];

  return (
    <Link
      href={`/properties/${property.id}`}
      className="bg-slate-800 rounded-xl overflow-hidden hover:ring-2 hover:ring-blue-500 transition-all block"
    >
      <div className="h-44 bg-slate-700 overflow-hidden">
        {img ? (
          <img src={img} alt={property.title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-500 text-sm">
            Sin imagen
          </div>
        )}
      </div>

      <div className="p-4">
        <p className="text-white font-semibold text-sm leading-tight mb-1 line-clamp-2">
          {property.title}
        </p>
        <p className="text-slate-400 text-xs mb-3 capitalize">
          {property.neighborhood} · Estrato {property.stratum ?? "—"}
        </p>

        <p className="text-blue-400 font-bold text-lg mb-2">{fmt(property.price)}</p>

        <div className="flex gap-3 text-slate-400 text-xs">
          <span>{property.area_m2} m²</span>
          {property.bedrooms > 0 && <span>{property.bedrooms} hab</span>}
          {property.bathrooms > 0 && <span>{property.bathrooms} baños</span>}
          {property.parking > 0 && <span>{property.parking} parq</span>}
        </div>

        <p className="text-slate-500 text-xs mt-2">
          {fmt(property.price_per_m2)}/m² · {property.source_portal}
        </p>
      </div>
    </Link>
  );
}
