export default function StatsBar({ stats }) {
  if (!stats) return null;

  const fmt = (n) =>
    n ? "$" + Number(n).toLocaleString("es-CO") : "—";

  const items = [
    { label: "Total anuncios",     value: stats.total_listings },
    { label: "Precio promedio",    value: fmt(stats.avg_price) },
    { label: "Mediana de precio",  value: fmt(stats.median_price) },
    { label: "Precio/m² promedio", value: fmt(stats.avg_price_per_m2) },
    { label: "Área promedio",      value: stats.avg_area_m2 ? `${stats.avg_area_m2} m²` : "—" },
    { label: "Precio mínimo",      value: fmt(stats.min_price) },
    { label: "Precio máximo",      value: fmt(stats.max_price) },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-6">
      {items.map((item) => (
        <div key={item.label} className="bg-slate-800 rounded-lg p-3 text-center">
          <p className="text-slate-400 text-xs mb-1">{item.label}</p>
          <p className="text-white font-semibold text-sm">{item.value}</p>
        </div>
      ))}
    </div>
  );
}
