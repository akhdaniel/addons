-- phpMyAdmin SQL Dump
-- version 4.2.7.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 06, 2016 at 06:59 AM
-- Server version: 5.6.20
-- PHP Version: 5.5.15

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `spc`
--

-- --------------------------------------------------------

--
-- Table structure for table `detil_tagihan`
--

CREATE TABLE IF NOT EXISTS `detil_tagihan` (
  `id_record_detil_tagihan` varchar(30) NOT NULL,
  `id_record_tagihan` varchar(30) DEFAULT NULL,
  `urutan_detil_tagihan` int(11) DEFAULT NULL,
  `kode_jenis_biaya` varchar(10) DEFAULT NULL,
  `label_jenis_biaya` varchar(10) DEFAULT NULL,
  `label_jenis_biaya_panjang` varchar(255) DEFAULT NULL,
  `nilai_tagihan` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `detil_tagihan`
--

INSERT INTO `detil_tagihan` (`id_record_detil_tagihan`, `id_record_tagihan`, `urutan_detil_tagihan`, `kode_jenis_biaya`, `label_jenis_biaya`, `label_jenis_biaya_panjang`, `nilai_tagihan`) VALUES
('2', 'SAJ/2016/0002', 2, '0', 'Service', 'Service', 75),
('6', 'SAJ/2016/0004', 6, '0', 'Service', 'Service', 75);

-- --------------------------------------------------------

--
-- Table structure for table `pembayaran`
--

CREATE TABLE IF NOT EXISTS `pembayaran` (
  `id_record_pembayaran` varchar(30) NOT NULL DEFAULT '',
  `id_record_tagihan` varchar(30) DEFAULT NULL,
  `waktu_transaksi` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `nomor_pembayaran` varchar(30) DEFAULT NULL,
  `kode_unik_transaksi_bank` varchar(30) DEFAULT NULL,
  `waktu_transaksi_bank` varchar(20) DEFAULT NULL,
  `kode_bank` varchar(10) DEFAULT NULL,
  `kanal_bayar_bank` varchar(20) DEFAULT NULL,
  `kode_terminal_bank` varchar(20) DEFAULT NULL,
  `total_nilai_pembayaran` double DEFAULT NULL,
  `status_pembayaran` int(11) DEFAULT NULL,
  `id_record_rekonsiliasi` varchar(30) DEFAULT NULL,
  `id_record_settlement` varchar(30) DEFAULT NULL,
  `billref` varchar(30) DEFAULT NULL,
  `metode_pembayaran` varchar(10) DEFAULT NULL,
  `catatan` varchar(200) DEFAULT NULL,
  `key_val_1` varchar(255) DEFAULT NULL,
  `key_val_2` varchar(255) DEFAULT NULL,
  `key_val_3` varchar(255) DEFAULT NULL,
  `key_val_4` varchar(255) DEFAULT NULL,
  `key_val_5` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `pembayaran`
--

INSERT INTO `pembayaran` (`id_record_pembayaran`, `id_record_tagihan`, `waktu_transaksi`, `nomor_pembayaran`, `kode_unik_transaksi_bank`, `waktu_transaksi_bank`, `kode_bank`, `kanal_bayar_bank`, `kode_terminal_bank`, `total_nilai_pembayaran`, `status_pembayaran`, `id_record_rekonsiliasi`, `id_record_settlement`, `billref`, `metode_pembayaran`, `catatan`, `key_val_1`, `key_val_2`, `key_val_3`, `key_val_4`, `key_val_5`) VALUES
('12', 'SAJ/2016/0002', '2016-01-26 21:33:42', '100000', '10', '10', '100', '100', '100', 75, 0, '0', '0', '0', '0', '0', '1', NULL, NULL, NULL, NULL),
('423989', 'SAJ/2016/0001', '2016-01-27 08:25:47', '8432', '538', '58390', '5380', '53809', '58309', 75, 5398, '53809', '538092', '53809', '5380', '53809', '1', NULL, NULL, NULL, NULL),
('4239890', 'SAJ/2016/0003', '2016-01-27 08:25:47', '8432', '538', '58390', '5380', '53809', '58309', 75, 5398, '53809', '538092', '53809', '5380', '53809', '1', NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tagihan`
--

CREATE TABLE IF NOT EXISTS `tagihan` (
  `id_record_tagihan` varchar(30) NOT NULL,
  `nomor_pembayaran` varchar(30) DEFAULT NULL,
  `nama` varchar(255) DEFAULT NULL,
  `kode_fakultas` varchar(20) DEFAULT NULL,
  `nama_fakultas` varchar(255) DEFAULT NULL,
  `kode_prodi` varchar(20) DEFAULT NULL,
  `nama_prodi` varchar(255) DEFAULT NULL,
  `kode_periode` varchar(20) DEFAULT NULL,
  `nama_periode` varchar(255) DEFAULT NULL,
  `is_tagihan_aktif` int(11) DEFAULT NULL,
  `waktu_berlaku` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `waktu_berakhir` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `strata` varchar(255) DEFAULT NULL,
  `angkatan` varchar(255) DEFAULT NULL,
  `urutan_antrian` int(11) DEFAULT NULL,
  `total_nilai_tagihan` double DEFAULT NULL,
  `minimal_nilai_pembayaran` double DEFAULT NULL,
  `maksimal_nilai_pembayaran` double DEFAULT NULL,
  `nomor_induk` varchar(30) DEFAULT NULL,
  `pembayaran_atau_voucher` varchar(20) DEFAULT NULL,
  `voucher_nama` varchar(255) DEFAULT NULL,
  `voucher_nama_fakultas` varchar(255) DEFAULT NULL,
  `voucher_nama_prodi` varchar(255) DEFAULT NULL,
  `voucher_nama_periode` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `tagihan`
--

INSERT INTO `tagihan` (`id_record_tagihan`, `nomor_pembayaran`, `nama`, `kode_fakultas`, `nama_fakultas`, `kode_prodi`, `nama_prodi`, `kode_periode`, `nama_periode`, `is_tagihan_aktif`, `waktu_berlaku`, `waktu_berakhir`, `strata`, `angkatan`, `urutan_antrian`, `total_nilai_tagihan`, `minimal_nilai_pembayaran`, `maksimal_nilai_pembayaran`, `nomor_induk`, `pembayaran_atau_voucher`, `voucher_nama`, `voucher_nama_fakultas`, `voucher_nama_prodi`, `voucher_nama_periode`) VALUES
('SAJ/2016/0004', '16/00011', 'john', '16', 'PASCA SARJANA', '52', 'Teknik Elektro S2', '2015', '2015', 1, '2016-04-03 17:00:00', '2016-07-03 17:00:00', 'Magister', '2015', 0, 75, 75, 75, '/', '', '', '', '', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `detil_tagihan`
--
ALTER TABLE `detil_tagihan`
 ADD PRIMARY KEY (`id_record_detil_tagihan`);

--
-- Indexes for table `pembayaran`
--
ALTER TABLE `pembayaran`
 ADD PRIMARY KEY (`id_record_pembayaran`);

--
-- Indexes for table `tagihan`
--
ALTER TABLE `tagihan`
 ADD PRIMARY KEY (`id_record_tagihan`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
