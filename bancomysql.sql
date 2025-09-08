CREATE DATABASE cadastro;
USE cadastro;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    senha VARCHAR(255),
    tel VARCHAR(20) UNIQUE,
    email VARCHAR(100) UNIQUE,
    cpf VARCHAR(20) UNIQUE
);

SELECT * FROM usuarios;

DELETE FROM usuarios WHERE id >= 0;

