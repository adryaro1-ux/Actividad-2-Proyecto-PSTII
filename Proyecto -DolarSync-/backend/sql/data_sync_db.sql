-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 08, 2026 at 08:16 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `data_sync_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `audit_logs`
--

CREATE TABLE `audit_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `accion` varchar(255) DEFAULT NULL,
  `detalles` text DEFAULT NULL,
  `fecha_hora` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `audit_logs`
--

INSERT INTO `audit_logs` (`id`, `user_id`, `username`, `accion`, `detalles`, `fecha_hora`) VALUES
(1, 1, 'Soport_LogicoSH', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 09:19:39'),
(4, 1, 'Soport_LogicoSH', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 09:33:44'),
(5, 1, 'Soport_LogicoSH', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 09:33:50'),
(6, NULL, 'Soport_LogicoSH', 'CIERRE DE SESIÓN', 'Sesión terminada (Cierre de pestaña/navegador)', '2026-02-04 09:35:19'),
(7, 1, 'Soport_LogicoSH', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 12:28:42'),
(8, 3, 'Arelis Camacaro', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 12:28:51'),
(9, 3, 'Arelis Camacaro', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 12:35:23'),
(10, 5, 'Gabriel Alfonso', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 12:35:30'),
(11, 5, 'Gabriel Alfonso', 'CREACIÓN', 'Reporte creado para paciente: Vivian Cortez', '2026-02-04 13:03:16'),
(12, 5, 'Gabriel Alfonso', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 13:11:28'),
(13, 4, 'Luis Garrido', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 13:11:58'),
(14, 4, 'Luis Garrido', 'EDICIÓN', 'Editó reporte ID: 34 (Paciente: Vivian Cortez)', '2026-02-04 13:12:13'),
(15, 4, 'Luis Garrido', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 13:13:49'),
(16, 3, 'Arelis Camacaro', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 13:13:56'),
(17, 3, 'Arelis Camacaro', 'Descarga de Reporte', 'PDF: 10.100.010', '2026-02-04 13:14:06'),
(18, 3, 'Arelis Camacaro', 'Descarga de Reporte', 'PDF: 10.100.010', '2026-02-04 13:19:38'),
(19, 3, 'Arelis Camacaro', 'Descarga de Reporte', 'PDF: 10.100.010', '2026-02-04 13:19:38'),
(20, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 13:20:17'),
(21, 3, 'Arelis Camacaro', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 14:02:02'),
(22, 1, 'Soport_LogicoSH', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 19:46:42'),
(23, 1, 'Soport_LogicoSH', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 19:57:58'),
(24, 5, 'Gabriel Alfonso', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 19:58:06'),
(25, 5, 'Gabriel Alfonso', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 20:59:04'),
(26, 5, 'Gabriel Alfonso', 'CREACIÓN', 'Reporte creado para paciente: Mario Herrera', '2026-02-04 21:29:19'),
(27, 5, 'Gabriel Alfonso', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 21:29:31'),
(28, 4, 'Luis Garrido', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 21:29:39'),
(29, 4, 'Luis Garrido', 'EDICIÓN', 'Editó reporte ID: 35 (Paciente: Mario Herrera)', '2026-02-04 21:29:57'),
(30, 4, 'Luis Garrido', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 21:30:05'),
(31, 3, 'Arelis Camacaro', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 21:30:13'),
(32, 3, 'Arelis Camacaro', 'Descarga de Reporte', 'PDF: 27.432.102', '2026-02-04 21:30:20'),
(33, 3, 'Arelis Camacaro', 'Descarga de Reporte', 'PDF: 27.432.102', '2026-02-04 21:31:39'),
(34, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 21:31:50'),
(35, NULL, 'Arelis Camacaro', 'CIERRE DE SESIÓN', 'Sesión terminada (Cierre de pestaña/navegador)', '2026-02-04 22:08:59'),
(36, NULL, 'Arelis Camacaro', 'CIERRE DE SESIÓN', 'Sesión terminada (Cierre de pestaña/navegador)', '2026-02-04 22:12:40'),
(37, NULL, 'Arelis Camacaro', 'CIERRE DE SESIÓN', 'Sesión terminada (Cierre de pestaña/navegador)', '2026-02-04 22:12:42'),
(38, NULL, 'Arelis Camacaro', 'CIERRE DE SESIÓN', 'Sesión terminada (Cierre de pestaña/navegador)', '2026-02-04 22:12:44'),
(39, NULL, 'Arelis Camacaro', 'CIERRE DE SESIÓN', 'Sesión terminada (Cierre de pestaña/navegador)', '2026-02-04 22:15:03'),
(40, 3, 'Arelis Camacaro', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 22:15:04'),
(41, 3, 'Arelis Camacaro', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 22:15:40'),
(42, 3, 'Arelis Camacaro', 'EDICIÓN', 'Editó reporte ID: 35 (Paciente: Mario Herrera)', '2026-02-04 22:15:52'),
(43, NULL, 'Arelis Camacaro', 'CIERRE DE SESIÓN', 'Sesión terminada (Cierre de pestaña/navegador)', '2026-02-04 22:20:23'),
(44, 3, 'Arelis Camacaro', 'EDICIÓN', 'Editó reporte ID: 35 (Paciente: Mario Herrera)', '2026-02-04 22:20:55'),
(45, 3, 'Arelis Camacaro', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 22:23:24'),
(46, 1, 'Soport_LogicoSH', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 22:23:29'),
(47, 1, 'Soport_LogicoSH', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 22:24:41'),
(48, 9, 'Paola Quintero', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 22:28:26'),
(49, 9, 'Paola Quintero', 'CREACIÓN', 'Reporte creado para paciente: Jeremias Rosas', '2026-02-04 22:30:15'),
(50, 9, 'Paola Quintero', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 22:30:20'),
(51, 3, 'Arelis Camacaro', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 22:30:26'),
(52, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 22:30:47'),
(53, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 22:38:23'),
(54, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 22:42:21'),
(55, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 22:45:15'),
(56, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 22:47:10'),
(57, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 22:47:24'),
(58, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 22:48:51'),
(59, 3, 'Arelis Camacaro', 'Exportación Excel', 'Descargó reporte de fecha: 2026-02-04', '2026-02-04 22:51:22'),
(60, 3, 'Arelis Camacaro', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-04 23:04:09'),
(61, 1, 'Soport_LogicoSH', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-04 23:36:54'),
(62, 1, 'Soport_LogicoSH', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-08 12:34:06'),
(63, 1, 'Soport_LogicoSH', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-08 12:35:28'),
(64, 3, 'Arelis Camacaro', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-08 12:35:41'),
(65, 3, 'Arelis Camacaro', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-08 12:35:53'),
(66, 1, 'Soport_LogicoSH', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-08 12:36:00'),
(67, 1, 'Soport_LogicoSH', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-08 12:37:00'),
(68, 12, 'Jose Esperanza', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-08 12:37:08'),
(69, 12, 'Jose Esperanza', 'CREACIÓN', 'Reporte creado para paciente: Felipe Villareal', '2026-02-08 12:38:15'),
(70, 12, 'Jose Esperanza', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-08 12:38:21'),
(71, 5, 'Gabriel Alfonso', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-08 12:38:27'),
(72, 5, 'Gabriel Alfonso', 'CREACIÓN', 'Reporte creado para paciente: Wendy Leal', '2026-02-08 12:39:51'),
(73, 5, 'Gabriel Alfonso', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-08 12:40:00'),
(74, 4, 'Luis Garrido', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-08 12:40:07'),
(75, 4, 'Luis Garrido', 'Cierre de Sesión', 'Sesión finalizada por el usuario', '2026-02-08 12:40:59'),
(76, 1, 'Soport_LogicoSH', 'Inicio de Sesión', 'Acceso exitoso', '2026-02-08 13:48:02');

-- --------------------------------------------------------

--
-- Table structure for table `reports`
--

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `numero_poliza` varchar(50) DEFAULT NULL,
  `nombre_apellido` varchar(255) NOT NULL,
  `cedula` varchar(50) NOT NULL,
  `contratante` varchar(255) NOT NULL,
  `num_control` varchar(50) NOT NULL,
  `proveedor` varchar(255) NOT NULL,
  `estado` varchar(100) NOT NULL,
  `patologia` varchar(255) NOT NULL,
  `monto_bs` decimal(10,2) NOT NULL,
  `monto_dolar` decimal(10,2) DEFAULT NULL,
  `tratamiento` varchar(255) NOT NULL,
  `observaciones` text DEFAULT NULL,
  `fecha_creado` datetime DEFAULT current_timestamp(),
  `fecha_modificado` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `reports`
--

INSERT INTO `reports` (`id`, `user_id`, `numero_poliza`, `nombre_apellido`, `cedula`, `contratante`, `num_control`, `proveedor`, `estado`, `patologia`, `monto_bs`, `monto_dolar`, `tratamiento`, `observaciones`, `fecha_creado`, `fecha_modificado`) VALUES
(34, 5, '0000', 'Vivian Cortez', '10.100.010', 'xxxxxx', '2022', 'Angelitos S.A', 'Distrito Capital', 'xxxxxxx', 45009.60, 120.00, 'N/A', 'Ninguna', '2026-02-04 13:03:15', '2026-02-04 13:12:12'),
(35, 5, '0001', 'Mario Herrera', '27.432.102', 'xxxxxx', '2030', 'Alta Villa', 'Distrito Capital', 'xxxxxxx', 32169.10, 85.00, 'xxxxxx', 'En proceso', '2026-02-04 21:29:19', '2026-02-04 22:20:55'),
(36, 9, '0002', 'Jeremias Rosas', '26.041.130', 'xxxxxx', '2015', 'Alta Villa', 'Distrito Capital', 'xxxxxxx', 75313.54, 199.00, 'N/A', 'Ninguna', '2026-02-04 22:30:15', '2026-02-04 22:30:15'),
(37, 12, '0003', 'Felipe Villareal', '22.541.109', 'xxxxxx', '2098', 'Alta Villa', 'Distrito Capital', 'xxxxxxx', 85322.66, 222.99, 'N/A', 'En proceso', '2026-02-08 12:38:15', '2026-02-08 12:38:15'),
(38, 5, '0004', 'Wendy Leal', '29.413.236', 'xxxxxx', '2023', 'KAILA S.A', 'Distrito Capital', 'xxxxxxx', 42089.30, 110.00, 'xxxxxx', 'En proceso', '2026-02-08 12:39:51', '2026-02-08 12:39:51');

-- --------------------------------------------------------

--
-- Table structure for table `tipo_cambio`
--

CREATE TABLE `tipo_cambio` (
  `id` int(11) NOT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  `fecha_hora` datetime NOT NULL DEFAULT current_timestamp(),
  `moneda` varchar(10) DEFAULT 'USD',
  `fuente` varchar(50) DEFAULT 'BCV',
  `activo` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tipo_cambio`
--

INSERT INTO `tipo_cambio` (`id`, `valor`, `fecha_hora`, `moneda`, `fuente`, `activo`) VALUES
(74, 223.65, '2025-10-30 17:46:20', 'USD', 'BCV', 1),
(75, 221.74, '2025-10-29 17:50:20', 'USD', 'BCV', 1),
(76, 223.96, '2025-10-31 21:25:41', 'USD', 'BCV', 1),
(77, 226.13, '2025-11-04 19:27:33', 'USD', 'BCV', 1),
(78, 231.09, '2025-11-11 09:22:36', 'USD', 'BCV', 1),
(79, 233.56, '2025-11-13 09:26:55', 'USD', 'BCV', 1),
(80, 234.87, '2025-11-14 09:46:32', 'USD', 'BCV', 1),
(81, 236.84, '2025-11-18 09:39:34', 'USD', 'BCV', 1),
(82, 237.75, '2025-11-19 09:54:19', 'USD', 'BCV', 1),
(83, 243.11, '2025-11-25 09:49:14', 'USD', 'BCV', 1),
(84, 249.20, '2025-12-03 09:35:29', 'USD', 'BCV', 1),
(85, 262.10, '2025-12-10 08:23:02', 'USD', 'BCV', 1),
(86, 330.38, '2026-01-13 10:11:37', 'USD', 'BCV', 1),
(87, 336.46, '2026-01-14 10:47:56', 'USD', 'BCV', 1),
(88, 372.11, '2026-02-04 10:42:08', 'USD', 'BCV', 1),
(90, 375.08, '2026-02-04 12:15:11', 'USD', 'BCV', 1),
(119, 378.46, '2026-02-04 21:59:57', 'USD', 'BCV', 1),
(120, 382.63, '2026-02-08 12:34:07', 'USD', 'BCV', 1);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(80) NOT NULL,
  `ultimo_login` datetime DEFAULT NULL,
  `rol` varchar(50) NOT NULL DEFAULT 'Operador',
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `fecha_registro` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `ultimo_login`, `rol`, `activo`, `fecha_registro`) VALUES
(1, 'Soport_LogicoSH', 'adminSH', '2026-02-08 13:48:02', 'Administrador', 1, '2025-12-10 09:55:34'),
(3, 'Arelis Camacaro', 'Relisca001', '2026-02-08 12:35:41', 'Gerente', 1, '2025-12-10 09:55:34'),
(4, 'Luis Garrido', 'LuisSH002', '2026-02-08 12:40:07', 'Coordinador', 1, '2026-01-14 11:15:52'),
(5, 'Gabriel Alfonso', 'Gbriel003', '2026-02-08 12:38:27', 'Operador', 1, '2026-01-14 12:34:26'),
(6, 'Ramona Carrillo', 'Ramcar004', '2026-02-03 11:18:28', 'Operador', 1, '2026-01-14 12:35:01'),
(9, 'Paola Quintero', 'Paquin005', '2026-02-04 22:28:26', 'Operador', 1, '2026-01-15 22:22:12'),
(11, 'Rubi Garcia', 'Ggarcia008', '2026-01-19 13:00:13', 'Coordinador', 0, '2026-01-19 12:57:17'),
(12, 'Jose Esperanza', 'JespSH009', '2026-02-08 12:37:08', 'Operador', 1, '2026-02-02 23:46:49');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `tipo_cambio`
--
ALTER TABLE `tipo_cambio`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `audit_logs`
--
ALTER TABLE `audit_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=77;

--
-- AUTO_INCREMENT for table `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `tipo_cambio`
--
ALTER TABLE `tipo_cambio`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=121;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
