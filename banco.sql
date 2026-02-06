-- Criação do Banco de Dados
CREATE DATABASE IF NOT EXISTS cadastro;
USE cadastro;

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    tel VARCHAR(20)
);

-- Tabela de Contas (Onde fica o saldo)
CREATE TABLE IF NOT EXISTS contas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) DEFAULT 'Conta Principal',
    saldo DECIMAL(10, 2) DEFAULT 0.00,
    id_usuario INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

-- Tabela de Cartões
CREATE TABLE IF NOT EXISTS cartoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_titular VARCHAR(100),
    numero VARCHAR(20),
    validade VARCHAR(5),
    cvv VARCHAR(5),
    id_usuario INT,
    id_conta INT, -- Opcional, se quiser vincular cartão a uma conta
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

-- Tabela de Favoritas (caso use)
CREATE TABLE IF NOT EXISTS favoritas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_linha VARCHAR(50),
    id_usuario INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

SELECT id, nome_titular FROM cartoes;