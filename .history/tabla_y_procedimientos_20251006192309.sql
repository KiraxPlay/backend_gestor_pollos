CREATE TABLE lote (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cantidad_pollos INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    fecha_inicio DATE NOT NULL,
    cantidad_muerto INT DEFAULT 0,
    estado TINYINT DEFAULT 0
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

--A
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


