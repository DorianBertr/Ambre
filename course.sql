-- Base de données : `course`

-- --------------------------------------------------------

-- Structure de la table `user`

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user` (
  `id_user` bigint NOT NULL PRIMARY KEY,
  `creation` date NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
INSERT INTO `user` (id_user) VALUES
 (385088777837871116);
-- --------------------------------------------------------

-- Structure de la table `perf`

DROP TABLE IF EXISTS `perf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `perf` (
  `id_perf` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `id_user` bigint NOT NULL,
  FOREIGN KEY (id_user) REFERENCES user(id_user),
  `date_course` date NULL,
  `distance` float NOT NULL,
  `duree` float NOT NULL,
  `vitesse_moy` float NULL,
  `lieu` varchar(100) NULL,
  `meteo` varchar(100) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
INSERT INTO `perf` (id_user, date_course, distance, duree, vitesse_moy, lieu, meteo) VALUES
 (385088777837871116, '2024-03-10', 2.76, 20.37, 8, 'Étang de Cloyes', 'Nuageux'),
 (385088777837871116, '2024-03-12', 2.66, 17.37, 9, 'Étang de Cloyes', 'Nuageux');
-- --------------------------------------------------------

-- Structure de la table `objectif`

DROP TABLE IF EXISTS `objectif`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `objectif` (
  `id_objectif` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `id_user` bigint NOT NULL,
  FOREIGN KEY (id_user) REFERENCES user(id_user),
  `nom` varchar(100) NOT NULL,
  `valid` boolean NOT NULL default False,
  `date_valid` date NULL,
  `actuel` int NOT NULL DEFAULT 1,
  `creation` date NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
-- --------------------------------------------------------



COMMIT;
