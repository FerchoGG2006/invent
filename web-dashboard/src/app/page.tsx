"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { format, subDays, startOfMonth, startOfWeek } from "date-fns";
import { es } from "date-fns/locale";
import { Package, DollarSign, TrendingUp, AlertTriangle, Users, ArrowUpRight } from "lucide-react";
import clsx from "clsx";

// Types
type Venta = {
  id: number;
  producto_id?: number;
  nombre?: string;
  cantidad: number;
  precio_unitario: number;
  total: number;
  fecha: string;
  metodo_pago: string;
};

type Producto = {
  id: number;
  nombre: string;
  stock: number;
  stock_minimo: number;
};

export default function Dashboard() {
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"todo" | "hoy" | "semana" | "mes">("mes");

  useEffect(() => {
    fetchData();
    
    // Subscribe to realtime changes
    const ventasSubscription = supabase
      .channel('ventas_changes')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'ventas' }, () => {
        fetchData();
      })
      .subscribe();

    const productosSubscription = supabase
      .channel('productos_changes')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'productos' }, () => {
        fetchData();
      })
      .subscribe();

    return () => {
      supabase.removeChannel(ventasSubscription);
      supabase.removeChannel(productosSubscription);
    };
  }, []);

  const fetchData = async () => {
    try {
      const { data: ventasData, error: ventasError } = await supabase
        .from("ventas")
        .select("*")
        .order("fecha", { ascending: false });

      const { data: productosData, error: productosError } = await supabase
        .from("productos")
        .select("id, nombre, stock, stock_minimo");

      if (ventasError) throw ventasError;
      if (productosError) throw productosError;

      setVentas(ventasData || []);
      setProductos(productosData || []);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  // Filtrado de ventas
  const filteredVentas = ventas.filter((v) => {
    const fecha = new Date(v.fecha);
    const hoy = new Date();
    switch (filter) {
      case "hoy":
        return fecha >= new Date(hoy.setHours(0, 0, 0, 0));
      case "semana":
        return fecha >= startOfWeek(hoy, { weekStartsOn: 1 });
      case "mes":
        return fecha >= startOfMonth(hoy);
      default:
        return true;
    }
  });

  // KPIs
  const totalIngresos = filteredVentas.reduce((sum, v) => sum + v.total, 0);
  const totalVentas = filteredVentas.length;
  const productosBajoStock = productos.filter((p) => p.stock <= p.stock_minimo).length;

  // Chart Data: Tendencia de Ventas (Agrupado por día)
  const ventasPorDia = filteredVentas.reduce((acc: any, v) => {
    const dia = format(new Date(v.fecha), "dd MMM", { locale: es });
    if (!acc[dia]) acc[dia] = 0;
    acc[dia] += v.total;
    return acc;
  }, {});
  
  const chartDataVentas = Object.keys(ventasPorDia).map((dia) => ({
    name: dia,
    Total: ventasPorDia[dia],
  })).reverse(); // Para que el más antiguo quede primero (dependiendo de cómo se ordenó)

  // Top Productos Data
  const ventasPorProducto = filteredVentas.reduce((acc: any, v) => {
    const nombre = v.nombre || (v.producto_id ? `Producto #${v.producto_id}` : "Producto Desconocido");
    if (!acc[nombre]) acc[nombre] = 0;
    acc[nombre] += v.cantidad;
    return acc;
  }, {});

  const topProductosData = Object.keys(ventasPorProducto)
    .map(key => ({ nombre: key, cantidad: ventasPorProducto[key] }))
    .sort((a, b) => b.cantidad - a.cantidad)
    .slice(0, 5);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-4 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Panel Web POS</h1>
            <p className="text-slate-500 text-sm mt-1">Monitoreo en tiempo real de tu negocio</p>
          </div>
          <div className="flex bg-slate-100 p-1 rounded-lg">
            {["todo", "hoy", "semana", "mes"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as any)}
                className={clsx(
                  "px-4 py-2 text-sm font-medium rounded-md capitalize transition-all",
                  filter === f ? "bg-white text-indigo-600 shadow-sm" : "text-slate-500 hover:text-slate-700"
                )}
              >
                {f}
              </button>
            ))}
          </div>
        </header>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <KpiCard title="Ingresos Totales" value={`$${totalIngresos.toLocaleString()}`} icon={<DollarSign size={24} />} trend="+12%" color="text-emerald-600" bg="bg-emerald-100" />
          <KpiCard title="Transacciones" value={totalVentas.toString()} icon={<TrendingUp size={24} />} trend="+5%" color="text-indigo-600" bg="bg-indigo-100" />
          <KpiCard title="Alertas de Stock" value={productosBajoStock.toString()} icon={<AlertTriangle size={24} />} color={productosBajoStock > 0 ? "text-rose-600" : "text-slate-500"} bg={productosBajoStock > 0 ? "bg-rose-100" : "bg-slate-100"} />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Main Chart */}
          <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
            <h2 className="text-lg font-bold text-slate-800 mb-6">Tendencia de Ingresos</h2>
            <div className="h-72 w-full">
              {chartDataVentas.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartDataVentas}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} tickFormatter={(val) => `$${val}`} dx={-10} />
                    <RechartsTooltip 
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      formatter={(value) => [`$${Number(value).toLocaleString()}`, "Ingresos"]}
                    />
                    <Line type="monotone" dataKey="Total" stroke="#4f46e5" strokeWidth={3} dot={{r: 4, strokeWidth: 2, fill: "#fff"}} activeDot={{r: 6}} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-slate-400">No hay datos en este período</div>
              )}
            </div>
          </div>

          {/* Top Products */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col">
            <h2 className="text-lg font-bold text-slate-800 mb-6">Productos Más Vendidos</h2>
            <div className="flex-1 flex flex-col justify-center">
               {topProductosData.length > 0 ? (
                 <ResponsiveContainer width="100%" height={240}>
                   <BarChart data={topProductosData} layout="vertical" margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                     <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                     <XAxis type="number" hide />
                     <YAxis dataKey="nombre" type="category" axisLine={false} tickLine={false} tick={{fill: '#475569', fontSize: 11}} width={120} />
                     <RechartsTooltip cursor={{fill: '#f1f5f9'}} contentStyle={{ borderRadius: '8px', border: 'none' }} />
                     <Bar dataKey="cantidad" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={24} />
                   </BarChart>
                 </ResponsiveContainer>
               ) : (
                 <div className="text-center text-slate-400 py-10">No hay ventas registradas</div>
               )}
            </div>
          </div>
          
        </div>

        {/* Recent Transactions Table */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <h2 className="text-lg font-bold text-slate-800">Transacciones Recientes</h2>
            <button className="text-indigo-600 text-sm font-medium flex items-center hover:text-indigo-800 transition-colors">
              Ver todas <ArrowUpRight size={16} className="ml-1" />
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                  <th className="p-4 font-semibold">ID</th>
                  <th className="p-4 font-semibold">Fecha</th>
                  <th className="p-4 font-semibold">Método</th>
                  <th className="p-4 font-semibold text-right">Total</th>
                </tr>
              </thead>
              <tbody className="text-sm divide-y divide-slate-100">
                {filteredVentas.slice(0, 8).map((v) => (
                  <tr key={v.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="p-4 font-medium text-slate-700">#{v.id}</td>
                    <td className="p-4 text-slate-500">{format(new Date(v.fecha), "dd MMM, HH:mm", { locale: es })}</td>
                    <td className="p-4">
                      <span className={clsx(
                        "px-2.5 py-1 rounded-full text-xs font-medium",
                        v.metodo_pago === 'Efectivo' ? "bg-emerald-100 text-emerald-700" : 
                        v.metodo_pago === 'Transferencia' ? "bg-blue-100 text-blue-700" : 
                        "bg-amber-100 text-amber-700"
                      )}>
                        {v.metodo_pago}
                      </span>
                    </td>
                    <td className="p-4 font-bold text-slate-900 text-right">${v.total.toLocaleString()}</td>
                  </tr>
                ))}
                {filteredVentas.length === 0 && (
                  <tr>
                    <td colSpan={4} className="p-8 text-center text-slate-400">No hay transacciones recientes.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}

function KpiCard({ title, value, icon, trend, color, bg }: { title: string, value: string, icon: any, trend?: string, color: string, bg: string }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between hover:shadow-md transition-shadow">
      <div>
        <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
        <h3 className="text-3xl font-bold text-slate-800">{value}</h3>
        {trend && (
          <p className="text-xs font-medium text-emerald-600 mt-2 flex items-center">
            <TrendingUp size={14} className="mr-1" /> {trend} en este período
          </p>
        )}
      </div>
      <div className={`${bg} ${color} p-4 rounded-xl`}>
        {icon}
      </div>
    </div>
  )
}
