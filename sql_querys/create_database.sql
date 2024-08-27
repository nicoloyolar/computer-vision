USE db_conteo_entero;

CREATE TABLE Productos (
    ProductoID INT PRIMARY KEY IDENTITY(1,1),
    Nombre VARCHAR(100),
    Peso DECIMAL(5,2),
    FechaCreacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE ConteoBolsas (
    ConteoID INT PRIMARY KEY IDENTITY(1,1),
    ProductoID INT FOREIGN KEY REFERENCES Productos(ProductoID),
    Cantidad INT,
    FechaHora DATETIME DEFAULT GETDATE()
);

CREATE TABLE Alertas (
    AlertaID INT PRIMARY KEY IDENTITY(1,1),
    TipoAlerta VARCHAR(50),
    Descripcion TEXT,
    FechaHora DATETIME DEFAULT GETDATE(),
    ProductoID INT FOREIGN KEY REFERENCES Productos(ProductoID),
    Estado VARCHAR(20)
);

CREATE TABLE GraficosEstadistica (
    GraficoID INT PRIMARY KEY IDENTITY(1,1),
    TipoGrafico VARCHAR(50),
    Descripcion TEXT,
    FechaGeneracion DATETIME DEFAULT GETDATE(),
    ConteoID INT FOREIGN KEY REFERENCES ConteoBolsas(ConteoID),
    AlertaID INT FOREIGN KEY REFERENCES Alertas(AlertaID) NULL
);

CREATE TABLE Usuarios (
    UsuarioID INT PRIMARY KEY IDENTITY(1,1),
    Nombre VARCHAR(100),
    Email VARCHAR(100),
    Telefono VARCHAR(20)
);

CREATE TABLE AlertasEnviadas (
    AlertaEnviadaID INT PRIMARY KEY IDENTITY(1,1),
    AlertaID INT FOREIGN KEY REFERENCES Alertas(AlertaID),
    UsuarioID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID),
    FechaEnvio DATETIME DEFAULT GETDATE(),
    Canal VARCHAR(20)
);
