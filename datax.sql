/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 50743
 Source Host           : 192.168.0.21:3306
 Source Schema         : datax

 Target Server Type    : MySQL
 Target Server Version : 50743
 File Encoding         : 65001

 Date: 22/02/2024 16:31:31
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for datax_config
-- ----------------------------
DROP TABLE IF EXISTS `datax_config`;
CREATE TABLE `datax_config`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '类型，支持不能的源和目的',
  `src_table_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `json_id` int(11) NULL DEFAULT NULL COMMENT '抽取模板id，和datax_json的id关联',
  `des_table_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `split_pk_field` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `relation` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `dcondition` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `src_table_column` varchar(8000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `des_table_column` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `server_type` int(255) NULL DEFAULT NULL COMMENT '机器执行好，不同机器可以并行执行不同的表',
  `ordernum` decimal(6, 3) NULL DEFAULT NULL COMMENT '执行顺序，如1.666',
  `status` int(11) NULL DEFAULT 0 COMMENT '0是有效，1是无效',
  `etl_type` int(11) NULL DEFAULT NULL COMMENT '抽取类型：0，全量，1，按天增量  2, 特殊增量，etl_column存条件',
  `etl_column` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '增量字段',
  `etl_num` int(11) NULL DEFAULT 0 COMMENT '抽取次数',
  `last_etl_date` date NULL DEFAULT NULL COMMENT '抽取日期',
  `note` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_name`(`src_table_name`, `json_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 84 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for datax_config_repair
-- ----------------------------
DROP TABLE IF EXISTS `datax_config_repair`;
CREATE TABLE `datax_config_repair`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '类型，支持不能的源和目的',
  `json_id` int(11) NULL DEFAULT NULL COMMENT '抽取模板id，和datax_json的id关联',
  `src_table_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `des_table_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `split_pk_field` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `relation` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `dcondition` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `src_table_column` varchar(8000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `des_table_column` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `server_type` int(255) NULL DEFAULT NULL COMMENT '机器执行好，不同机器可以并行执行不同的表',
  `ordernum` decimal(5, 3) NULL DEFAULT NULL COMMENT '执行顺序，如1.666',
  `status` int(11) NULL DEFAULT 0 COMMENT '0是有效，1是无效',
  `etl_type` int(11) NULL DEFAULT NULL COMMENT '抽取类型：0，全量，1，增量',
  `etl_column` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '增量字段',
  `etl_num` int(11) NULL DEFAULT 0 COMMENT '抽取次数',
  `last_etl_date` date NULL DEFAULT NULL COMMENT '抽取日期',
  `note` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx`(`src_table_name`, `json_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 88 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for datax_etl_error
-- ----------------------------
DROP TABLE IF EXISTS `datax_etl_error`;
CREATE TABLE `datax_etl_error`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `datax_id` int(11) NULL DEFAULT NULL COMMENT '任务表id',
  `table_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `msg` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 51 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for datax_json
-- ----------------------------
DROP TABLE IF EXISTS `datax_json`;
CREATE TABLE `datax_json`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `df_json` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '全量配置json模板文件全名称',
  `di_json` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '增量配置json模板文件全名称',
  `source_dbname` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '源库',
  `target_dbname` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '目标库',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for datax_log
-- ----------------------------
DROP TABLE IF EXISTS `datax_log`;
CREATE TABLE `datax_log`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `table_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '表名',
  `dt` date NULL DEFAULT NULL COMMENT '抽取日期',
  `datax_id` int(11) NULL DEFAULT NULL COMMENT '任务表id',
  `starttime` datetime NULL DEFAULT NULL COMMENT '任务开始时间',
  `endtime` datetime NULL DEFAULT NULL COMMENT '任务结束时间',
  `etl_endtime` date NULL DEFAULT NULL COMMENT 'etl 截止日期',
  `etl_begintime` date NULL DEFAULT NULL COMMENT 'etl 抽取的开始日期',
  `net_num` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '流量',
  `is_finished` tinyint(4) NULL DEFAULT 0 COMMENT '是否已经完成，0：未完成 1： 完成',
  `time_num` int(11) NULL DEFAULT NULL COMMENT '任务总计耗时(秒)',
  `speed_num` int(11) NULL DEFAULT NULL COMMENT '记录写入速度（行/秒)',
  `read_num` bigint(20) NULL DEFAULT NULL COMMENT '读出记录总数',
  `error_num` int(11) NULL DEFAULT NULL COMMENT '读写失败总数',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5763 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for datax_row_error
-- ----------------------------
DROP TABLE IF EXISTS `datax_row_error`;
CREATE TABLE `datax_row_error`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `error_num` int(11) NULL DEFAULT NULL COMMENT '出错行数',
  `total_num` int(255) NULL DEFAULT NULL COMMENT '总行数',
  `datax_id` int(11) NULL DEFAULT NULL COMMENT '任务表id',
  `table_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '源表名',
  `msg` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '出错信息',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 38 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;


INSERT INTO `datax`.`datax_config` (`id`, `type`, `src_table_name`, `json_id`, `des_table_name`, `split_pk_field`, `relation`, `dcondition`, `src_table_column`, `des_table_column`, `server_type`, `ordernum`, `status`, `etl_type`, `etl_column`, `etl_num`, `last_etl_date`, `note`, `create_time`) VALUES (2, '1', 'dbo.a', 1, 'ods.ods_a', 'a1', 't', '1=1', 'a1,a2,a3,a4,a5 ', '*', 0, 2.000, 0, 0, '', 81, '2024-01-22', '测试表', '2023-10-20 15:34:28');


INSERT INTO `datax`.`datax_json` (`id`, `df_json`, `di_json`, `source_dbname`, `target_dbname`, `create_time`) VALUES (1, 'oracle_ps_table_df_job.json', 'oracle_ps_table_di_job.json', 'Oracle', 'progresql在数据仓库', '2023-11-26 12:06:00');
