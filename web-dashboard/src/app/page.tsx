"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/utils/supabase/client";
import styles from "./page.module.css";

// Definición de Interfaces
interface Producto {
  id: number;
  codigo: string | null;
  nombre: string;
  categoria: string | null;
  precio_venta: number;
  stock: number;
  stock_minimo: number;
  updated_at?: string;
}

interface Venta {
  id: number;
  codigo: string | null;
  nombre: string;
  cantidad: number;
  precio_unitario: number;
  total: number;
  fecha: string | null;
  metodo_pago: string | null;
  descuento: number;
  cliente_nombre: string | null;
  impuestos: number;
}

// Datos de demostración en caso de que no haya conexión a Supabase o base de datos vacía
const MOCK_PRODUCTOS: Producto[] = [
  { id: 1, codigo: "PROD-CERA", nombre: "Cera Modeladora Premium (80g)", categoria: "Fijación", precio_venta: 45000, stock: 15, stock_minimo: 5 },
  { id: 2, codigo: "PROD-ACEITE", nombre: "Aceite de Barba de Eucalipto", categoria: "Cuidado Barba", precio_venta: 60000, stock: 2, stock_minimo: 5 },
  { id: 3, codigo: "PROD-SHAMP", nombre: "Shampoo Refrescante Menta (250ml)", categoria: "Cuidado Capilar", precio_venta: 35000, stock: 24, stock_minimo: 5 },
  { id: 4, codigo: "PROD-GEL", nombre: "Gel Afeitar Hidratante Transparente", categoria: "Afeitado", precio_venta: 28000, stock: 0, stock_minimo: 3 },
  { id: 5, codigo: "PROD-NAVAJA", nombre: "Navaja Profesional de Acero Gold", categoria: "Herramientas", precio_venta: 120000, stock: 6, stock_minimo: 2 },
  { id: 6, codigo: "PROD-TONICO", nombre: "Tónico Estimulante de Crecimiento", categoria: "Tratamientos", precio_venta: 95000, stock: 8, stock_minimo: 4 }
];

const MOCK_VENTAS: Venta[] = [
  { id: 101, codigo: "PROD-CERA", nombre: "Cera Modeladora Premium (80g)", cantidad: 2, precio_unitario: 45000, total: 90000, fecha: new Date(Date.now() - 3600000).toISOString(), metodo_pago: "Efectivo", descuento: 0, cliente_nombre: "Luis Gomez", impuestos: 0 },
  { id: 102, codigo: "PROD-ACEITE", nombre: "Aceite de Barba de Eucalipto", cantidad: 1, precio_unitario: 60000, total: 60000, fecha: new Date(Date.now() - 10800000).toISOString(), metodo_pago: "Transferencia", descuento: 0, cliente_nombre: "Andres Ruiz", impuestos: 0 },
  { id: 103, codigo: "PROD-NAVAJA", nombre: "Navaja Profesional de Acero Gold", cantidad: 1, precio_unitario: 120000, total: 120000, fecha: new Date(Date.now() - 86400000).toISOString(), metodo_pago: "Transferencia", descuento: 0, cliente_nombre: "Felipe Soto", impuestos: 0 },
  { id: 104, codigo: "PROD-SHAMP", nombre: "Shampoo Refrescante Menta (250ml)", cantidad: 3, precio_unitario: 35000, total: 105000, fecha: new Date(Date.now() - 172800000).toISOString(), metodo_pago: "Efectivo", descuento: 5000, cliente_nombre: "Mauricio Ortiz", impuestos: 0 },
  { id: 105, codigo: "PROD-TONICO", nombre: "Tónico Estimulante de Crecimiento", cantidad: 1, precio_unitario: 95000, total: 95000, fecha: new Date(Date.now() - 259200000).toISOString(), metodo_pago: "Efectivo", descuento: 0, cliente_nombre: "Carlos Perez", impuestos: 0 },
  { id: 106, codigo: "PROD-GEL", nombre: "Gel Afeitar Hidratante Transparente", cantidad: 2, precio_unitario: 28000, total: 56000, fecha: new Date(Date.now() - 345600000).toISOString(), metodo_pago: "Efectivo", descuento: 0, cliente_nombre: "Juan Perez", impuestos: 0 }
];

export default function Dashboard() {
  const supabase = createClient();

  // Estados de Autenticación
  const [session, setSession] = useState<any>(null);
  const [loadingSession, setLoadingSession] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [authError, setAuthError] = useState("");
  const [authSuccess, setAuthSuccess] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);

  // Estados de Datos
  const [productos, setProductos] = useState<Producto[]>([]);
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [loadingData, setLoadingData] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // Estados de Control e Interfaz
  const [activeTab, setActiveTab] = useState<"dashboard" | "inventory" | "sales">("dashboard");
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState<"all" | "today" | "week" | "month">("all");

  // Verificar la sesión de usuario
  useEffect(() => {
    async function checkSession() {
      try {
        const { data: { session: activeSession } } = await supabase.auth.getSession();
        setSession(activeSession);
      } catch (err) {
        console.error("Error al obtener sesión:", err);
      } finally {
        setLoadingSession(false);
      }
    }
    checkSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Cargar datos al iniciar sesión o cambiar a modo demo
  useEffect(() => {
    if (session || isDemoMode) {
      fetchData();
    }
  }, [session, isDemoMode]);

  // Cargar datos desde Supabase (o mock de respaldo)
  async function fetchData() {
    setLoadingData(true);
    setRefreshing(true);
    
    if (isDemoMode) {
      setTimeout(() => {
        setProductos(MOCK_PRODUCTOS);
        setVentas(MOCK_VENTAS);
        setLoadingData(false);
        setRefreshing(false);
      }, 500);
      return;
    }

    try {
      // 1. Obtener Productos
      const { data: prods, error: prodErr } = await supabase
        .from("productos")
        .select("*")
        .order("nombre", { ascending: true });

      // 2. Obtener Ventas
      const { data: vts, error: salesErr } = await supabase
        .from("ventas")
        .select("*")
        .order("fecha", { ascending: false });

      if (prodErr || salesErr) {
        console.warn("Fallo al obtener datos de Supabase, usando respaldo local. Error:", prodErr || salesErr);
        // Si no hay tablas creadas o hay error RLS/conexión, usamos el Mock
        setProductos(MOCK_PRODUCTOS);
        setVentas(MOCK_VENTAS);
      } else {
        setProductos(prods || []);
        setVentas(vts || []);
      }
    } catch (err) {
      console.error("Excepción al consultar Supabase, cargando Mock:", err);
      setProductos(MOCK_PRODUCTOS);
      setVentas(MOCK_VENTAS);
    } finally {
      setLoadingData(false);
      setRefreshing(false);
    }
  }

  // Manejar Login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    setAuthSuccess("");
    setAuthLoading(true);

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        setAuthError(error.message || "Credenciales incorrectas.");
      } else {
        setSession(data.session);
        setIsDemoMode(false);
      }
    } catch (err) {
      setAuthError("Ocurrió un error inesperado al iniciar sesión.");
    } finally {
      setAuthLoading(false);
    }
  };

  // Manejar Registro
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    setAuthSuccess("");
    setAuthLoading(true);

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      });

      if (error) {
        setAuthError(error.message || "Error al registrarse.");
      } else {
        setAuthSuccess("¡Registro exitoso! Por favor inicia sesión con tu cuenta.");
        setIsRegistering(false);
      }
    } catch (err) {
      setAuthError("Ocurrió un error inesperado al registrar.");
    } finally {
      setAuthLoading(false);
    }
  };

  // Salir
  const handleLogout = async () => {
    if (isDemoMode) {
      setIsDemoMode(false);
      setSession(null);
      return;
    }
    await supabase.auth.signOut();
    setSession(null);
  };

  // Cambiar a Modo Demo
  const handleDemoMode = () => {
    setIsDemoMode(true);
    setSession({ user: { email: "demo@barberiapos.com" } });
  };

  if (loadingSession) {
    return (
      <div className={styles.loginContainer}>
        <div className={styles.loginCard} style={{ alignItems: "center", justifyContent: "center" }}>
          <div className={styles.refreshing} style={{ fontSize: "40px" }}>🌀</div>
          <p style={{ marginTop: "16px", fontWeight: "600", color: "#64748b" }}>Cargando Panel...</p>
        </div>
      </div>
    );
  }

  // Si no está autenticado, mostrar formulario de Login/Registro
  if (!session) {
    return (
      <div className={styles.loginContainer}>
        <div className={styles.loginCard}>
          <div className={styles.loginHeader}>
            <div className={styles.loginIcon}>💈</div>
            <h2>BARBERÍA POS</h2>
            <p>Panel Administrativo en la Nube</p>
          </div>

          {authError && <div className={`${styles.alertBox} ${styles.alertError}`}>⚠️ {authError}</div>}
          {authSuccess && <div className={`${styles.alertBox} ${styles.alertSuccess}`}>✔️ {authSuccess}</div>}

          <form onSubmit={isRegistering ? handleRegister : handleLogin}>
            <div className={styles.formGroup}>
              <label className={styles.formLabel}>Correo Electrónico</label>
              <input
                type="email"
                required
                className={styles.formInput}
                placeholder="ejemplo@barberia.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.formLabel}>Contraseña</label>
              <input
                type="password"
                required
                minLength={6}
                className={styles.formInput}
                placeholder="******"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button type="submit" className={styles.submitBtn} disabled={authLoading}>
              {authLoading ? "Cargando..." : isRegistering ? "Crear Cuenta de Admin" : "Iniciar Sesión"}
            </button>
          </form>

          <div className={styles.toggleAuthMode}>
            {isRegistering ? "¿Ya tienes una cuenta?" : "¿No tienes cuenta de Supabase?"}
            <button
              className={styles.toggleAuthBtn}
              onClick={() => {
                setIsRegistering(!isRegistering);
                setAuthError("");
                setAuthSuccess("");
              }}
            >
              {isRegistering ? "Inicia Sesión" : "Regístrate"}
            </button>
          </div>

          <div className={styles.demoDivider}>o explora la app</div>

          <button onClick={handleDemoMode} className={styles.demoBtn}>
            Ver en Modo Demo
          </button>
        </div>
      </div>
    );
  }

  // --- CÁLCULO DE MÉTRICAS ---
  const totalVentasValor = ventas.reduce((acc, v) => acc + (v.total || 0), 0);
  const cantVentasVal = ventas.length;
  const cantProductosVal = productos.length;
  const bajoStockVal = productos.filter((p) => (p.stock || 0) <= (p.stock_minimo || 0)).length;

  // --- FILTRADO DE PRODUCTOS ---
  const categoriesSet = new Set(productos.map((p) => p.categoria || "Sin categoría"));
  const categoriesList = Array.from(categoriesSet);

  const filteredProductos = productos.filter((p) => {
    const matchSearch = p.nombre.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (p.codigo && p.codigo.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchCategory = categoryFilter === "all" || p.categoria === categoryFilter;
    return matchSearch && matchCategory;
  });

  // --- FILTRADO DE VENTAS ---
  const filteredVentas = ventas.filter((v) => {
    if (dateFilter === "all") return true;
    const vDate = v.fecha ? new Date(v.fecha) : new Date();
    const now = new Date();
    if (dateFilter === "today") {
      return vDate.toDateString() === now.toDateString();
    }
    if (dateFilter === "week") {
      const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      return vDate >= oneWeekAgo;
    }
    if (dateFilter === "month") {
      return vDate.getMonth() === now.getMonth() && vDate.getFullYear() === now.getFullYear();
    }
    return true;
  });

  // --- MÉTODO DE PAGO ---
  const cashSales = ventas.filter((v) => v.metodo_pago === "Efectivo").reduce((sum, v) => sum + v.total, 0);
  const cardSales = ventas.filter((v) => v.metodo_pago === "Transferencia" || v.metodo_pago === "Tarjeta").reduce((sum, v) => sum + v.total, 0);
  const totalMetodos = cashSales + cardSales;
  const cashPct = totalMetodos > 0 ? Math.round((cashSales / totalMetodos) * 100) : 50;
  const cardPct = totalMetodos > 0 ? 100 - cashPct : 50;

  // --- FORMATO DE MONEDA ---
  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(val);
  };

  // --- FORMATO DE FECHA ---
  const formatFecha = (isoString: string | null) => {
    if (!isoString) return "-";
    const date = new Date(isoString);
    return date.toLocaleDateString("es-ES", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className={styles.dashboardLayout}>
      {/* SIDEBAR */}
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <div className={styles.brandIcon}>💈</div>
          <span className={styles.brandName}>Barbería POS</span>
        </div>

        <nav className={styles.navigation}>
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`${styles.navItem} ${activeTab === "dashboard" ? styles.navItemActive : ""}`}
          >
            📊 Resumen General
          </button>
          <button
            onClick={() => setActiveTab("inventory")}
            className={`${styles.navItem} ${activeTab === "inventory" ? styles.navItemActive : ""}`}
          >
            📦 Inventario de Stock
          </button>
          <button
            onClick={() => setActiveTab("sales")}
            className={`${styles.navItem} ${activeTab === "sales" ? styles.navItemActive : ""}`}
          >
            💸 Registro de Ventas
          </button>
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.userInfo}>
            <span className={styles.userEmail}>{session?.user?.email}</span>
            <span className={styles.userRole}>
              {isDemoMode ? "📝 Modo Demostración" : "🔐 Administrador Sincronizado"}
            </span>
          </div>
          <button onClick={handleLogout} className={styles.logoutBtn}>
            🚪 Cerrar Sesión
          </button>
        </div>
      </aside>

      {/* MAIN CONTAINER */}
      <main className={styles.mainContainer}>
        {/* HEADER */}
        <header className={styles.topHeader}>
          <div className={styles.titleArea}>
            <h1>
              {activeTab === "dashboard" && "Resumen del Negocio"}
              {activeTab === "inventory" && "Control de Inventario"}
              {activeTab === "sales" && "Registro de Ventas"}
            </h1>
            <p>
              {activeTab === "dashboard" && "Monitorea las ventas, productos populares e inventario de tu barbería."}
              {activeTab === "inventory" && "Revisa existencias, categorías y alertas de stock de productos."}
              {activeTab === "sales" && "Listado detallado de todas las transacciones sincronizadas de tu caja."}
            </p>
          </div>

          <div className={styles.actionsArea}>
            <div className={styles.syncIndicator}>
              <span className={isDemoMode ? styles.syncGray : styles.syncGreen}>●</span>
              {isDemoMode ? "Respaldo Offline" : "Nube Supabase"}
            </div>
            <button onClick={fetchData} className={styles.refreshBtn} disabled={loadingData}>
              <span className={refreshing ? styles.refreshing : ""}>🔄</span> Actualizar
            </button>
          </div>
        </header>

        {/* METRICS / KPIS */}
        <section className={styles.kpiGrid}>
          <div className={styles.kpiCard}>
            <div className={styles.kpiLabel}>Ventas Totales</div>
            <div className={styles.kpiValue}>{formatCurrency(totalVentasValor)}</div>
            <div className={styles.kpiChange} style={{ color: "#10b981" }}>
              En caja local
            </div>
            <div className={`${styles.kpiBadge} ${styles.successBadge}`}>💵</div>
          </div>

          <div className={styles.kpiCard}>
            <div className={styles.kpiLabel}>Transacciones</div>
            <div className={styles.kpiValue}>{cantVentasVal}</div>
            <div className={styles.kpiChange} style={{ color: "#4f46e5" }}>
              Total boletas emitidas
            </div>
            <div className={`${styles.kpiBadge} ${styles.primaryBadge}`}>📝</div>
          </div>

          <div className={styles.kpiCard}>
            <div className={styles.kpiLabel}>Productos en Stock</div>
            <div className={styles.kpiValue}>{cantProductosVal}</div>
            <div className={styles.kpiChange} style={{ color: "#64748b" }}>
              Diferentes ítems
            </div>
            <div className={`${styles.kpiBadge} ${styles.warningBadge}`}>📦</div>
          </div>

          <div className={styles.kpiCard}>
            <div className={styles.kpiLabel}>Bajo Stock</div>
            <div className={styles.kpiValue} style={{ color: bajoStockVal > 0 ? "#ef4444" : "inherit" }}>
              {bajoStockVal}
            </div>
            <div className={styles.kpiChange} style={{ color: bajoStockVal > 0 ? "#ef4444" : "#10b981" }}>
              {bajoStockVal > 0 ? "Requiere reposición inmediata" : "Inventario al día"}
            </div>
            <div className={`${styles.kpiBadge} ${styles.dangerBadge}`}>⚠️</div>
          </div>
        </section>

        {/* TAB CONTENTS */}

        {/* TAB 1: DASHBOARD / GENERAL */}
        {activeTab === "dashboard" && (
          <div className={styles.detailsGrid}>
            {/* VENTAS POR DÍA (GRÁFICO SVG) */}
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h3 className={styles.cardTitle}>Evolución de Ingresos Recientes</h3>
                <span style={{ fontSize: "12px", color: "#64748b" }}>Últimas ventas sincronizadas</span>
              </div>
              <div className={styles.chartContainer}>
                {ventas.length === 0 ? (
                  <div className={styles.emptyState}>
                    <span className={styles.emptyStateIcon}>📈</span>
                    <p className={styles.emptyStateTitle}>Sin transacciones</p>
                    <p>Las ventas que realices en el POS aparecerán aquí.</p>
                  </div>
                ) : (
                  <svg className={styles.chartContainerSvg} viewBox="0 0 500 200" preserveAspectRatio="none">
                    {/* Grillas de fondo */}
                    <line x1="0" y1="50" x2="500" y2="50" stroke="#f1f5f9" strokeWidth="1" />
                    <line x1="0" y1="100" x2="500" y2="100" stroke="#f1f5f9" strokeWidth="1" />
                    <line x1="0" y1="150" x2="500" y2="150" stroke="#f1f5f9" strokeWidth="1" />
                    
                    {/* Dibujo de la línea de ventas */}
                    {(() => {
                      // Agrupar ventas por fecha y ordenar
                      const sortedSales = [...ventas]
                        .reverse()
                        .slice(-6); // Tomar las últimas 6 ventas para graficar
                      const points = sortedSales.map((v, i) => {
                        const x = (i / (sortedSales.length - 1 || 1)) * 480 + 10;
                        // Mapear de 0 a 160 (dejando margen)
                        const maxVal = Math.max(...sortedSales.map(s => s.total), 1);
                        const y = 180 - ((v.total / maxVal) * 140);
                        return { x, y, total: v.total, name: v.nombre };
                      });
                      
                      const pathD = points.reduce((acc, p, i) => {
                        return i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`;
                      }, "");

                      const areaD = points.length > 0 
                        ? `${pathD} L ${points[points.length-1].x} 190 L ${points[0].x} 190 Z` 
                        : "";

                      return (
                        <>
                          <defs>
                            <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor="#4f46e5" stopOpacity="0.2" />
                              <stop offset="100%" stopColor="#4f46e5" stopOpacity="0.0" />
                            </linearGradient>
                          </defs>
                          {areaD && <path d={areaD} fill="url(#salesGrad)" />}
                          {pathD && <path d={pathD} fill="none" stroke="#4f46e5" strokeWidth="3" />}
                          {points.map((p, idx) => (
                            <g key={idx}>
                              <circle cx={p.x} cy={p.y} r="5" fill="#ffffff" stroke="#4f46e5" strokeWidth="2.5" />
                              <text x={p.x} y={p.y - 12} fontSize="9" fontWeight="700" fill="#0f172a" textAnchor="middle">
                                {formatCurrency(p.total)}
                              </text>
                            </g>
                          ))}
                        </>
                      );
                    })()}
                  </svg>
                )}
              </div>
            </div>

            {/* SEGMENTACIÓN MÉTODOS DE PAGO */}
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <h3 className={styles.cardTitle}>Métodos de Pago</h3>
              </div>
              
              <div className={styles.donutWrapper}>
                <svg width="120" height="120" className={styles.donutSvg}>
                  <circle cx="60" cy="60" r="45" fill="transparent" stroke="#f1f5f9" strokeWidth="12" />
                  <circle
                    cx="60"
                    cy="60"
                    r="45"
                    fill="transparent"
                    stroke="#10b981"
                    strokeWidth="12"
                    className={styles.donutSegment}
                    strokeDasharray={`${(cashPct * 282) / 100} ${282 - (cashPct * 282) / 100}`}
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r="45"
                    fill="transparent"
                    stroke="#4f46e5"
                    strokeWidth="12"
                    className={styles.donutSegment}
                    strokeDasharray={`${(cardPct * 282) / 100} ${282 - (cardPct * 282) / 100}`}
                    strokeDashoffset={-((cashPct * 282) / 100)}
                  />
                </svg>
                
                <div className={styles.donutInfo}>
                  <div className={styles.donutLegendItem}>
                    <span className={styles.legendDot} style={{ backgroundColor: "#10b981" }}></span>
                    <div>
                      <div>Efectivo</div>
                      <div style={{ color: "#64748b", fontSize: "11px" }}>{cashPct}% ({formatCurrency(cashSales)})</div>
                    </div>
                  </div>
                  <div className={styles.donutLegendItem}>
                    <span className={styles.legendDot} style={{ backgroundColor: "#4f46e5" }}></span>
                    <div>
                      <div>Transferencia / Tarjeta</div>
                      <div style={{ color: "#64748b", fontSize: "11px" }}>{cardPct}% ({formatCurrency(cardSales)})</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* TOP PRODUCTOS POPULARES */}
            <div className={styles.card} style={{ gridColumn: "1 / -1" }}>
              <div className={styles.cardHeader}>
                <h3 className={styles.cardTitle}>Top Productos Más Vendidos</h3>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {(() => {
                  // Calcular cantidades vendidas por producto
                  const salesMap: { [key: string]: { cant: number, total: number } } = {};
                  ventas.forEach((v) => {
                    if (!salesMap[v.nombre]) salesMap[v.nombre] = { cant: 0, total: 0 };
                    salesMap[v.nombre].cant += v.cantidad;
                    salesMap[v.nombre].total += v.total;
                  });

                  const topProds = Object.entries(salesMap)
                    .sort((a, b) => b[1].cant - a[1].cant)
                    .slice(0, 4);

                  if (topProds.length === 0) {
                    return <p style={{ color: "#64748b", fontSize: "14px" }}>Aún no se registran ventas para calcular productos estrella.</p>;
                  }

                  const maxQty = Math.max(...topProds.map(([_, data]) => data.cant), 1);

                  return topProds.map(([name, data], idx) => {
                    const widthPct = (data.cant / maxQty) * 100;
                    return (
                      <div key={idx} className={styles.barChartRow}>
                        <span className={styles.barLabel}>{name}</span>
                        <div className={styles.barWrapper}>
                          <div className={styles.barFill} style={{ width: `${widthPct}%` }}></div>
                        </div>
                        <span className={styles.barValue}>{data.cant} und.</span>
                        <span style={{ fontSize: "13px", fontWeight: "600", width: "100px", textAlign: "right", color: "#10b981" }}>
                          {formatCurrency(data.total)}
                        </span>
                      </div>
                    );
                  });
                })()}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: INVENTARIO */}
        {activeTab === "inventory" && (
          <div className={styles.card}>
            {/* Buscador y Filtros */}
            <div className={styles.filterRow}>
              <div className={styles.searchWrapper}>
                <span className={styles.searchIcon}>🔍</span>
                <input
                  type="text"
                  placeholder="Buscar producto por nombre o código..."
                  className={styles.searchInput}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <select
                className={styles.selectInput}
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <option value="all">Todas las Categorías</option>
                {categoriesList.map((cat, i) => (
                  <option key={i} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* Tabla de Inventario */}
            <div className={styles.tableWrapper}>
              {filteredProductos.length === 0 ? (
                <div className={styles.emptyState}>
                  <span className={styles.emptyStateIcon}>📦</span>
                  <p className={styles.emptyStateTitle}>No se encontraron productos</p>
                  <p>Intenta ajustar el término de búsqueda o la categoría seleccionada.</p>
                </div>
              ) : (
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Nombre del Producto</th>
                      <th>Categoría</th>
                      <th>Precio de Venta</th>
                      <th>Stock Actual</th>
                      <th>Stock Mínimo</th>
                      <th>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProductos.map((p) => {
                      const isLowStock = p.stock <= p.stock_minimo;
                      const isOutOfStock = p.stock === 0;
                      let badgeStyle = styles.badgeSuccess;
                      let statusText = "Saludable";

                      if (isOutOfStock) {
                        badgeStyle = styles.badgeDanger;
                        statusText = "Sin Stock";
                      } else if (isLowStock) {
                        badgeStyle = styles.badgeWarning;
                        statusText = "Bajo Stock";
                      }

                      return (
                        <tr key={p.id}>
                          <td style={{ fontWeight: "700", color: "#4f46e5" }}>{p.codigo || "S/C"}</td>
                          <td style={{ fontWeight: "600" }}>{p.nombre}</td>
                          <td>
                            <span className={styles.badgeNeutral} style={{ padding: "2px 6px", fontSize: "11px" }}>
                              {p.categoria || "General"}
                            </span>
                          </td>
                          <td style={{ fontWeight: "600" }}>{formatCurrency(p.precio_venta)}</td>
                          <td style={{ fontWeight: "700", color: isLowStock ? "#ef4444" : "inherit" }}>
                            {p.stock}
                          </td>
                          <td style={{ color: "#64748b" }}>{p.stock_minimo}</td>
                          <td>
                            <span className={`${styles.badge} ${badgeStyle}`}>
                              {statusText}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: REGISTRO DE VENTAS */}
        {activeTab === "sales" && (
          <div className={styles.card}>
            {/* Control de Filtro de Fechas */}
            <div className={styles.filterRow} style={{ justifyContent: "flex-end" }}>
              <select
                className={styles.selectInput}
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value as any)}
              >
                <option value="all">Todas las Fechas</option>
                <option value="today">Ventas de Hoy</option>
                <option value="week">Últimos 7 Días</option>
                <option value="month">Este Mes</option>
              </select>
            </div>

            {/* Tabla de Ventas */}
            <div className={styles.tableWrapper}>
              {filteredVentas.length === 0 ? (
                <div className={styles.emptyState}>
                  <span className={styles.emptyStateIcon}>💸</span>
                  <p className={styles.emptyStateTitle}>No se registraron ventas</p>
                  <p>No hay ventas sincronizadas en el rango de fechas seleccionado.</p>
                </div>
              ) : (
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>ID Venta</th>
                      <th>Fecha</th>
                      <th>Producto</th>
                      <th>Cant.</th>
                      <th>Precio Unit.</th>
                      <th>Descuento</th>
                      <th>Total</th>
                      <th>Pago</th>
                      <th>Cliente</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredVentas.map((v) => (
                      <tr key={v.id}>
                        <td style={{ fontWeight: "600", color: "#64748b" }}>#{v.id}</td>
                        <td style={{ fontSize: "13px" }}>{formatFecha(v.fecha)}</td>
                        <td style={{ fontWeight: "600" }}>{v.nombre}</td>
                        <td style={{ fontWeight: "700" }}>{v.cantidad}</td>
                        <td>{formatCurrency(v.precio_unitario)}</td>
                        <td style={{ color: "#ef4444" }}>
                          {v.descuento > 0 ? `-${formatCurrency(v.descuento)}` : "-"}
                        </td>
                        <td style={{ fontWeight: "800", color: "#10b981" }}>{formatCurrency(v.total)}</td>
                        <td>
                          <span
                            className={styles.badge}
                            style={{
                              backgroundColor: v.metodo_pago === "Efectivo" ? "#d1fae5" : "#e0e7ff",
                              color: v.metodo_pago === "Efectivo" ? "#065f46" : "#3730a3",
                              padding: "2px 6px",
                              fontSize: "11px"
                            }}
                          >
                            {v.metodo_pago || "Efectivo"}
                          </span>
                        </td>
                        <td style={{ fontSize: "13px", fontStyle: "italic" }}>
                          {v.cliente_nombre || "Público General"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
