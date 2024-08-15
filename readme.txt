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
 数据抽取平台pydatax实现过程中，有2个关键点：
    1、是否能在python3中调用执行datax任务，自己测试了一下可以，代码如下：
    这个str1就是配置的shell文件     

try:
   result = os.popen(str1).read()
except Exception as e:
  print(e)
　 2、是否能获取datax执行后的信息：用来捕获执行的情况和错误信息

         上面执行后的result就包含了datax的执行信息，对信息进行筛选，就可以获得

   pydatax的表设计 
        在上面的2个关键点解决后，其他问题就比较简单，设计相关的表：

datax_config   datax抽取表的模板配置（源表名，目标表名，模板id，抽取的字段，抽取条件（增量，全量，特殊），抽取时间，执行顺序等）
datax_config_repair   datax的出错修复表，结构和datax_config一样，用于datax出错后，修复数据用
datax_etl_error    datax的etl的报错信息（非异常字符的报错）
datax_json   datax的模板id配置（全量和增量2个模板文件名）
datax_log   datax运行抽取表的执行信息（是否执行完成，抽取行数，速度，读出行数，流量等）
datax_row_error  datax执行中，字段有异常字符的报错信息
　pydatax在项目中使用
       项目1： 直接配置datax的模板json，从oracle 11g抽取到postgresql中，

                     因postgresql中会对"0x"这些异常字符报错,如oracle中字段有这样字段，必须在抽取字段使用：

                    使用 replace(name,chr(0),'\'\'') as name 来代替 以前的字段 name

       项目2： 客户有9个分公司，用的ERP有9套，有9个库，不同版本，抽取的同一个表字段长度有不一样，字段可能有多有少，客户ERP核心分公司ERP几个月后有大版本升级。

                     因项目2中：数据仓库使用的GreePlum，datax的驱动用的是gpdbwriter-v1.0.4-hashdata.jar，该驱动自动删除"0x"非法字符，就不存在该错误

                     不可能写9个抽取json模板，再抽取，只能原有json模板上修改

                     字段长度不同： 取9个库的最大值，作为目标表字段的字段长度

                     字段个数不同:   取其一个核心分公司库表为基础建表，其他8个库表，如果有就保留，没有就字段数据为NULL，每次执行查询取出8个库的字段：                         

复制代码
# 获取分公司库该表的字段，如对比核心库表字段的缺失，使用null as 字段替换，如果多余则废弃，
# 字段对比以核心库为标准
def get_org_src_columns(src_columns,org_name,tab_name):
    src_columns = src_columns
    # 分公司字段
    org_cols = get_org_cols(org_name,tab_name)
    lst = src_columns.split(",")
    cols1 = (org_cols + ',')
    src_columns1 = (src_columns + ',')
    for i in lst:
      str1 =i.strip() + ','  # 去掉空格，对比使用，字段名+',',这样避免有重复前缀的字段名，导致误判
      if (cols1.find(str(','+str1)) == -1):
        src_columns1 = src_columns1.replace(str(','+str1), ',NULL as ' + str1)
    return src_columns1.rstrip(',')

# 获取分公司库的表的字段用','合并成一个字符串
def get_org_cols(org_name,tab_name):
    conn = ora_conn()
    cur = conn.cursor()
    cols=""
    sql="select WM_CONCAT(COLUMN_NAME) cols from (SELECT  COLUMN_NAME FROM  all_tab_columns WHERE " \
        " OWNER=upper('"+org_name+"') and  table_name =upper('"+tab_name+"') order by COLUMN_ID asc) t ";
    cur.execute(sql)
    datas = cur.fetchall()
    for row in datas:
      cols= str(row[0])
    return cols;
复制代码
       修改json模板支持同时抽取9个数据库，修改的9个库同时抽取oracle数据到greeplum全量json模板，见下载文件的：oracle_gp_table_df_job.json：  

复制代码
    src_table_columns=row.get("src_table_column")
    # 其他8家分公司库
    src_table_columns_fz=get_org_src_columns(src_table_columns,"FZ",src_table_name)
    src_table_columns_jcg=get_org_src_columns(src_table_columns,"JCG",src_table_name)
    src_table_columns_ks=get_org_src_columns(src_table_columns,"KS",src_table_name)
    src_table_columns_qzdf=get_org_src_columns(src_table_columns,"QZDF",src_table_name)
    src_table_columns_sdsht=get_org_src_columns(src_table_columns,"SDSHT",src_table_name)
    src_table_columns_wfjx=get_org_src_columns(src_table_columns,"WFJX",src_table_name)
    src_table_columns_wst=get_org_src_columns(src_table_columns,"WST",src_table_name)
    src_table_columns_std=get_org_src_columns(src_table_columns,"STD",src_table_name)


    str1 = "/usr/bin/python /opt/module/datax/bin/datax.py /opt/module/datax/job/json/"+etl_mode+" -p  \" " \
           " -Dsrc_table_name='"+src_table_name+"' " \
           " -Ddes_table_name='"+des_table_name+"' " \
           " -Dsplit_pk_field='"+split_pk_field+"'   " \
           " -Drelation='"+relation+"' " \
           " -Dcondition='"+dcondition+"' " \
           " -Dsrc_table_columns='"+src_table_columns+"' " \
           " -Dsrc_table_columns_fz='" + src_table_columns_fz + "' " \
           " -Dsrc_table_columns_jcg='" + src_table_columns_jcg + "' " \
           " -Dsrc_table_columns_ks='" + src_table_columns_ks + "' " \
           " -Dsrc_table_columns_qzdf='" + src_table_columns_qzdf + "' " \
           " -Dsrc_table_columns_sdsht='" + src_table_columns_sdsht + "' " \
           " -Dsrc_table_columns_wfjx='" + src_table_columns_wfjx + "' " \
           " -Dsrc_table_columns_wst='" + src_table_columns_wst + "' " \
           " -Dsrc_table_columns_std='" + src_table_columns_std + "' " \
           " -Ddes_table_columns='"+des_table_columns+"' \" "
复制代码
      这样修改后，就可以同时抽取9个库的数据，同时配置时，只需要配置核心库的相关字段等数据即可！  

 
