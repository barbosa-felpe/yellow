// server.js
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 5000;

// Conecta ao banco de dados SQLite (em modo de leitura)
const db = new sqlite3.Database('./setupDatabase.db', sqlite3.OPEN_READONLY, (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Conectado ao banco de dados setupDatabase.');
});

// Middlewares
app.use(cors());
app.use(express.json());

// 🔹 Servir arquivos estáticos da pasta "templates"
// Isso garante que seu linhas.js, css etc. fiquem acessíveis
app.use(express.static(path.join(__dirname, 'static')));

// 🔹 Rota para abrir a página linhas.html
app.get('/linhas', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'linhas.html'));
});

// 🔹 Rota da API para buscar linhas de ônibus
app.get('/api/search', (req, res) => {
    const searchTerm = req.query.term;

    if (!searchTerm) {
        return res.json([]);
    }

    const sql = `
        SELECT codigo, nome 
        FROM linhas 
        WHERE nome LIKE ? OR codigo LIKE ?
        LIMIT 20`;

    const searchValue = `%${searchTerm}%`;

    db.all(sql, [searchValue, searchValue], (err, rows) => {
        if (err) {
            console.error(err.message);
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});

app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
