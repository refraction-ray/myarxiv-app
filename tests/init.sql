/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


--
-- Table structure for table `author`
--

DROP TABLE IF EXISTS `author`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `author` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pid` int(11) NOT NULL,
  `author` varchar(50) NOT NULL,
  `authorrank` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pid` (`pid`),
  CONSTRAINT `author_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `paper` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `author`
--

LOCK TABLES `author` WRITE;
ALTER TABLE `author` DISABLE KEYS;
INSERT INTO `author` VALUES (1,1,'Mucong Ding',1),(2,1,'Kwok Yip Szeto',2),(3,2,'P. Mikheenko',1),(4,3,'Boris L. Oksengendler',1),(5,3,'Nigora N. Turaeva',2),(6,3,'Marlen I. Akhmedov',3);
ALTER TABLE `author` ENABLE KEYS;
UNLOCK TABLES;

--
-- Table structure for table `favorite`
--

DROP TABLE IF EXISTS `favorite`;
SET @saved_cs_client     = @@character_set_client ;
SET character_set_client = utf8 ;
CREATE TABLE `favorite` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`),
  KEY `pid` (`pid`),
  CONSTRAINT `favorite_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `user` (`id`),
  CONSTRAINT `favorite_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `paper` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4;
SET character_set_client = @saved_cs_client ;

--
-- Dumping data for table `favorite`
--

LOCK TABLES `favorite` WRITE;
/*!40000 ALTER TABLE `favorite` DISABLE KEYS */;
INSERT INTO `favorite` VALUES (1,1,2);
/*!40000 ALTER TABLE `favorite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interest`
--

DROP TABLE IF EXISTS `interest`;
SET @saved_cs_client     = @@character_set_client ;
SET character_set_client = utf8 ;
CREATE TABLE `interest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `interest` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`),
  CONSTRAINT `interest_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4;
SET character_set_client = @saved_cs_client ;

--
-- Dumping data for table `interest`
--

LOCK TABLES `interest` WRITE;
/*!40000 ALTER TABLE `interest` DISABLE KEYS */;
INSERT INTO `interest` VALUES (1,1,'quant-ph'),(2,1,'cond-mat');
/*!40000 ALTER TABLE `interest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `keyword`
--

DROP TABLE IF EXISTS `keyword`;
SET @saved_cs_client     = @@character_set_client ;
SET character_set_client = utf8 ;
CREATE TABLE `keyword` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `keyword` varchar(100) NOT NULL,
  `weight` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`),
  CONSTRAINT `keyword_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4;
SET character_set_client = @saved_cs_client ;

--
-- Dumping data for table `keyword`
--

LOCK TABLES `keyword` WRITE;
ALTER TABLE `keyword` DISABLE KEYS ;
INSERT INTO `keyword` VALUES (1,1,'quantum computation',1),(2,1,'machine learning',2);
ALTER TABLE `keyword` ENABLE KEYS ;
UNLOCK TABLES;

--
-- Table structure for table `paper`
--

DROP TABLE IF EXISTS `paper`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paper` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `arxivid` varchar(12) CHARACTER SET latin1 NOT NULL,
  `title` varchar(2048) NOT NULL,
  `summary` text NOT NULL,
  `mainsubject` varchar(32) CHARACTER SET latin1 NOT NULL,
  `announce` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_paper_arxivid` (`arxivid`)
) ENGINE=InnoDB AUTO_INCREMENT=532 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paper`
--

LOCK TABLES `paper` WRITE;
/*!40000 ALTER TABLE `paper` DISABLE KEYS */;
INSERT INTO `paper` VALUES (1,'1812.35598','First-passage time distribution for random walks on complex networks  using inverse Laplace transform and mean-field approximation','We obtain an exact formula for the first-passage time probability distribution for random walks on complex networks using inverse Laplace transform.  $\\tau$ is quantum computation and machine learning revolution. ','cond-mat.stat-mech','2018-12-17'),(2,'1812.35602','Possible superconductivity in brain','The unprecedented power of the brain suggests that it may process information quantum-mechanically. Since quantum processing is already achieved in superconducting quantum computers, it may imply that superconductivity is the basis of quantum computation in brain too. Superconductivity could also be responsible for long-term memory. Following these ideas, the paper reviews the progress in the search for superconductors with high critical temperature and tries to answer the question about the superconductivity in brain. It focuses on recent electrical measurements of brain slices, in which graphene was used as a room-temperature quantum mediator, and argues that these measurements could be interpreted as providing evidence of superconductivity in the neural network of mammalian brains. The estimated critical temperature of superconducting network in brain is rather high: 2063 plus-minus 114 K. This work has nothing to do with machine learning ','cond-mat.supr-con','2018-12-17'),(3,'1812.05604','Mechanisms of radiation-induced degradation of hybryd perovskites based  solar cells and ways to increase their radiation tolerance','The basic processes of perovskite radiation resistance are discussed for photo- and high-energy electron irradiation. It is shown that ionization of iodine ions and a staged mechanism of elastic scattering (upon intermediate scattering on light ions of an organic molecule) lead to the formation of a recombination center Ii. The features of ionization degradation of interfaces with both planar and fractal structures are considered. A special type of fractality is identified, and its minimum possible level of photodegradation is predicted. By using the methodology of classical radiation physics, the Hoke effect was also studied, as well as the synergetics of cooperative phenomena in tandem systems. The principal channels for counteracting the radiation degradation of solar cells based on hybrid perovskites have been revealed. ','cond-mat.mes-hall','2018-12-18');
ALTER TABLE `paper` ENABLE KEYS ;
UNLOCK TABLES;

--
-- Table structure for table `subject`
--

DROP TABLE IF EXISTS `subject`;
SET @saved_cs_client     = @@character_set_client ;
SET character_set_client = utf8 ;
CREATE TABLE `subject` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pid` int(11) NOT NULL,
  `subject` varchar(25) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pid` (`pid`),
  CONSTRAINT `subject_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `paper` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=385 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client ;

--
-- Dumping data for table `subject`
--

LOCK TABLES `subject` WRITE;
ALTER TABLE `subject` DISABLE KEYS ;
INSERT INTO `subject` VALUES (1,1,'cs.SI'),(2,2,'cond-mat.mes-hall');
ALTER TABLE `subject` ENABLE KEYS ;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
SET @saved_cs_client     = @@character_set_client ;
SET character_set_client = utf8 ;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(60) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(40) NOT NULL,
  `created_at` datetime NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `admin` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
ALTER TABLE `user` DISABLE KEYS ;
INSERT INTO `user` VALUES (1,'test','test@test.com','edc933e6b7a2a53fd5c6db7d0f1d0f19f312d489','2018-12-21 11:14:36',0,0);
ALTER TABLE `user` ENABLE KEYS ;
UNLOCK TABLES;

--
-- Table structure for table `userinfo`
--

DROP TABLE IF EXISTS `userinfo`;
SET @saved_cs_client     = @@character_set_client ;
SET character_set_client = utf8 ;
CREATE TABLE `userinfo` (
  `noti1` tinyint(1) NOT NULL,
  `noti2` tinyint(1) NOT NULL,
  `noti3` tinyint(1) NOT NULL,
  `img` varchar(512) NOT NULL,
  `verified` tinyint(1) NOT NULL,
  `profile` text NOT NULL,
  `uid` int(11) NOT NULL,
  KEY `uid` (`uid`),
  CONSTRAINT `userinfo_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
SET character_set_client = @saved_cs_client ;

--
-- Dumping data for table `userinfo`
--

LOCK TABLES `userinfo` WRITE;
/*!40000 ALTER TABLE `userinfo` DISABLE KEYS */;
INSERT INTO `userinfo` VALUES (0,0,0,'https://www.gravatar.com/avatar/cdbd6879db41fe9d4919cf5630fa0a2f?d=monsterid',0,'I am the first test user with the correct password input, haha',1);
ALTER TABLE `userinfo` ENABLE KEYS ;
UNLOCK TABLES;
SET TIME_ZONE=@OLD_TIME_ZONE ;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
