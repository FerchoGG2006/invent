"use client";

import { useEffect, useState, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import {
  Package, DollarSign, TrendingUp, AlertTriangle,
  BarChart3, ShoppingCart, RefreshCw, Layers,
  Home, Activity, Settings, Search, CreditCard
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import styles from "./page.module.css";

// Types
type Venta = {
  id: number;
  producto_id?: number;
  nombre?: string;
  cantidad: number;
  total: number;
  fecha: string;
  metodo_pago: string;
};

type Producto = {
  id: number;
  nombre: string;
  stock: number;
  stock_minimo: number;
  precio: number;
};

export default function FuturisticDashboard() {
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("home");
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const fetchData = useCallback(async () => {
    try {
      const [ventasRes, productosRes] = await Promise.all([
        supabase.from("ventas").select("*").order("fecha", { ascending: false }),
        supabase.from("productos").select("*"),
      ]);

      setVentas(ventasRes.data || []);
      setProductos(productosRes.data || []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();

    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);

    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [fetchData]);

  // KPIs
  const totalIngresos = ventas.reduce((sum, v) => sum + v.total, 0);
  const totalTransacciones = ventas.length;
  const ticketPromedio = totalTransacciones > 0 ? totalIngresos / totalTransacciones : 0;
  const productosBajoStock = productos.filter((p) => p.stock <= p.stock_minimo);

  // Top productos
  const ventasPorProducto = ventas.reduce((acc: Record<string, number>, v) => {
    const nombre = v.nombre || `Producto #${v.producto_id}`;
    acc[nombre] = (acc[nombre] || 0) + v.cantidad;
    return acc;
  }, {});

  const topProductos = Object.entries(ventasPorProducto)
    .map(([nombre, cantidad]) => ({ nombre, cantidad }))
    .sort((a, b) => b.cantidad - a.cantidad)
    .slice(0, 4);

  const chartData = topProductos.map(p => ({
    name: p.nombre.length > 15 ? p.nombre.substring(0, 15) + '...' : p.nombre,
    ventas: p.cantidad
  }));

  const efectivoTotal = ventas.filter(v => v.metodo_pago === 'Efectivo').reduce((acc, v) => acc + v.total, 0);
  const efectivoPct = totalIngresos > 0 ? (efectivoTotal / totalIngresos) * 100 : 0;

  const generatePath = () => {
    if (ventas.length === 0) return "M 0,50 L 100,50";
    const values = ventas.slice(0, 10).reverse().map(v => v.total);
    const max = Math.max(...values, 1);
    const min = Math.min(...values, 0);
    const range = max - min;
    if (range === 0) return `M 0,30 L 100,30`;
    const points = values.map((val, i) => {
      const x = (i / (values.length - 1)) * 100;
      const y = 90 - (((val - min) / range) * 80);
      return `${x},${y}`;
    });
    return `M ${points[0]} L ${points.slice(1).join(" L ")}`;
  };

  const getPageTitle = () => {
    switch (activeTab) {
      case "home": return "Visión General";
      case "inventory": return "Gestión de Inventario";
      case "sales": return "Historial de Ventas";
      case "stats": return "Analíticas";
      case "settings": return "Configuración";
      default: return "";
    }
  };

  if (loading) {
    return (
      <div className={styles.dashboardLayout} style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div className={styles.spinner} />
      </div>
    );
  }

  return (
    <div className={styles.dashboardLayout}>
      <div className={styles.ambientMesh} />

      <motion.div
        style={{
          position: "fixed", top: 0, left: 0, width: 600, height: 600,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(99, 102, 241, 0.04), transparent 50%)",
          pointerEvents: "none", zIndex: 0,
          x: mousePosition.x - 300, y: mousePosition.y - 300,
        }}
        transition={{ type: "tween", ease: "backOut", duration: 0.1 }}
      />

      <main className={styles.mainContainer}>
        <header className={styles.header}>
          <div className={styles.greeting}>
            <div className={styles.datePill}>
              {format(new Date(), "EEEE, d 'de' MMMM", { locale: es })}
            </div>
            <motion.h1 
              key={activeTab}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {getPageTitle()}
            </motion.h1>
          </div>
          <div className={styles.controls}>
            <div className={styles.controlBtn}><Search size={20} /></div>
            <div className={styles.controlBtn} onClick={fetchData}><RefreshCw size={20} /></div>
          </div>
        </header>

        <AnimatePresence mode="wait">
          {activeTab === "home" && (
            <motion.div
              key="home"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.3 }}
              className={styles.bentoGrid}
            >
              <BentoCard className={styles.span2x2} delay={0.1}>
                <div className={`${styles.cardGlow} ${styles.successGlow}`} />
                <div className={styles.cardIcon} style={{ color: "#34d399", background: "rgba(52, 211, 153, 0.1)" }}>
                  <DollarSign size={24} />
                </div>
                <h3 className={styles.kpiLabel}>INGRESOS TOTALES</h3>
                <div className={styles.kpiValue}>${totalIngresos.toLocaleString("es-CO")}</div>
                <div className={styles.miniChart}>
                  <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
                    <defs>
                      <linearGradient id="glowLine" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="rgba(52, 211, 153, 0.2)" />
                        <stop offset="50%" stopColor="rgba(52, 211, 153, 1)" />
                        <stop offset="100%" stopColor="rgba(52, 211, 153, 0.2)" />
                      </linearGradient>
                      <filter id="blurGlow"><feGaussianBlur stdDeviation="3" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                    </defs>
                    <motion.path initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ duration: 1.5, ease: "easeInOut" }} d={generatePath()} fill="none" stroke="url(#glowLine)" strokeWidth="3" vectorEffect="non-scaling-stroke" filter="url(#blurGlow)" />
                  </svg>
                </div>
              </BentoCard>

              <BentoCard delay={0.2}>
                <div className={styles.cardIcon} style={{ color: "#818cf8", background: "rgba(99, 102, 241, 0.1)" }}><ShoppingCart size={24} /></div>
                <h3 className={styles.kpiLabel}>TRANSACCIONES</h3>
                <div className={styles.kpiValue}>{totalTransacciones}</div>
              </BentoCard>

              <BentoCard delay={0.3}>
                <div className={styles.cardIcon} style={{ color: "#fbcfe8", background: "rgba(244, 114, 182, 0.1)" }}><TrendingUp size={24} /></div>
                <h3 className={styles.kpiLabel}>TICKET PROMEDIO</h3>
                <div className={styles.kpiValue} style={{ fontSize: "36px" }}>${ticketPromedio.toLocaleString("es-CO", { maximumFractionDigits: 0 })}</div>
              </BentoCard>

              <BentoCard className={styles.span2x2} delay={0.4}>
                <h3 className={styles.kpiLabel} style={{ marginBottom: "10px" }}>TOP PRODUCTOS (UNIDADES)</h3>
                <div className={styles.dynamicList}>
                  {topProductos.map((p, i) => (
                    <div key={p.nombre} className={styles.listItem}>
                      <div className={styles.itemLeft}>
                        <div className={styles.itemIcon}>#{i + 1}</div>
                        <span className={styles.itemName}>{p.nombre}</span>
                      </div>
                      <div className={styles.itemRight}>{p.cantidad} uds</div>
                    </div>
                  ))}
                  {topProductos.length === 0 && <div className={styles.emptyState}>Sin ventas registradas</div>}
                </div>
              </BentoCard>

              <BentoCard className={styles.span1x2} delay={0.5}>
                <h3 className={styles.kpiLabel}>DISTRIBUCIÓN PAGOS</h3>
                <div className={styles.ringContainer}>
                  <svg viewBox="0 0 100 100" className={styles.ringSvg}>
                    <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(0,0,0,0.05)" strokeWidth="12" />
                    <motion.circle initial={{ strokeDasharray: "0 251" }} animate={{ strokeDasharray: `${(efectivoPct / 100) * 251} 251` }} transition={{ duration: 1.5, ease: "easeOut", delay: 0.5 }} cx="50" cy="50" r="40" fill="none" stroke="#6366f1" strokeWidth="12" strokeLinecap="round" />
                  </svg>
                  <div className={styles.ringValue}>
                    <span className={styles.ringNumber}>{Math.round(efectivoPct)}%</span>
                    <span className={styles.ringText}>EFECTIVO</span>
                  </div>
                </div>
              </BentoCard>

              <BentoCard className={styles.span1x2} delay={0.6}>
                <div className={`${styles.cardGlow} ${styles.dangerGlow}`} />
                <h3 className={styles.kpiLabel}>ALERTAS CRÍTICAS</h3>
                <div className={styles.dynamicList}>
                  {productosBajoStock.length > 0 ? (
                    productosBajoStock.map((p) => (
                      <div key={p.id} className={styles.listItem} style={{ borderColor: "rgba(248, 113, 113, 0.2)", background: "rgba(248, 113, 113, 0.05)" }}>
                        <div className={styles.itemLeft} style={{flexDirection: 'column', alignItems: 'flex-start', gap: '4px'}}>
                          <span className={styles.itemName} style={{color: '#ef4444'}}>{p.nombre}</span>
                          <span className={styles.itemSub}>Stock: {p.stock} / Mín: {p.stock_minimo}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className={styles.emptyState}><Package size={32} style={{ opacity: 0.5, marginBottom: 10 }} />Inventario Saludable</div>
                  )}
                </div>
              </BentoCard>
            </motion.div>
          )}

          {activeTab === "inventory" && (
            <motion.div
              key="inventory"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={styles.tabContainer}
            >
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '15px' }}>
                <button 
                  style={{ background: '#10b981', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}
                  onClick={() => alert("Funcionalidad de Crear Producto en desarrollo")}
                >
                  + Nuevo Producto
                </button>
              </div>
              <div className={styles.tableWrapper}>
                <table className={styles.modernTable}>
                  <thead>
                    <tr>
                      <th>Producto</th>
                      <th>Precio</th>
                      <th>Stock Actual</th>
                      <th>Estado</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {productos.map(p => (
                      <tr key={p.id}>
                        <td style={{ fontWeight: 700 }}>{p.nombre}</td>
                        <td>${p.precio?.toLocaleString("es-CO") || "0"}</td>
                        <td>{p.stock}</td>
                        <td>
                          {p.stock <= p.stock_minimo ? (
                            <span className={`${styles.badge} ${styles.badgeDanger}`}>Bajo Stock</span>
                          ) : (
                            <span className={`${styles.badge} ${styles.badgeSuccess}`}>Óptimo</span>
                          )}
                        </td>
                        <td>
                          <button style={{ background: 'transparent', border: 'none', color: '#6366f1', cursor: 'pointer', marginRight: '10px' }}>Editar</button>
                          <button style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer' }}>Eliminar</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}

          {activeTab === "sales" && (
            <motion.div
              key="sales"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={styles.tabContainer}
            >
              <div className={styles.tableWrapper}>
                <table className={styles.modernTable}>
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Producto</th>
                      <th>Cantidad</th>
                      <th>Método de Pago</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ventas.map(v => (
                      <tr key={v.id}>
                        <td style={{ color: '#64748b' }}>{format(new Date(v.fecha), "dd/MM/yyyy HH:mm")}</td>
                        <td style={{ fontWeight: 700 }}>{v.nombre || `Prod #${v.producto_id}`}</td>
                        <td>{v.cantidad}</td>
                        <td>
                          <span className={`${styles.badge} ${v.metodo_pago === 'Efectivo' ? styles.badgeSuccess : styles.badgeInfo}`}>
                            {v.metodo_pago}
                          </span>
                        </td>
                        <td style={{ fontWeight: 800 }}>${v.total.toLocaleString("es-CO")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}

          {activeTab === "stats" && (
            <motion.div
              key="stats"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className={styles.tabContainer}
              style={{ display: "flex", flexDirection: "column", gap: "20px" }}
            >
              <div style={{ background: "rgba(255, 255, 255, 0.7)", backdropFilter: "blur(20px)", borderRadius: "24px", padding: "30px", border: "1px solid rgba(255, 255, 255, 0.4)", boxShadow: "0 10px 40px -10px rgba(0,0,0,0.05)" }}>
                <h2 style={{ fontSize: "20px", color: "#0f172a", marginBottom: "20px", fontWeight: 800 }}>Productos Más Vendidos</h2>
                <div style={{ width: '100%', height: '400px', position: 'relative' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0,0,0,0.05)" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                      <Tooltip 
                        cursor={{ fill: 'rgba(99, 102, 241, 0.05)' }}
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)' }}
                      />
                      <Bar dataKey="ventas" fill="#6366f1" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === "settings" && (
            <motion.div
              key="settings"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className={styles.tabContainer}
              style={{ alignItems: "center", justifyContent: "center", padding: "100px 0" }}
            >
              <div className={styles.emptyState}>
                <Layers size={64} style={{ opacity: 0.2, marginBottom: 20 }} />
                <h2 style={{ fontSize: "24px", color: "#0f172a", marginBottom: "8px" }}>Próximamente</h2>
                <p>La configuración del sistema estará disponible en la versión final.</p>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </main>

      <div className={styles.dockWrapper}>
        <motion.div 
          className={styles.dock}
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 20, delay: 0.8 }}
        >
          <DockIcon active={activeTab === 'home'} onClick={() => setActiveTab('home')} icon={<Home />} />
          <DockIcon active={activeTab === 'inventory'} onClick={() => setActiveTab('inventory')} icon={<Package />} />
          <DockIcon active={activeTab === 'sales'} onClick={() => setActiveTab('sales')} icon={<CreditCard />} />
          <DockIcon active={activeTab === 'stats'} onClick={() => setActiveTab('stats')} icon={<Activity />} />
          <div style={{ width: 1, height: 32, background: "rgba(0,0,0,0.1)", margin: "8px 4px" }} />
          <DockIcon active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} icon={<Settings />} />
        </motion.div>
      </div>
    </div>
  );
}

function BentoCard({ children, className = "", delay = 0 }: { children: React.ReactNode, className?: string, delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 200, damping: 20, delay }}
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      className={`${styles.bentoCard} ${className}`}
    >
      {children}
    </motion.div>
  );
}

function DockIcon({ icon, active, onClick }: { icon: React.ReactNode, active: boolean, onClick: () => void }) {
  return (
    <motion.button 
      className={`${styles.dockIcon} ${active ? styles.dockIconActive : ""}`}
      onClick={onClick}
      whileHover={{ y: -5, scale: 1.2 }}
      whileTap={{ scale: 0.9 }}
      transition={{ type: "spring", stiffness: 400, damping: 15 }}
    >
      {icon}
      {active && (
        <motion.div 
          layoutId="dockIndicator"
          className={styles.dockIndicator}
          initial={false}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        />
      )}
    </motion.button>
  );
}
