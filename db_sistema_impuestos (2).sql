-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-10-2026 a las 19:33:17
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `db_sistema_impuestos`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `idCliente` int(10) NOT NULL,
  `codigo` char(10) NOT NULL,
  `nombre` char(100) NOT NULL,
  `direccion` char(150) NOT NULL,
  `telefono` char(10) NOT NULL,
  `email` char(150) NOT NULL,
  `tipo` char(10) NOT NULL DEFAULT 'particular'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`idCliente`, `codigo`, `nombre`, `direccion`, `telefono`, `email`, `tipo`) VALUES
(1, '001', 'Luis Hernandez', 'Usulutan', '4545-3256', 'luishernandez@ugb.edu.sv', 'particular'),
(2, '0939393', 'paco', 'san jorge', '7272-2271', 'pacomoreir@gmail.com', 'particular'),
(3, '3883883', 'Juan', 'san jorge', '7272-2271', 'pacomoreir@gmail.com', 'particular'),
(4, '3883883', 'Juan', 'san jorge', '7272-2271', 'pacomoreir@gmail.com', 'particular'),
(5, '3883883', 'Juan', 'san jorge', '7272-2271', 'pacomoreir@gmail.com', 'particular'),
(6, '11801', 'Empresa Demo Comercio', 'San Salvador', '2222-1111', 'demo@comercio.sv', 'empresa'),
(7, '11802', 'Empresa Demo Industria', 'San Salvador', '2222-2222', 'demo@industria.sv', 'empresa'),
(8, '1123', 'paco', 'Saint George', '7272-7272', 'pacomoreir@gmail.com', 'empresa');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `periodos`
--

CREATE TABLE `periodos` (
  `idPeriodo` int(11) NOT NULL,
  `idCliente` int(10) NOT NULL,
  `idProducto` int(11) NOT NULL,
  `idTarifa` int(11) NOT NULL,
  `desde` date NOT NULL,
  `hasta` date NOT NULL,
  `monto` decimal(14,2) NOT NULL,
  `cantidad` decimal(14,2) NOT NULL DEFAULT 1.00,
  `precio` decimal(14,6) NOT NULL,
  `subtotal` decimal(14,2) NOT NULL,
  `formula` varchar(20) NOT NULL,
  `tarifaDesde` decimal(14,2) NOT NULL,
  `tarifaHasta` decimal(14,2) NOT NULL,
  `precioBase` decimal(14,6) NOT NULL,
  `adicional` decimal(14,6) NOT NULL,
  `porcentaje` decimal(9,6) NOT NULL DEFAULT 0.000000,
  `excedente` decimal(14,2) NOT NULL DEFAULT 0.00,
  `bloques` int(11) NOT NULL DEFAULT 0,
  `facturado` tinyint(1) NOT NULL DEFAULT 0,
  `usuario` varchar(50) NOT NULL,
  `fechaCalculo` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `periodos`
--

INSERT INTO `periodos` (`idPeriodo`, `idCliente`, `idProducto`, `idTarifa`, `desde`, `hasta`, `monto`, `cantidad`, `precio`, `subtotal`, `formula`, `tarifaDesde`, `tarifaHasta`, `precioBase`, `adicional`, `porcentaje`, `excedente`, `bloques`, `facturado`, `usuario`, `fechaCalculo`) VALUES
(1, 6, 1, 16, '2026-09-22', '2027-05-26', 500.00, 4.00, 1.500000, 6.00, 'BLOQUES_V2', 0.01, 500.00, 1.500000, 0.000000, 0.000000, 499.99, 1, 0, 'admin', '2026-09-30 11:40:35');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `idProducto` int(11) NOT NULL,
  `codigo` varchar(10) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipoActividad` enum('comercio','industria') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`idProducto`, `codigo`, `nombre`, `tipoActividad`) VALUES
(1, '11801', 'Impuesto a las Actividades Economicas Comercio', 'comercio'),
(2, '11802', 'Impuesto a las Actividades Economicas Industria', 'industria');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tarifas`
--

CREATE TABLE `tarifas` (
  `idTarifa` int(11) NOT NULL,
  `idProducto` int(11) NOT NULL,
  `version` int(11) NOT NULL DEFAULT 1,
  `desde` decimal(14,2) NOT NULL,
  `hasta` decimal(14,2) NOT NULL,
  `precioBase` decimal(14,6) NOT NULL,
  `adicional` decimal(14,6) NOT NULL,
  `porcentaje` decimal(9,6) NOT NULL DEFAULT 0.000000,
  `vigenteDesde` date NOT NULL,
  `vigenteHasta` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tarifas`
--

INSERT INTO `tarifas` (`idTarifa`, `idProducto`, `version`, `desde`, `hasta`, `precioBase`, `adicional`, `porcentaje`, `vigenteDesde`, `vigenteHasta`) VALUES
(1, 2, 1, 0.01, 500.00, 1.500000, 0.000000, 0.000000, '2000-01-01', NULL),
(2, 2, 1, 500.01, 1000.00, 1.500000, 3.000000, 0.000000, '2000-01-01', NULL),
(3, 2, 1, 1000.01, 2000.00, 3.000000, 3.000000, 0.000000, '2000-01-01', NULL),
(4, 2, 1, 2000.01, 3000.00, 6.000000, 3.000000, 0.000000, '2000-01-01', NULL),
(5, 2, 1, 3000.01, 6000.00, 9.000000, 2.000000, 0.000000, '2000-01-01', NULL),
(6, 2, 1, 8000.01, 18000.00, 15.000000, 2.000000, 0.000000, '2000-01-01', NULL),
(7, 2, 1, 18000.01, 30000.00, 39.000000, 2.000000, 0.000000, '2000-01-01', NULL),
(8, 2, 1, 30000.01, 60000.00, 63.000000, 1.000000, 0.000000, '2000-01-01', NULL),
(9, 2, 1, 60000.01, 100000.00, 93.000000, 0.800000, 0.000000, '2000-01-01', NULL),
(10, 2, 1, 100000.01, 200000.00, 125.000000, 0.700000, 0.000000, '2000-01-01', NULL),
(11, 2, 1, 200000.01, 300000.00, 195.000000, 0.600000, 0.000000, '2000-01-01', NULL),
(12, 2, 1, 300000.01, 400000.00, 255.000000, 0.450000, 0.000000, '2000-01-01', NULL),
(13, 2, 1, 400000.01, 500000.00, 300.000000, 0.400000, 0.000000, '2000-01-01', NULL),
(14, 2, 1, 500000.01, 1000000.00, 340.000000, 0.300000, 0.000000, '2000-01-01', NULL),
(15, 2, 1, 1000000.01, 99999999.99, 490.000000, 0.180000, 0.000000, '2000-01-01', NULL),
(16, 1, 1, 0.01, 500.00, 1.500000, 0.000000, 0.000000, '2000-01-01', NULL),
(17, 1, 1, 500.01, 1000.00, 1.500000, 3.000000, 0.000000, '2000-01-01', NULL),
(18, 1, 1, 1000.01, 2000.00, 3.000000, 3.000000, 0.000000, '2000-01-01', NULL),
(19, 1, 1, 2000.01, 3000.00, 6.000000, 3.000000, 0.000000, '2000-01-01', NULL),
(20, 1, 1, 3000.01, 6000.00, 9.000000, 2.000000, 0.000000, '2000-01-01', NULL),
(21, 1, 1, 8000.01, 18000.00, 15.000000, 2.000000, 0.000000, '2000-01-01', NULL),
(22, 1, 1, 18000.01, 30000.00, 39.000000, 2.000000, 0.000000, '2000-01-01', NULL),
(23, 1, 1, 30000.01, 60000.00, 63.000000, 1.000000, 0.000000, '2000-01-01', NULL),
(24, 1, 1, 60000.01, 100000.00, 93.000000, 0.800000, 0.000000, '2000-01-01', NULL),
(25, 1, 1, 100000.01, 200000.00, 125.000000, 0.700000, 0.000000, '2000-01-01', NULL),
(26, 1, 1, 200000.01, 300000.00, 195.000000, 0.600000, 0.000000, '2000-01-01', NULL),
(27, 1, 1, 300000.01, 400000.00, 255.000000, 0.450000, 0.000000, '2000-01-01', NULL),
(28, 1, 1, 400000.01, 500000.00, 300.000000, 0.400000, 0.000000, '2000-01-01', NULL),
(29, 1, 1, 500000.01, 1000000.00, 340.000000, 0.300000, 0.000000, '2000-01-01', NULL),
(30, 1, 1, 1000000.01, 99999999.99, 490.000000, 0.180000, 0.000000, '2000-01-01', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios_usss020525`
--

CREATE TABLE `usuarios_usss020525` (
  `idUsuario` int(10) NOT NULL,
  `usuario` char(35) NOT NULL,
  `clave` char(35) NOT NULL,
  `nombre` char(85) NOT NULL,
  `direccion` char(100) NOT NULL,
  `telefono` char(9) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios_usss020525`
--

INSERT INTO `usuarios_usss020525` (`idUsuario`, `usuario`, `clave`, `nombre`, `direccion`, `telefono`) VALUES
(1, 'admin', '21232f297a57a5a743894a0e4a801fc3', 'Administrador', 'Usulutan', '0000-0000'),
(2, 'Auditor', '81dc9bdb52d04dc20036dbd8313ed055', 'Juan', 'San Jorge', '7271-2271'),
(3, 'UGBUSU', 'b213b2cc51532bd0a44ca42bedc5c23b', 'Luis', 'San Jorge', '2222-2222');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`idCliente`);

--
-- Indices de la tabla `periodos`
--
ALTER TABLE `periodos`
  ADD PRIMARY KEY (`idPeriodo`),
  ADD KEY `idx_cliente_producto_fechas` (`idCliente`,`idProducto`,`desde`,`hasta`),
  ADD KEY `idProducto` (`idProducto`),
  ADD KEY `idTarifa` (`idTarifa`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`idProducto`),
  ADD UNIQUE KEY `codigo` (`codigo`);

--
-- Indices de la tabla `tarifas`
--
ALTER TABLE `tarifas`
  ADD PRIMARY KEY (`idTarifa`),
  ADD KEY `idProducto` (`idProducto`);

--
-- Indices de la tabla `usuarios_usss020525`
--
ALTER TABLE `usuarios_usss020525`
  ADD PRIMARY KEY (`idUsuario`),
  ADD UNIQUE KEY `usuario` (`usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `idCliente` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `periodos`
--
ALTER TABLE `periodos`
  MODIFY `idPeriodo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `idProducto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `tarifas`
--
ALTER TABLE `tarifas`
  MODIFY `idTarifa` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT de la tabla `usuarios_usss020525`
--
ALTER TABLE `usuarios_usss020525`
  MODIFY `idUsuario` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `periodos`
--
ALTER TABLE `periodos`
  ADD CONSTRAINT `periodos_ibfk_1` FOREIGN KEY (`idCliente`) REFERENCES `clientes` (`idCliente`),
  ADD CONSTRAINT `periodos_ibfk_2` FOREIGN KEY (`idProducto`) REFERENCES `productos` (`idProducto`),
  ADD CONSTRAINT `periodos_ibfk_3` FOREIGN KEY (`idTarifa`) REFERENCES `tarifas` (`idTarifa`);

--
-- Filtros para la tabla `tarifas`
--
ALTER TABLE `tarifas`
  ADD CONSTRAINT `tarifas_ibfk_1` FOREIGN KEY (`idProducto`) REFERENCES `productos` (`idProducto`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
