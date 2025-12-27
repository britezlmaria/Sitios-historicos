-- Crear bases
CREATE DATABASE grupo05_test OWNER admin;

-- Habilitar PostGIS en ambas
\connect grupo05
CREATE EXTENSION IF NOT EXISTS postgis;

\connect grupo05_test
CREATE EXTENSION IF NOT EXISTS postgis;
