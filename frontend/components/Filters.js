"use client";

export default function Filters({ filters, onChange, onSearch }) {
  const handle = (e) => onChange({ ...filters, [e.target.name]: e.target.value });

  return (
    <div className="bg-slate-800 rounded-xl p-4 mb-6 flex flex-wrap gap-3 items-end">
      <div className="flex flex-col gap-1">
        <label className="text-slate-400 text-xs">Ciudad</label>
        <select
          name="city"
          value={filters.city}
          onChange={handle}
          className="bg-slate-700 text-white rounded px-3 py-2 text-sm"
        >
          <option value="bogota">Bogotá</option>
          <option value="medellin">Medellín</option>
          <option value="cali">Cali</option>
          <option value="barranquilla">Barranquilla</option>
          <option value="bucaramanga">Bucaramanga</option>
          <option value="pereira">Pereira</option>
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-slate-400 text-xs">Operación</label>
        <select
          name="operation_type"
          value={filters.operation_type}
          onChange={handle}
          className="bg-slate-700 text-white rounded px-3 py-2 text-sm"
        >
          <option value="venta">Venta</option>
          <option value="arriendo">Arriendo</option>
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-slate-400 text-xs">Tipo</label>
        <select
          name="property_type"
          value={filters.property_type}
          onChange={handle}
          className="bg-slate-700 text-white rounded px-3 py-2 text-sm"
        >
          <option value="">Todos</option>
          <option value="apartamento">Apartamento</option>
          <option value="casa">Casa</option>
          <option value="lote">Lote</option>
          <option value="oficina">Oficina</option>
          <option value="local_comercial">Local</option>
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-slate-400 text-xs">Habitaciones</label>
        <select
          name="bedrooms"
          value={filters.bedrooms}
          onChange={handle}
          className="bg-slate-700 text-white rounded px-3 py-2 text-sm"
        >
          <option value="">Todas</option>
          {[1, 2, 3, 4, 5].map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-slate-400 text-xs">Precio mín</label>
        <input
          name="min_price"
          type="number"
          value={filters.min_price}
          onChange={handle}
          placeholder="0"
          className="bg-slate-700 text-white rounded px-3 py-2 text-sm w-32"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-slate-400 text-xs">Precio máx</label>
        <input
          name="max_price"
          type="number"
          value={filters.max_price}
          onChange={handle}
          placeholder="Sin límite"
          className="bg-slate-700 text-white rounded px-3 py-2 text-sm w-32"
        />
      </div>

      <button
        onClick={onSearch}
        className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded text-sm font-medium transition-colors"
      >
        Buscar
      </button>
    </div>
  );
}
