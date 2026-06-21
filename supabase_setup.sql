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
