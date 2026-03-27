-- ============================================================
--  SmartGalpón - Esquema PostgreSQL
-- ============================================================

-- ============================================================
--  TABLAS PRINCIPALES
-- ============================================================

CREATE TABLE lote (
    id               SERIAL PRIMARY KEY,
    nombre           VARCHAR(100)   NOT NULL,
    cantidad_pollos  INT            NOT NULL,
    precio_unitario  NUMERIC(10,2)  NOT NULL,
    fecha_inicio     DATE           NOT NULL,
    cantidad_muerto  INT            DEFAULT 0,
    estado           SMALLINT       DEFAULT 0,
    edad_dias        INT            DEFAULT 0
);

CREATE TABLE registro_mortalidad (
    id              SERIAL PRIMARY KEY,
    lote_id         INT  NOT NULL REFERENCES lote(id) ON DELETE CASCADE,
    fecha           DATE NOT NULL,
    cantidad_muerta INT  NOT NULL
);

CREATE TABLE insumos (
    id       SERIAL PRIMARY KEY,
    lotes_id INT            NOT NULL REFERENCES lote(id) ON DELETE CASCADE,
    nombre   VARCHAR(100)   NOT NULL,
    cantidad INT            NOT NULL,
    unidad   VARCHAR(50)    NOT NULL,
    precio   NUMERIC(10,2)  NOT NULL,
    tipo     VARCHAR(50)    NOT NULL DEFAULT 'Otro'
                CHECK (tipo IN ('Alimento','Medicamento','Vacuna','Vitamina','Desinfectante','Otro')),
    fecha    DATE           NOT NULL
);

CREATE TABLE registro_peso (
    id            SERIAL PRIMARY KEY,
    lotes_id      INT            NOT NULL REFERENCES lote(id) ON DELETE CASCADE,
    fecha         DATE           NOT NULL,
    peso_promedio NUMERIC(10,2)  NOT NULL
);

-- ============================================================
--  TABLAS PONEDORAS
-- ============================================================

CREATE TABLE lote_ponedora (
    id               SERIAL PRIMARY KEY,
    nombre           VARCHAR(100)  NOT NULL,
    cantidad_gallinas INT          NOT NULL,
    precio_unitario  NUMERIC(10,2) NOT NULL,
    fecha_inicio     DATE          NOT NULL,
    cantidad_muerto  INT           DEFAULT 0,
    estado           INT           DEFAULT 0,
    edad_semanas     INT           DEFAULT 0,
    muertos_semanales INT          DEFAULT 0
);

CREATE TABLE registro_huevos (
    id              SERIAL PRIMARY KEY,
    lote_id         INT  NOT NULL,
    fecha           DATE NOT NULL,
    cantidad_huevos INT  NOT NULL,
    CONSTRAINT fk_registro_huevos_lote
        FOREIGN KEY (lote_id) REFERENCES lote_ponedora(id) ON DELETE CASCADE
);

CREATE TABLE insumos_ponedora (
    id       SERIAL PRIMARY KEY,
    lotes_id INT            NOT NULL,
    nombre   VARCHAR(100)   NOT NULL,
    cantidad INT            NOT NULL,
    unidad   VARCHAR(50)    NOT NULL,
    precio   NUMERIC(10,2)  NOT NULL,
    tipo     VARCHAR(50)    DEFAULT 'Otro'
                CHECK (tipo IN ('Alimento','Medicamento','Vacuna','Vitamina','Desinfectante','Otro')),
    fecha    DATE           NOT NULL,
    CONSTRAINT fk_insumo_lote
        FOREIGN KEY (lotes_id) REFERENCES lote_ponedora(id) ON DELETE CASCADE
);

CREATE TABLE registro_peso_ponedora (
    id            SERIAL PRIMARY KEY,
    lotes_id      INT            NOT NULL REFERENCES lote_ponedora(id) ON DELETE CASCADE,
    fecha         DATE           NOT NULL,
    peso_promedio NUMERIC(10,2)  NOT NULL
);

CREATE TABLE precio_venta_huevos (
    id               SERIAL PRIMARY KEY,
    lote_id          INT            NOT NULL REFERENCES lote_ponedora(id),
    precio_por_huevo NUMERIC(10,2)  NOT NULL,
    fecha_inicio     DATE           NOT NULL,
    fecha_fin        DATE,
    activo           BOOLEAN        DEFAULT TRUE
);

CREATE TABLE costos_adicionales (
    id          SERIAL PRIMARY KEY,
    lote_id     INT            NOT NULL REFERENCES lote_ponedora(id),
    descripcion VARCHAR(200)   NOT NULL,
    costo       NUMERIC(10,2)  NOT NULL,
    fecha       DATE           NOT NULL,
    tipo        VARCHAR(50)    DEFAULT 'Otros'
                    CHECK (tipo IN ('Mano de obra','Energía','Agua','Mantenimiento','Otros'))
);


-- ============================================================
--  TRIGGERS
-- ============================================================

-- Trigger: registrar mortalidad automáticamente
CREATE OR REPLACE FUNCTION fn_registrar_mortalidad()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.cantidad_muerto > OLD.cantidad_muerto THEN
        INSERT INTO registro_mortalidad (lote_id, fecha, cantidad_muerta)
        VALUES (NEW.id, CURRENT_DATE, NEW.cantidad_muerto - OLD.cantidad_muerto);
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_registrar_mortalidad
AFTER UPDATE ON lote
FOR EACH ROW EXECUTE FUNCTION fn_registrar_mortalidad();


-- Trigger: calcular edad_dias antes de UPDATE
CREATE OR REPLACE FUNCTION fn_actualizar_edad_lote()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.edad_dias := CURRENT_DATE - NEW.fecha_inicio;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_actualizar_edad_lote
BEFORE UPDATE ON lote
FOR EACH ROW EXECUTE FUNCTION fn_actualizar_edad_lote();


-- Trigger: calcular edad_dias antes de INSERT
CREATE OR REPLACE FUNCTION fn_calcular_edad_lote_insert()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.edad_dias := CURRENT_DATE - NEW.fecha_inicio;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_calcular_edad_lote_insert
BEFORE INSERT ON lote
FOR EACH ROW EXECUTE FUNCTION fn_calcular_edad_lote_insert();


-- Trigger: activar lote ponedora al agregar insumo
CREATE OR REPLACE FUNCTION fn_activar_lote_ponedora()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    UPDATE lote_ponedora SET estado = 1 WHERE id = NEW.lotes_id;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_activar_lote_despues_insumo
AFTER INSERT ON insumos_ponedora
FOR EACH ROW EXECUTE FUNCTION fn_activar_lote_ponedora();


-- ============================================================
--  FUNCIONES (equivalentes a Stored Procedures)
-- ============================================================

-- Crear nuevo lote (engorde)
CREATE OR REPLACE FUNCTION sp_crear_nuevo_lote(
    p_cantidad_pollos  INT,
    p_precio_unitario  NUMERIC(10,2),
    p_fecha_inicio     DATE
)
RETURNS SETOF lote LANGUAGE plpgsql AS $$
DECLARE
    v_nuevo_id  INT;
    v_nombre    VARCHAR(100);
BEGIN
    -- Calculamos el próximo id usando la secuencia
    v_nuevo_id := nextval('lote_id_seq');
    v_nombre   := 'Lote ' || v_nuevo_id;

    INSERT INTO lote (id, nombre, cantidad_pollos, precio_unitario, fecha_inicio, cantidad_muerto, estado)
    VALUES (v_nuevo_id, v_nombre, p_cantidad_pollos, p_precio_unitario, p_fecha_inicio, 0, 0);

    RETURN QUERY SELECT * FROM lote WHERE id = v_nuevo_id;
END;
$$;


-- Listar todos los lotes
CREATE OR REPLACE FUNCTION sp_listar_lotes()
RETURNS SETOF lote LANGUAGE sql AS $$
    SELECT * FROM lote;
$$;


-- Ver detalle de lote (engorde)
-- En PostgreSQL no se pueden retornar múltiples result-sets en una función.
-- Se crean funciones separadas por cada conjunto de datos.

CREATE OR REPLACE FUNCTION sp_detalle_lote_info(p_lote_id INT)
RETURNS SETOF lote LANGUAGE sql AS $$
    SELECT * FROM lote WHERE id = p_lote_id;
$$;

CREATE OR REPLACE FUNCTION sp_detalle_lote_insumos(p_lote_id INT)
RETURNS SETOF insumos LANGUAGE sql AS $$
    SELECT * FROM insumos WHERE lotes_id = p_lote_id;
$$;

CREATE OR REPLACE FUNCTION sp_detalle_lote_pesos(p_lote_id INT)
RETURNS SETOF registro_peso LANGUAGE sql AS $$
    SELECT * FROM registro_peso WHERE lotes_id = p_lote_id;
$$;


-- Registrar peso promedio (engorde)
CREATE OR REPLACE FUNCTION sp_registrar_peso(
    p_lotes_id      INT,
    p_fecha         DATE,
    p_peso_promedio NUMERIC(10,2)
)
RETURNS VOID LANGUAGE sql AS $$
    INSERT INTO registro_peso (lotes_id, fecha, peso_promedio)
    VALUES (p_lotes_id, p_fecha, p_peso_promedio);
$$;


-- Crear lote ponedora
CREATE OR REPLACE FUNCTION crear_lote_ponedora(
    p_nombre           VARCHAR(100),
    p_cantidad_gallinas INT,
    p_precio_unitario  NUMERIC(10,2),
    p_fecha_inicio     DATE
)
RETURNS INT LANGUAGE plpgsql AS $$
DECLARE
    v_lote_id INT;
BEGIN
    INSERT INTO lote_ponedora (nombre, cantidad_gallinas, precio_unitario, fecha_inicio)
    VALUES (p_nombre, p_cantidad_gallinas, p_precio_unitario, p_fecha_inicio)
    RETURNING id INTO v_lote_id;

    RETURN v_lote_id;
END;
$$;


-- Listar lotes ponedoras con total de huevos
CREATE OR REPLACE FUNCTION sp_listar_lotes_ponedoras()
RETURNS TABLE (
    id                INT,
    nombre            VARCHAR,
    cantidad_gallinas INT,
    precio_unitario   NUMERIC,
    fecha_inicio      DATE,
    cantidad_muerto   INT,
    estado            INT,
    edad_semanas      INT,
    muertos_semanales INT,
    total_huevos      BIGINT
) LANGUAGE sql AS $$
    SELECT lp.*,
           COALESCE(SUM(rh.cantidad_huevos), 0)::BIGINT AS total_huevos
    FROM lote_ponedora lp
    LEFT JOIN registro_huevos rh ON lp.id = rh.lote_id
    GROUP BY lp.id
    ORDER BY lp.id DESC;
$$;


-- Eliminar lote ponedora
CREATE OR REPLACE FUNCTION sp_eliminar_lote_ponedora(p_lote_id INT)
RETURNS TABLE (mensaje TEXT, lote_eliminado INT) LANGUAGE plpgsql AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM lote_ponedora WHERE id = p_lote_id) THEN
        RAISE EXCEPTION 'El lote con ID % no existe', p_lote_id
            USING ERRCODE = 'P0001';
    END IF;

    DELETE FROM registro_huevos      WHERE lote_id  = p_lote_id;
    DELETE FROM insumos_ponedora      WHERE lotes_id = p_lote_id;
    DELETE FROM registro_peso_ponedora WHERE lotes_id = p_lote_id;
    DELETE FROM precio_venta_huevos   WHERE lote_id  = p_lote_id;
    DELETE FROM costos_adicionales    WHERE lote_id  = p_lote_id;
    DELETE FROM lote_ponedora         WHERE id       = p_lote_id;

    RETURN QUERY SELECT 'Lote eliminado correctamente'::TEXT, p_lote_id;
END;
$$;


--Reporte 

-- Agregar insumo ponedora
CREATE OR REPLACE FUNCTION sp_agregar_insumo_ponedora(
    p_lotes_id INT,
    p_nombre   VARCHAR(100),
    p_cantidad INT,
    p_unidad   VARCHAR(50),
    p_precio   NUMERIC(10,2),
    p_tipo     VARCHAR(50),
    p_fecha    DATE
)
RETURNS TABLE (insumo_id INT, mensaje TEXT) LANGUAGE plpgsql AS $$
DECLARE
    v_id INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM lote_ponedora WHERE id = p_lotes_id) THEN
        RAISE EXCEPTION 'El lote especificado no existe' USING ERRCODE = 'P0001';
    END IF;

    INSERT INTO insumos_ponedora (lotes_id, nombre, cantidad, unidad, precio, tipo, fecha)
    VALUES (p_lotes_id, p_nombre, p_cantidad, p_unidad, p_precio, p_tipo, p_fecha)
    RETURNING id INTO v_id;

    RETURN QUERY SELECT v_id, 'Insumo agregado correctamente'::TEXT;
END;
$$;


-- Eliminar insumo ponedora
CREATE OR REPLACE FUNCTION sp_eliminar_insumo_ponedora(p_insumo_id INT)
RETURNS TABLE (mensaje TEXT, insumo_eliminado INT) LANGUAGE plpgsql AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM insumos_ponedora WHERE id = p_insumo_id) THEN
        RAISE EXCEPTION 'El insumo con ID % no existe', p_insumo_id
            USING ERRCODE = 'P0001';
    END IF;

    DELETE FROM insumos_ponedora WHERE id = p_insumo_id;

    RETURN QUERY SELECT 'Insumo eliminado correctamente'::TEXT, p_insumo_id;
END;
$$;


-- Agregar registro de huevos
CREATE OR REPLACE FUNCTION sp_agregar_registro_huevos(
    p_lote_id        INT,
    p_fecha          DATE,
    p_cantidad_huevos INT
)
RETURNS TABLE (registro_id INT, mensaje TEXT) LANGUAGE plpgsql AS $$
DECLARE
    v_id INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM lote_ponedora WHERE id = p_lote_id) THEN
        RAISE EXCEPTION 'El lote especificado no existe' USING ERRCODE = 'P0001';
    END IF;

    INSERT INTO registro_huevos (lote_id, fecha, cantidad_huevos)
    VALUES (p_lote_id, p_fecha, p_cantidad_huevos)
    RETURNING id INTO v_id;

    RETURN QUERY SELECT v_id, 'Registro de huevos agregado correctamente'::TEXT;
END;
$$;


-- Agregar registro de peso ponedora
CREATE OR REPLACE FUNCTION sp_agregar_registro_peso(
    p_lotes_id      INT,
    p_fecha         DATE,
    p_peso_promedio NUMERIC(10,2)
)
RETURNS TABLE (registro_id INT, mensaje TEXT) LANGUAGE plpgsql AS $$
DECLARE
    v_id INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM lote_ponedora WHERE id = p_lotes_id) THEN
        RAISE EXCEPTION 'El lote especificado no existe' USING ERRCODE = 'P0001';
    END IF;

    INSERT INTO registro_peso_ponedora (lotes_id, fecha, peso_promedio)
    VALUES (p_lotes_id, p_fecha, p_peso_promedio)
    RETURNING id INTO v_id;

    RETURN QUERY SELECT v_id, 'Registro de peso agregado correctamente'::TEXT;
END;
$$;


-- Establecer precio de venta de huevo
CREATE OR REPLACE FUNCTION sp_establecer_precio_huevo(
    p_lote_id        INT,
    p_precio_por_huevo NUMERIC(10,2),
    p_fecha_inicio   DATE
)
RETURNS INT LANGUAGE plpgsql AS $$
DECLARE
    v_id INT;
BEGIN
    -- Desactivar precios anteriores
    UPDATE precio_venta_huevos
    SET activo    = FALSE,
        fecha_fin = p_fecha_inicio - INTERVAL '1 day'
    WHERE lote_id = p_lote_id AND activo = TRUE;

    INSERT INTO precio_venta_huevos (lote_id, precio_por_huevo, fecha_inicio, activo)
    VALUES (p_lote_id, p_precio_por_huevo, p_fecha_inicio, TRUE)
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;


-- Agregar costo adicional
CREATE OR REPLACE FUNCTION sp_agregar_costo_adicional(
    p_lote_id     INT,
    p_descripcion VARCHAR(200),
    p_costo       NUMERIC(10,2),
    p_fecha       DATE,
    p_tipo        VARCHAR(50)
)
RETURNS INT LANGUAGE plpgsql AS $$
DECLARE
    v_id INT;
BEGIN
    INSERT INTO costos_adicionales (lote_id, descripcion, costo, fecha, tipo)
    VALUES (p_lote_id, p_descripcion, p_costo, p_fecha, p_tipo)
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;


-- Calcular ganancia por rango de fechas
CREATE OR REPLACE FUNCTION sp_calcular_ganancia_lote(
    p_lote_id     INT,
    p_fecha_inicio DATE,
    p_fecha_fin    DATE
)
RETURNS TABLE (
    ingresos_huevos   NUMERIC,
    costo_insumos     NUMERIC,
    costos_adicionales NUMERIC,
    ganancia_neta     NUMERIC
) LANGUAGE sql AS $$
    SELECT
        COALESCE((
            SELECT SUM(rh.cantidad_huevos * pvh.precio_por_huevo)
            FROM registro_huevos rh
            JOIN precio_venta_huevos pvh ON rh.lote_id = pvh.lote_id
            WHERE rh.lote_id = p_lote_id
              AND rh.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
              AND rh.fecha BETWEEN pvh.fecha_inicio AND COALESCE(pvh.fecha_fin, CURRENT_DATE)
        ), 0) AS ingresos_huevos,

        COALESCE((
            SELECT SUM(ip.cantidad * ip.precio)
            FROM insumos_ponedora ip
            WHERE ip.lotes_id = p_lote_id
              AND ip.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
        ), 0) AS costo_insumos,

        COALESCE((
            SELECT SUM(ca.costo)
            FROM costos_adicionales ca
            WHERE ca.lote_id = p_lote_id
              AND ca.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
        ), 0) AS costos_adicionales,

        COALESCE((
            SELECT SUM(rh.cantidad_huevos * pvh.precio_por_huevo)
            FROM registro_huevos rh
            JOIN precio_venta_huevos pvh ON rh.lote_id = pvh.lote_id
            WHERE rh.lote_id = p_lote_id
              AND rh.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
              AND rh.fecha BETWEEN pvh.fecha_inicio AND COALESCE(pvh.fecha_fin, CURRENT_DATE)
        ), 0)
        -
        (
            COALESCE((
                SELECT SUM(ip.cantidad * ip.precio)
                FROM insumos_ponedora ip
                WHERE ip.lotes_id = p_lote_id
                  AND ip.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
            ), 0)
            +
            COALESCE((
                SELECT SUM(ca.costo)
                FROM costos_adicionales ca
                WHERE ca.lote_id = p_lote_id
                  AND ca.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
            ), 0)
        ) AS ganancia_neta;
$$;


-- Resumen total de ganancia de un lote ponedora
CREATE OR REPLACE FUNCTION sp_resumen_ganancia_lote(p_lote_id INT)
RETURNS TABLE (
    id               INT,
    nombre           VARCHAR,
    cantidad_gallinas INT,
    fecha_inicio     DATE,
    total_huevos     BIGINT,
    ingresos_totales NUMERIC,
    costos_totales   NUMERIC,
    ganancia_total   NUMERIC
) LANGUAGE sql AS $$
    SELECT
        lp.id,
        lp.nombre,
        lp.cantidad_gallinas,
        lp.fecha_inicio,

        COALESCE((
            SELECT SUM(cantidad_huevos) FROM registro_huevos WHERE lote_id = p_lote_id
        ), 0)::BIGINT AS total_huevos,

        COALESCE((
            SELECT SUM(rh.cantidad_huevos * pvh.precio_por_huevo)
            FROM registro_huevos rh
            JOIN precio_venta_huevos pvh ON rh.lote_id = pvh.lote_id
            WHERE rh.lote_id = p_lote_id
              AND rh.fecha BETWEEN pvh.fecha_inicio AND COALESCE(pvh.fecha_fin, CURRENT_DATE)
        ), 0) AS ingresos_totales,

        (
            COALESCE((
                SELECT SUM(ip.cantidad * ip.precio) FROM insumos_ponedora ip WHERE ip.lotes_id = p_lote_id
            ), 0)
            +
            COALESCE((
                SELECT SUM(ca.costo) FROM costos_adicionales ca WHERE ca.lote_id = p_lote_id
            ), 0)
        ) AS costos_totales,

        COALESCE((
            SELECT SUM(rh.cantidad_huevos * pvh.precio_por_huevo)
            FROM registro_huevos rh
            JOIN precio_venta_huevos pvh ON rh.lote_id = pvh.lote_id
            WHERE rh.lote_id = p_lote_id
              AND rh.fecha BETWEEN pvh.fecha_inicio AND COALESCE(pvh.fecha_fin, CURRENT_DATE)
        ), 0)
        -
        (
            COALESCE((
                SELECT SUM(ip.cantidad * ip.precio) FROM insumos_ponedora ip WHERE ip.lotes_id = p_lote_id
            ), 0)
            +
            COALESCE((
                SELECT SUM(ca.costo) FROM costos_adicionales ca WHERE ca.lote_id = p_lote_id
            ), 0)
        ) AS ganancia_total

    FROM lote_ponedora lp
    WHERE lp.id = p_lote_id;
$$;


-- ============================================================
--  EVENTO SEMANAL → pg_cron (requiere extensión pg_cron)
-- ============================================================
-- Si tienes pg_cron instalado, descomenta las siguientes líneas:
--
-- SELECT cron.schedule(
--     'actualizar_edad_semanas',
--     '0 0 * * 0',   -- cada domingo a medianoche
--     $$
--         UPDATE lote_ponedora
--         SET edad_semanas = edad_semanas + 1
--         WHERE estado = 1;
--     $$
-- );