-- ==================== INSERT PRODUCTS ====================
INSERT INTO product (code, name, category, cost_price, sale_price, min_stock, status) VALUES
('MS-COLET-BEBE-300', 'Colet Panty Bebe Individual', 'Accesorios', 300.0, 1100.0, 1, 'ativo'),
('MS-TIBURON-DOUBLE-3600', 'Tiburon Rectangular Double Agarre Color', 'Accesorios', 3600.0, 12000.0, 1, 'ativo'),
('MS-TICTAC-ESTRELLA-700', 'Tictac Estrella G Color 1', 'Accesorios', 700.0, 12600.0, 1, 'ativo'),
('MS-TICTAC-PUNTO-400', 'Tic Tac Punto + Cuadrille', 'Accesorios', 400.0, 7200.0, 1, 'ativo'),
('MS-PINZA-DIFT-700', 'Pinza 6/3 DIFT', 'Accesorios', 700.0, 12600.0, 1, 'ativo'),
('MS-COLET-MEDIANO-1500', 'Colet Panty Mediano Con Carton', 'Accesorios', 1500.0, 9000.0, 1, 'ativo'),
('MS-CINILLO-AZUL-4800', 'Cinillo Nudo Surtido Azul', 'Accesorios', 4800.0, 4800.0, 1, 'ativo'),
('MS-TIBURON-ENGOMADO-3600', 'Tiburon Engomado Rectangular', 'Accesorios', 3600.0, 7200.0, 1, 'ativo'),
('MS-SET-CINTILLO-SPA-1400', 'Set Cintillo Spa + Hawai', 'Accesorios', 1400.0, 5600.0, 1, 'ativo'),
('MS-TIBURON-NEGRO-1500', 'Tiburon Rectangular Negro 4cm', 'Accesorios', 1500.0, 1500.0, 1, 'ativo'),
('MS-TIRA-MARIPOSA-1500', 'Tira Mariposa Chica', 'Accesorios', 1500.0, 3000.0, 1, 'ativo'),
('MS-TIBURON-METAL-3600', 'Tiburon Metal Mediano Cuadrado', 'Accesorios', 3600.0, 3600.0, 1, 'ativo'),
('MS-COLET-TRENZA-500', 'Colet Trenza Tubo', 'Accesorios', 500.0, 6000.0, 1, 'ativo');

-- ==================== INSERT INITIAL STOCK ====================
INSERT INTO purchase (date, product_code, quantity, unit_cost) VALUES
('2026-09-28', 'MS-COLET-BEBE-300', 24, 300.0),
('2026-09-28', 'MS-TIBURON-DOUBLE-3600', 2, 3600.0),
('2026-09-28', 'MS-TICTAC-ESTRELLA-700', 18, 700.0),
('2026-09-28', 'MS-TICTAC-PUNTO-400', 18, 400.0),
('2026-09-28', 'MS-PINZA-DIFT-700', 18, 700.0),
('2026-09-28', 'MS-COLET-MEDIANO-1500', 6, 1500.0),
('2026-09-28', 'MS-CINILLO-AZUL-4800', 1, 4800.0),
('2026-09-28', 'MS-TIBURON-ENGOMADO-3600', 2, 3600.0),
('2026-09-28', 'MS-SET-CINTILLO-SPA-1400', 4, 1400.0),
('2026-09-28', 'MS-TIBURON-NEGRO-1500', 1, 1500.0),
('2026-09-28', 'MS-TIRA-MARIPOSA-1500', 2, 1500.0),
('2026-09-28', 'MS-TIBURON-METAL-3600', 1, 3600.0),
('2026-09-28', 'MS-COLET-TRENZA-500', 12, 500.0);

-- ==================== RESULTADO ====================
-- ✅ 13 productos cargados
-- ✅ 109 unidades de stock inicial
-- ✅ Costo total: $87,500.00
