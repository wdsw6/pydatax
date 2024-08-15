1，在MySQL5.6+，创建配置数据库datax，并执行datax.sql （可以是其他类型数据库，datax库建表语句修改，和python3驱动连接，修改很方便）
2，在CentOS机器安装Python3.6+, 同时pip3安装pymysql，同时下载最新的Datax
    安装Datax目录：/opt/module/datax   （需安装jdk1.8+，并/etc/profile配置jdk）
3，json配置文件目录：/opt/module/datax/job/json
     配置抽取数据库源和目的库的IP，账号和密码
     oracle_ps_table_df_job.json： 单个库抽取oracle数据到postgresql全量json模板
     oracle_ps_table_df_job.json： 单个库抽取oracle数据到postgresql增量json模板
     oracle_gp_table_df_job.json：9个库同时抽取oracle数据到greeplum全量json模板
4，pydatax.py的执行目录： /opt/python3/pydatax.py
5，配置MySQL的：datax_config表
       抽取一个表，写入datax_config该表行一条数据，
       配置
         源表名：src_table_name
         目标表名：des_table_name
         主键：split_pk_field（datax会忽略，无意义）
         json模板id： json_id  对应 datax_json表的主键id
         别名：relation
         where条件：dcondition
         src_table_column： 需要源表字段（多字段用逗号分开）
         des_table_column： 为*(确保目标表的字段和个数和src_table_column的一致）
         server_type： 服务器器类型，预留多台机器并行抽取
         ordernum： 抽取顺序，最小的最先抽取，有3个小数
         status： 1是无效，0有效
         etl_type： 抽取类型  0：全量 ，1：增量（按etl_column的字段+昨天时间，增量抽取），2：特殊条件（按etl_column的条件抽取）
        last_etl_date： 上一次etl抽取日期
        note：备注
6，pyrepair.py和pydatax.py代码基本一样，就其取的配置表是datax_config_repair，表结构和datax_config一样，主要是用来首次初始化数据或出错修正数据用，这样不用改正式的datax_config配置，影响线上运行。
7，执行datax命令：datax.sh