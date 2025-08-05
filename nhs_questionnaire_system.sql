/*
 Navicat Premium Dump SQL

 Source Server         : newmysql
 Source Server Type    : MySQL
 Source Server Version : 90200 (9.2.0)
 Source Host           : localhost:3306
 Source Schema         : nhs_questionnaire_system

 Target Server Type    : MySQL
 Target Server Version : 90200 (9.2.0)
 File Encoding         : 65001

 Date: 20/07/2025 13:56:57
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version`  (
  `version_num` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  PRIMARY KEY (`version_num`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_520_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO `alembic_version` VALUES ('4ac507a7e148');

-- ----------------------------
-- Table structure for questionnaire
-- ----------------------------
DROP TABLE IF EXISTS `questionnaire`;
CREATE TABLE `questionnaire`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `score` float NULL DEFAULT NULL,
  `level` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NULL DEFAULT NULL,
  `answers` json NULL,
  `submitted_at` datetime NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `questionnaire_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_520_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of questionnaire
-- ----------------------------
INSERT INTO `questionnaire` VALUES (1, 1, 'dasi', 58.2, 'Universal', '{\"q1\": \"2.75\", \"q2\": \"1.75\", \"q3\": \"2.75\", \"q4\": \"5.5\", \"q5\": \"8\", \"q6\": \"2.7\", \"q7\": \"3.5\", \"q8\": \"8\", \"q9\": \"4.5\", \"q10\": \"5.25\", \"q11\": \"6\", \"q12\": \"7.5\", \"dasi_total\": \"50.7\", \"mets_score\": \"8.97\"}', '2025-07-20 05:01:33', 'completed');
INSERT INTO `questionnaire` VALUES (2, 1, 'phq4', 2, 'Universal', '{\"q1\": \"0\", \"q2\": \"1\", \"q3\": \"1\", \"q4\": \"0\", \"phq4_total\": \"2\"}', '2025-07-20 05:01:40', 'completed');
INSERT INTO `questionnaire` VALUES (3, 1, 'pgsga', 3, 'Targeted', '{\"height\": \"160\", \"activity\": \"0\", \"symptoms\": [\"1\", \"1\"], \"food_type\": \"1\", \"food_intake\": \"0\", \"pain_detail\": \"leg\", \"other_detail\": \"\", \"weight_1month\": \"50\", \"weight_6month\": \"49\", \"weight_change\": \"0\", \"current_weight\": \"50\"}', '2025-07-20 05:02:22', 'completed');
INSERT INTO `questionnaire` VALUES (4, 1, 'dasi', 52.2, 'Universal', '{\"q1\": \"2.75\", \"q2\": \"1.75\", \"q3\": \"2.75\", \"q4\": \"5.5\", \"q5\": \"8\", \"q6\": \"2.7\", \"q7\": \"3.5\", \"q8\": \"8\", \"q9\": \"4.5\", \"q10\": \"5.25\", \"q11\": \"0\", \"q12\": \"7.5\", \"dasi_total\": \"44.7\", \"mets_score\": \"8.23\"}', '2025-07-20 05:03:40', 'completed');
INSERT INTO `questionnaire` VALUES (5, 1, 'dasi', 47, 'Universal', '{\"q1\": \"2.75\", \"q2\": \"0\", \"q3\": \"2.75\", \"q4\": \"5.5\", \"q5\": \"8\", \"q6\": \"2.7\", \"q7\": \"0\", \"q8\": \"8\", \"q9\": \"4.5\", \"q10\": \"5.25\", \"q11\": \"0\", \"q12\": \"7.5\", \"dasi_total\": \"39.5\", \"mets_score\": \"7.59\"}', '2025-07-20 05:04:04', 'completed');

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `gender` enum('male','female','other') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `date_of_birth` date NOT NULL,
  `medical_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NULL DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `role` enum('user','nurse','doctor') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `medical_id`(`medical_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_520_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'Amy', 'female', '2021-02-10', '35414', NULL, '626317406@qq.com', '7776578998', '$2b$12$Q3fIywvReQ1q5XFzsNrPKezQu/rO5gY6bFbAepCf0nbWqRtJCmUi2', 'user', '2025-07-19 16:18:52');
INSERT INTO `user` VALUES (2, 'Mike', 'male', '2020-02-23', '6263', NULL, '15034688782@163.com', '7776578998', '$2b$12$EvoM6cDiENpjz4hYdzpLw.uxB1Y0bz.ooIuOW/GwtcBn3t0DSigjC', 'user', '2025-07-20 04:46:29');

SET FOREIGN_KEY_CHECKS = 1;
