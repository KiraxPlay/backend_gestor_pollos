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
