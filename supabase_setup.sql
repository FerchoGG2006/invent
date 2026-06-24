-- =========================================================================
-- SCRIPT DE CONFIGURACIÓN DE BASE DE DATOS EN SUPABASE
-- Ejecuta este script en el editor SQL de tu proyecto en Supabase (SQL Editor)
-- =========================================================================

-- 1. Tabla de Productos (Stock)
CREATE TABLE IF NOT EXISTS public.productos (
    id BIGINT PRIMARY KEY, -- Coincide con el ID del producto local
    codigo TEXT,
    nombre TEXT NOT NULL,
    categoria TEXT,
    precio_venta NUMERIC,
    stock INTEGER NOT NULL DEFAULT 0,
    stock_minimo INTEGER DEFAULT 3,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Tabla de Ventas
CREATE TABLE IF NOT EXISTS public.ventas (
    id BIGINT PRIMARY KEY, -- Coincide con el ID de la venta local
    codigo TEXT,
    nombre TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario NUMERIC NOT NULL,
    total NUMERIC NOT NULL,
    fecha TIMESTAMP WITH TIME ZONE,
    metodo_pago TEXT,
    descuento NUMERIC DEFAULT 0.0,
    cliente_nombre TEXT,
    impuestos NUMERIC DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Habilitar el acceso público sin autenticación (Usando la Anon Key del POS)
-- Esto permite que el sistema POS de escritorio suba los datos usando la clave Anon.

-- Deshabilitar RLS temporalmente o crear políticas para permitir operaciones Anon:
ALTER TABLE public.productos DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.ventas DISABLE ROW LEVEL SECURITY;

-- O si prefieres mantener RLS activo, puedes ejecutar lo siguiente para permitir que Anon inserte y actualice:
-- ALTER TABLE public.productos ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.ventas ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Permitir todo a Anon" ON public.productos FOR ALL TO anon USING (true) WITH CHECK (true);
-- CREATE POLICY "Permitir todo a Anon" ON public.ventas FOR ALL TO anon USING (true) WITH CHECK (true);

-- 4. Tabla de Clientes (CRM)
CREATE TABLE IF NOT EXISTS public.clientes (
    id BIGINT PRIMARY KEY,
    nombre TEXT NOT NULL,
    telefono TEXT,
    email TEXT,
    puntos INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Tabla de Citas (Agenda)
CREATE TABLE IF NOT EXISTS public.citas (
    id BIGINT PRIMARY KEY,
    cliente_nombre TEXT NOT NULL,
    cliente_telefono TEXT,
    fecha_cita TIMESTAMP WITH TIME ZONE NOT NULL,
    barbero TEXT,
    servicio TEXT,
    estado TEXT DEFAULT 'Pendiente', -- Pendiente, Completada, Cancelada
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Tabla de Turnos de Caja (Cierre)
CREATE TABLE IF NOT EXISTS public.turnos_caja (
    id BIGINT PRIMARY KEY,
    caja_id BIGINT,
    usuario_id BIGINT,
    fecha_apertura TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    fecha_cierre TIMESTAMP WITH TIME ZONE,
    monto_apertura NUMERIC DEFAULT 0.0,
    monto_cierre_esperado NUMERIC DEFAULT 0.0,
    monto_cierre_real NUMERIC DEFAULT 0.0,
    diferencia NUMERIC DEFAULT 0.0,
    estado TEXT DEFAULT 'Abierto',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Deshabilitar RLS temporalmente para las nuevas tablas
ALTER TABLE public.clientes DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.citas DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.turnos_caja DISABLE ROW LEVEL SECURITY;
