-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Feb 25, 2015 at 12:21 PM
-- Server version: 5.5.40-MariaDB-0ubuntu0.14.04.1
-- PHP Version: 5.5.9-1ubuntu4.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `auroratip`
--
CREATE DATABASE IF NOT EXISTS `auroratip` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `auroratip`;

-- --------------------------------------------------------

--
-- Table structure for table `deposits`
--

CREATE TABLE IF NOT EXISTS `deposits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `amount` decimal(16,8) DEFAULT NULL,
  `datetime` datetime NOT NULL,
  `pubkey` varchar(36) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `deposit_addresses`
--

CREATE TABLE IF NOT EXISTS `deposit_addresses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `deposit_pubkey` varchar(36) COLLATE utf8_unicode_ci NOT NULL,
  `received_to_date` decimal(16,8) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=19 ;

-- --------------------------------------------------------

--
-- Table structure for table `exchange_rate`
--

CREATE TABLE IF NOT EXISTS `exchange_rate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstcurrency` varchar(4) COLLATE utf8_unicode_ci DEFAULT NULL,
  `secondcurrency` varchar(4) COLLATE utf8_unicode_ci DEFAULT NULL,
  `rate` decimal(16,8) DEFAULT NULL,
  `datetime` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=395 ;

-- --------------------------------------------------------

--
-- Table structure for table `last_post`
--

CREATE TABLE IF NOT EXISTS `last_post` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category` varchar(2) COLLATE utf8_unicode_ci NOT NULL,
  `thread_id` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `updated_datetime` datetime NOT NULL,
  `created_datetime` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=402 ;

-- --------------------------------------------------------

--
-- Table structure for table `pool_transactions`
--

CREATE TABLE IF NOT EXISTS `pool_transactions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `amount` decimal(16,8) NOT NULL,
  `pubkey` varchar(36) COLLATE utf8_unicode_ci NOT NULL,
  `datetime` datetime NOT NULL,
  `txid` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tip_transactions`
--

CREATE TABLE IF NOT EXISTS `tip_transactions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `thread_id` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `sender_username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `receive_username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `amount` decimal(16,8) DEFAULT NULL,
  `datetime` datetime NOT NULL,
  `accepted` tinyint(1) NOT NULL,
  `withdrawn` tinyint(1) NOT NULL,
  `rejected` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=27 ;

-- --------------------------------------------------------

--
-- Table structure for table `unregister_requests`
--

CREATE TABLE IF NOT EXISTS `unregister_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `thread_id` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `datetime` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `user_data`
--

CREATE TABLE IF NOT EXISTS `user_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `regdate` datetime NOT NULL,
  `balance` decimal(16,8) DEFAULT NULL,
  `pubkey` varchar(36) COLLATE utf8_unicode_ci DEFAULT NULL,
  `reg_thread_id` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `pool` tinyint(1) NOT NULL,
  `registered` tinyint(1) DEFAULT NULL,
  `email` varchar(80) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=19 ;

-- --------------------------------------------------------

--
-- Table structure for table `withdrawls`
--

CREATE TABLE IF NOT EXISTS `withdrawls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `thread_id` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `receive_username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `receive_pubkey` varchar(36) COLLATE utf8_unicode_ci NOT NULL,
  `amount` decimal(16,8) DEFAULT NULL,
  `datetime` datetime NOT NULL,
  `txid` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
