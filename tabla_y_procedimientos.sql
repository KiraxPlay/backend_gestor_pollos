CREATE TABLE lote (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cantidad_pollos INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    fecha_inicio DATE NOT NULL,
    cantidad_muerto INT DEFAULT 0,
    estado TINYINT DEFAULT 0
);

CREATE TABLE registro_mortalidad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lote_id INT NOT NULL,
    fecha DATE NOT NULL,
    cantidad_muerta INT NOT NULL,
    FOREIGN KEY (lote_id) REFERENCES lote(id) ON DELETE CASCADE
);




CREATE TABLE insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lotes_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    unidad VARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    tipo ENUM('Alimento','Medicamento','Vacuna','Vitamina','Desinfectante','Otro') 
         NOT NULL DEFAULT 'Otro',
    fecha DATE NOT NULL,
    FOREIGN KEY (lotes_id) REFERENCES lote(id) ON DELETE CASCADE
);



CREATE TABLE registro_peso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lotes_id INT NOT NULL,
    fecha DATE NOT NULL,
    peso_promedio DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (lotes_id) REFERENCES lote(id) ON DELETE CASCADE
);

--Procedimientos almacenados
--Crear nuevo lote
DELIMITER $$

CREATE PROCEDURE sp_crear_nuevo_lote(
    IN p_cantidad_pollos INT,
    IN p_precio_unitario DECIMAL(10,2),
    IN p_fecha_inicio DATE
)
BEGIN
    DECLARE nuevo_id INT;

    -- Obtenemos el próximo id (AUTO_INCREMENT)
    SELECT AUTO_INCREMENT INTO nuevo_id
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'lote';

    -- Construimos el nombre automáticamente
    SET @nombre_lote = CONCAT('Lote ', nuevo_id);

    -- Insertamos el lote con cantidad_muertos y estado en 0
    INSERT INTO lote (nombre, cantidad_pollos, precio_unitario, fecha_inicio, cantidad_muerto, estado)
    VALUES (@nombre_lote, p_cantidad_pollos, p_precio_unitario, p_fecha_inicio, 0, 0);

    -- Devolvemos el lote creado
    SELECT * FROM lote WHERE id = LAST_INSERT_ID();
END$$

DELIMITER ;

--Motrar o en listar todos los lotes
DELIMITER $$
CREATE PROCEDURE sp_listar_lotes()
BEGIN
    SELECT * FROM lote;
END$$
DELIMITER ;

--Agregar insumo y actualizar estado del lote
DELIMITER $$

CREATE PROCEDURE sp_agregar_insumo(
    IN p_id_lote INT,
    IN p_nombre VARCHAR(100),
    IN p_tipo VARCHAR(50),
    IN p_cantidad INT,
    IN p_precio DECIMAL(10,2)
)
BEGIN
    -- Insertamos el insumo
    INSERT INTO insumo (id_lote, nombre, tipo, cantidad, precio)
    VALUES (p_id_lote, p_nombre, p_tipo, p_cantidad, p_precio);

    -- Actualizamos el estado del lote a 1 (activo)
    UPDATE lote
    SET estado = 1
    WHERE id = p_id_lote;

    -- Devolvemos el insumo agregado
    SELECT * FROM insumo WHERE id = LAST_INSERT_ID();
END$$

DELIMITER ;


--Ver detalles de lote
DELIMITER $$

CREATE PROCEDURE sp_detalle_lote(IN p_id_lote INT)
BEGIN
    -- Información del lote
    SELECT * FROM lote WHERE id = p_id_lote;

    -- Insumos asociados
    SELECT * FROM insumos WHERE lotes_id = p_id_lote;

    -- Registros de peso asociados
    SELECT * FROM registro_peso WHERE lotes_id = p_id_lote;
END$$

DELIMITER ;


--Eliminar insumo y actualizar estado del lote si es necesario

DELIMITER $$

CREATE PROCEDURE sp_eliminar_insumo(
    IN p_id_insumo INT,
    IN p_id_lote INT
)
BEGIN
    -- Eliminamos el insumo
    DELETE FROM insumo WHERE id = p_id_insumo;

    -- Si ya no quedan insumos, pasamos el lote a estado = 0
    IF (SELECT COUNT(*) FROM insumo WHERE id_lote = p_id_lote) = 0 THEN
        UPDATE lote SET estado = 0 WHERE id = p_id_lote;
    END IF;
END$$

DELIMITER ;

--Registrar peso promedio
DELIMITER //
CREATE PROCEDURE sp_registrar_peso(
    IN p_lotes_id INT,
    IN p_fecha DATE,
    IN p_peso_promedio DECIMAL(10,2)
)
BEGIN
    INSERT INTO registro_peso (lotes_id, fecha, peso_promedio)
    VALUES (p_lotes_id, p_fecha, p_peso_promedio);
END //
DELIMITER ;




--triggers 

-- Trigger para registrar mortalidad automáticamente
DELIMITER //
CREATE TRIGGER tr_registrar_mortalidad
AFTER UPDATE ON lote
FOR EACH ROW
BEGIN
    -- Solo se registra si la cantidad_muerto aumentó
    IF NEW.cantidad_muerto > OLD.cantidad_muerto THEN
        INSERT INTO registro_mortalidad (lote_id, fecha, cantidad_muerta)
        VALUES (NEW.id, CURDATE(), NEW.cantidad_muerto - OLD.cantidad_muerto);
    END IF;
END //
DELIMITER ;


DELIMITER //
CREATE TRIGGER tr_actualizar_edad_lote
BEFORE UPDATE ON lote
FOR EACH ROW
BEGIN
    -- Actualizar edad en días cuando cambie la fecha u otros campos relevantes
    SET NEW.edad_dias = DATEDIFF(CURDATE(), NEW.fecha_inicio);
END //
DELIMITER ;


-- Trigger para INSERT también
DELIMITER //
CREATE TRIGGER tr_calcular_edad_lote_insert
BEFORE INSERT ON lote
FOR EACH ROW
BEGIN
    SET NEW.edad_dias = DATEDIFF(CURDATE(), NEW.fecha_inicio);
END //
DELIMITER ;






--para modelo de ponedoras
CREATE TABLE lote_ponedora (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cantidad_gallinas INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    fecha_inicio DATE NOT NULL,
    cantidad_muerto INT DEFAULT 0,
    estado INT DEFAULT 0,
    edad_semanas INT DEFAULT 0,
    muertos_semanales INT DEFAULT 0
);

CREATE TABLE registro_huevos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lote_id INT NOT NULL,
    fecha DATE NOT NULL,
    cantidad_huevos INT NOT NULL,
    CONSTRAINT fk_registro_huevos_lote
        FOREIGN KEY (lote_id) REFERENCES lote_ponedora(id)
        ON DELETE CASCADE
);

CREATE TABLE insumos_ponedora (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lotes_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    unidad VARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    tipo ENUM('Alimento', 'Medicamento', 'Vacuna', 'Vitamina', 'Desinfectante', 'Otro') DEFAULT 'Otro',
    fecha DATE NOT NULL,
    CONSTRAINT fk_insumo_lote
        FOREIGN KEY (lotes_id) REFERENCES lote_ponedora(id)
        ON DELETE CASCADE
);

-- Tabla para precios de venta de huevos
CREATE TABLE precio_venta_huevos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lote_id INT NOT NULL,
    precio_por_huevo DECIMAL(10,2) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NULL,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (lote_id) REFERENCES lote_ponedora(id)
);

-- Tabla para costos adicionales
CREATE TABLE costos_adicionales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lote_id INT NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    costo DECIMAL(10,2) NOT NULL,
    fecha DATE NOT NULL,
    tipo ENUM('Mano de obra', 'Energía', 'Agua', 'Mantenimiento', 'Otros') DEFAULT 'Otros',
    FOREIGN KEY (lote_id) REFERENCES lote_ponedora(id)
);

DELIMITER //
CREATE PROCEDURE sp_eliminar_lote(
    IN p_lote_id INT
)
BEGIN
    DELETE FROM lote_ponedora
    WHERE id = p_lote_id AND estado = 0;
END //
DELIMITER ;



DELIMITER //
CREATE PROCEDURE sp_agregar_costo_adicional(
    IN p_lote_id INT,
    IN p_descripcion VARCHAR(200),
    IN p_costo DECIMAL(10,2),
    IN p_fecha DATE,
    IN p_tipo ENUM('Mano de obra', 'Energía', 'Agua', 'Mantenimiento', 'Otros')
)
BEGIN
    INSERT INTO costos_adicionales (lote_id, descripcion, costo, fecha, tipo)
    VALUES (p_lote_id, p_descripcion, p_costo, p_fecha, p_tipo);
    
    SELECT LAST_INSERT_ID() AS costo_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE sp_calcular_ganancia_lote(
    IN p_lote_id INT,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE
)
BEGIN
    SELECT 
        -- Ingresos por venta de huevos
        (SELECT IFNULL(SUM(rh.cantidad_huevos * pvh.precio_por_huevo), 0)
         FROM registro_huevos rh
         JOIN precio_venta_huevos pvh ON rh.lote_id = pvh.lote_id
         WHERE rh.lote_id = p_lote_id 
           AND rh.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
           AND rh.fecha BETWEEN pvh.fecha_inicio AND IFNULL(pvh.fecha_fin, CURDATE()))
        AS ingresos_huevos,
        
        -- Costo de insumos
        (SELECT IFNULL(SUM(ip.cantidad * ip.precio), 0)
         FROM insumos_ponedora ip
         WHERE ip.lotes_id = p_lote_id 
           AND ip.fecha BETWEEN p_fecha_inicio AND p_fecha_fin)
        AS costo_insumos,
        
        -- Costos adicionales
        (SELECT IFNULL(SUM(ca.costo), 0)
         FROM costos_adicionales ca
         WHERE ca.lote_id = p_lote_id 
           AND ca.fecha BETWEEN p_fecha_inicio AND p_fecha_fin)
        AS costos_adicionales,
        
        -- Ganancia neta
        ((SELECT IFNULL(SUM(rh.cantidad_huevos * pvh.precio_por_huevo), 0)
          FROM registro_huevos rh
          JOIN precio_venta_huevos pvh ON rh.lote_id = pvh.lote_id
          WHERE rh.lote_id = p_lote_id 
            AND rh.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
            AND rh.fecha BETWEEN pvh.fecha_inicio AND IFNULL(pvh.fecha_fin, CURDATE())))
        - 
        ((SELECT IFNULL(SUM(ip.cantidad * ip.precio), 0)
          FROM insumos_ponedora ip
          WHERE ip.lotes_id = p_lote_id 
            AND ip.fecha BETWEEN p_fecha_inicio AND p_fecha_fin)
         +
        (SELECT IFNULL(SUM(ca.costo), 0)
         FROM costos_adicionales ca
         WHERE ca.lote_id = p_lote_id 
           AND ca.fecha BETWEEN p_fecha_inicio AND p_fecha_fin))
        AS ganancia_neta;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE sp_establecer_precio_huevo(
    IN p_lote_id INT,
    IN p_precio_por_huevo DECIMAL(10,2),
    IN p_fecha_inicio DATE
)
BEGIN
    -- Desactivar precios anteriores del mismo lote
    UPDATE precio_venta_huevos 
    SET activo = FALSE, fecha_fin = DATE_SUB(p_fecha_inicio, INTERVAL 1 DAY)
    WHERE lote_id = p_lote_id AND activo = TRUE;
    
    -- Insertar nuevo precio
    INSERT INTO precio_venta_huevos (lote_id, precio_por_huevo, fecha_inicio, activo)
    VALUES (p_lote_id, p_precio_por_huevo, p_fecha_inicio, TRUE);
    
    SELECT LAST_INSERT_ID() AS precio_id;
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE sp_resumen_ganancia_lote(IN p_lote_id INT)
BEGIN
    SELECT 
        lp.id,  -- ← ¡AGREGA ESTA LÍNEA!
        lp.nombre,
        lp.cantidad_gallinas,
        lp.fecha_inicio,
        
        -- Total huevos producidos
        (SELECT IFNULL(SUM(cantidad_huevos), 0) 
         FROM registro_huevos 
         WHERE lote_id = p_lote_id) AS total_huevos,
        
        -- Ingresos totales
        (SELECT IFNULL(SUM(rh.cantidad_huevos * pvh.precio_por_huevo), 0)
         FROM registro_huevos rh
         JOIN precio_venta_huevos pvh ON rh.lote_id = pvh.lote_id
         WHERE rh.lote_id = p_lote_id
           AND rh.fecha BETWEEN pvh.fecha_inicio AND IFNULL(pvh.fecha_fin, CURDATE()))
        AS ingresos_totales,
        
        -- Costos totales
        (SELECT IFNULL(SUM(ip.cantidad * ip.precio), 0)
         FROM insumos_ponedora ip
         WHERE ip.lotes_id = p_lote_id)
        +
        (SELECT IFNULL(SUM(ca.costo), 0)
         FROM costos_adicionales ca
         WHERE ca.lote_id = p_lote_id)
        AS costos_totales,
        
        -- Ganancia total
        ((SELECT IFNULL(SUM(rh.cantidad_huevos * pvh.precio_por_huevo), 0)
          FROM registro_huevos rh
          JOIN precio_venta_huevos pvh ON rh.lote_id = pvh.lote_id
          WHERE rh.lote_id = p_lote_id
            AND rh.fecha BETWEEN pvh.fecha_inicio AND IFNULL(pvh.fecha_fin, CURDATE())))
        -
        ((SELECT IFNULL(SUM(ip.cantidad * ip.precio), 0)
          FROM insumos_ponedora ip
          WHERE ip.lotes_id = p_lote_id)
         +
        (SELECT IFNULL(SUM(ca.costo), 0)
         FROM costos_adicionales ca
         WHERE ca.lote_id = p_lote_id))
        AS ganancia_total
        
    FROM lote_ponedora lp
    WHERE lp.id = p_lote_id;
END //
DELIMITER ;

--Procedimientos almacenados para ponedoras
DELIMITER //
CREATE PROCEDURE crear_lote_ponedora(
    IN p_nombre VARCHAR(100),
    IN p_cantidad_gallinas INT,
    IN p_precio_unitario DECIMAL(10,2),
    IN p_fecha_inicio DATE
)
BEGIN
    INSERT INTO lote_ponedora (
        nombre, cantidad_gallinas, precio_unitario, fecha_inicio
    )
    VALUES (
        p_nombre, p_cantidad_gallinas, p_precio_unitario, p_fecha_inicio
    );

    SELECT LAST_INSERT_ID() AS lote_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE sp_listar_lotes_ponedoras()
BEGIN
    SELECT lp.*, 
           IFNULL(SUM(rh.cantidad_huevos), 0) AS total_huevos
    FROM lote_ponedora lp
    LEFT JOIN registro_huevos rh ON lp.id = rh.lote_id
    GROUP BY lp.id
    ORDER BY lp.id DESC;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE sp_detalle_lote_ponedora(IN p_lote_id INT)
BEGIN
    SELECT * FROM lote_ponedora WHERE id = p_lote_id;

    SELECT * FROM insumos_ponedora WHERE lotes_id = p_lote_id;
    SELECT * FROM registro_peso_ponedora WHERE lotes_id = p_lote_id;
    SELECT * FROM registro_huevos WHERE lote_id = p_lote_id;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER tr_activar_lote_despues_insumo
AFTER INSERT ON insumos_ponedora
FOR EACH ROW
BEGIN
    UPDATE lote_ponedora
    SET estado = 1
    WHERE id = NEW.lotes_id;
END //
DELIMITER ;

DELIMITER //
CREATE EVENT ev_actualizar_edad_semanas
ON SCHEDULE EVERY 1 WEEK
DO
BEGIN
    UPDATE lote_ponedora
    SET edad_semanas = edad_semanas + 1
    WHERE estado = 1; -- solo los activos
END //
DELIMITER ;





/*#por el momento no se usara autenticacion ni permisos
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

*/

/*en bd_Smartgalpon -> settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':'bd_smartgalpon',
        'USER':'root',
        'PASSWORD':'',
        'HOST':'localhost',
        'PORT':'3306',
    }
}
*/


