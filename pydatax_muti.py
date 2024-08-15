# coding:utf-8
import psycopg2
import os
import re
import datetime
import cx_Oracle

def dxconn():

    conn = psycopg2.connect(dbname='datax', user='datax_rw', password='123', host='192.168.0.1', port=9000)
    conn.set_client_encoding('utf-8')
    return conn


def ora_conn():
    conn = cx_Oracle.connect(user="ora_ro", password="123", dsn="192.168.11.17:1521/hr")
    return conn

def oldora_conn():
    conn = cx_Oracle.connect(user="ora_ro", password="123", dsn="10.0.1.1:1521/ht")
    return conn


def get_dataxlog(tab_name,dt):
    today = datetime.date.today().strftime("%Y-%m-%d")  # 今天
    sql = "select count(*) from datax_log where dt='"+dt+"' and table_name='"+tab_name+"'  "
    cn = dxconn()
    cursor = cn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    for i in results:
      if int(i[0])>0:
       return True
    return False


## 执行上次出错的datax
def get_error_datax():
    conn = dxconn()
    cur = conn.cursor()
    sql = "select  src_table_name,des_table_name,split_pk_field,relation,dcondition,src_table_column," \
          " des_table_column,id,etl_type from datax_config where status=0 and server_type=0 and type=1" \
          " and id in (select datax_id from datax_log where is_finished=0) order by ordernum desc"
    cur.execute(sql)
    datas = cur.fetchall()
    title = ('src_table_name', 'des_table_name', 'split_pk_field', 'relation', 'dcondition',
             'src_table_column', 'des_table_column', 'id', 'etl_type')
    data_list = [dict(zip(title, item)) for item in  datas ]
    return data_list

def get_datax_table():
    conn = dxconn()
    cur = conn.cursor()
    sql = "select  a.src_table_name,a.des_table_name,a.split_pk_field,a.relation,a.dcondition,a.src_table_column," \
          "a.des_table_column,a.id,a.etl_type,a.etl_column,b.df_json,b.di_json from datax_config a left join datax_json b" \
          " on a.json_id=b.id where a.status=0 and a.server_type=0 and a.type=1" \
          " order by a.ordernum asc"
    cur.execute(sql)
    datas = cur.fetchall()
    title = ('src_table_name', 'des_table_name', 'split_pk_field', 'relation', 'dcondition',
             'src_table_column', 'des_table_column', 'id', 'etl_type', 'etl_column','df_json','di_json')
    data_list = [dict(zip(title, item)) for item in datas]
    return data_list

## 记录行的出错信息
def process_row_error(dataxid,table_name,msg):
    conn = dxconn()
    cur = conn.cursor()
    error_num = re.findall("脏数据条数检查不通过，限制是\[0\]条，但实际上捕获了\[(\d*)\]条", msg)  # 抽取的行部分报错
    error_num = error_num[0].strip("") if error_num else 0
    total_num = re.findall("Total([\s\d]*)records", msg)
    total_num = total_num[0].strip("") if total_num else 0

    ssql = "insert into datax_row_error(datax_id,table_name,error_num,total_num, msg) " \
           " values ('{0}','{1}','{2}','{3}','{4}')".format(str(dataxid), table_name,
            str(error_num),str(total_num),str(msg).replace('\'','').replace(chr(0),'{异常字符占位替换}'))
    cur.execute(ssql)
    conn.commit()

## datax的etl执行报错
def process_etl_error(dataxid,table_name,msg):
    conn = dxconn()
    cur = conn.cursor()
    ssql = "insert into datax_etl_error(datax_id,table_name, msg) " \
           " values ('{0}','{1}','{2}')".format(str(dataxid), table_name, str(msg).replace('\'','').replace(chr(0),''))
    print("666")
    cur.execute(ssql)
    conn.commit()

## 记录ETL成功等
def process_etl(table_name):
    conn = dxconn()
    cur = conn.cursor()
    dt = datetime.date.today().strftime("%Y-%m-%d")  # 今天
    sql = "update datax_config set etl_num=etl_num+1,last_etl_date='" + str(dt) + "' " \
          " where src_table_name='" + str(table_name) + "'   "
    cur.execute(sql)
    conn.commit()

## 记录成功日志，返回的行数和速度等
def process_succss(dataxid,table_name,datax_msg,last_error_id):
    conn = dxconn()
    cur = conn.cursor()
    dt = datetime.date.today().strftime("%Y-%m-%d")  # 今天
    result=datax_msg
    starttime = re.findall("任务启动时刻\s*:\s*(.*)", result)   # 任务启动时刻
    endtime = re.findall("任务结束时刻\s*:\s*(.*)", result)     # 任务结束时刻
    zjhs = re.findall("任务总计耗时\s*:\s*([\d.]*)", result)    #任务总计耗时
    xrsd = re.findall("记录写入速度\s*:\s*([\d.]*)", result)    #记录写入速度
    dczs = re.findall("读出记录总数\s*:\s*(.*)", result)        #读出记录总数
    net = re.findall("任务平均流量\s*:\s*(.*)", result)         #任务平均流量
    dcsb = re.findall("读写失败总数\s*:\s*(.*)", result)        #读写失败总数
    kssj = re.findall("任务启动时刻\s*:\s*(.*)", result)        #任务启动时刻
    zjsj = re.findall("任务结束时刻\s*:\s*(.*)", result)        #任务结束时刻

    starttime = starttime[0].strip() if starttime else '2003-10-24 17:10:11'
    endtime = endtime[0].strip() if endtime else '2003-10-24 17:10:11'
    zjhs = zjhs[0].strip() if zjhs else 0
    xrsd = xrsd[0].strip() if xrsd else 0
    dcsb = dcsb[0].strip() if dcsb else 0
    dczs = dczs[0].strip() if dczs else 0
    net = net[0].strip() if net else 0
    kssj = kssj[0].strip() if kssj else 0
    zjsj = zjsj[0].strip() if zjsj else 0
    sql = "update datax_log set starttime='" + str(starttime) + "',endtime='" + str(endtime) + "'," \
          "is_finished=1,time_num='" + str(zjhs) + "',speed_num='" + str(xrsd) + "'," \
          "read_num='" + str(dczs) + "',net_num='" + str(net) + "',error_num='" + str(dcsb) + "' "
    if int(last_error_id)>0: # 更新出错log行的数据和截止日期
      sql=sql+" ,etl_endtime='"+str(getYesterday(0))+"' where  id='" + str(last_error_id)+ "' "
    else:  # 否则更新当天的日志
      sql = sql + " where  table_name='" + str(table_name) + "' and dt='" + dt + "' "
    cur.execute(sql)
    conn.commit()

# 和当前日期的间隔天数，计算得到日期
def getYesterday(num):
    today=datetime.date.today()
    oneday=datetime.timedelta(days=num)
    yesterday=today-oneday
    return yesterday

# datax执行抽取每个表
def etl_table(row):
    src_table_name=row.get("src_table_name")
    des_table_name=row.get("des_table_name")
    split_pk_field=row.get("split_pk_field")
    relation=row.get("relation")
    dcondition=row.get("dcondition")
    src_table_columns=row.get("src_table_column")
    des_table_columns=row.get("des_table_column")
    dataxid=row.get("id")
    etl_type = row.get("etl_type")
    etl_column= row.get("etl_column")
    df_json=row.get("df_json")   # etl抽取全量模板
    di_json=row.get("di_json")  # etl抽取增量模板

    etl_mode=df_json  # etl抽取模板，默认0为全量
    etl_beginday=1 # etl 开始日期于当前日期的间隔天数，默认前1天
    etl_endday=0 # etl 结束日期于当前日期的间隔天数，默认当天

    log_row=get_error_log(src_table_name) # 判断是否有上次执行错误的etl
    last_error_id=0  # 上次执行异常的log表的id
    if log_row:
        last_error_id=log_row[0].get("id")
        etl_beginday=log_row[0].get("begin_day") # 如果有的话，从上次出错开始日期到现在开始抽取

    if int(etl_type)>=1 and int(etl_type)<=2:    #1,2为增量 ,同时增量字段不为空
      etl_mode=di_json
      # dcondition=etl_column+'>=to_date($%'+etl_begintime.strftime("%Y-%m-%d") +'#%%,$%YYYY-MM-DD$%%) and  '+ \
      #            etl_column+'<to_date($%'+etl_endtime.strftime("%Y-%m-%d")+'#%%,$%YYYY-MM-DD$%%) '
      # dcondition = dcondition.replace('$', ''''\\''''').replace('#', '\\''').replace('%', '\'')
    
    if int(etl_type)==3:    #0为全量,3为按条件全量
      etl_mode=df_json
      dcondition=str(etl_column)

    if int(etl_type)==1 and len(str(etl_column).strip())>0: # 1为按天增量 ,配置有增量字段
      dcondition=str(etl_column)+'>=TRUNC(sysdate-'+str(etl_beginday)+') and '+ \
                 str(etl_column)+'<TRUNC(sysdate-'+str(etl_endday)+')'

    if int(etl_type)==2 and len(str(etl_column).strip())>0: # 2为特殊增量 ,配置有增量字段
      dcondition=str(etl_column)
    
   # if str(src_table_name)=='yw_kck':
   #   etl_mode=df_json  # yw_kck:etl抽取模板为全量
   # if str(src_table_name)=='gl_custom':
   #   etl_mode=df_json  # gl_custom抽取模板为全量
   # if str(src_table_name)=='gl_super':
   #   etl_mode=df_json  # gl_super:etl抽取模板为全量


    print(src_table_name)
    dt=datetime.date.today().strftime("%Y-%m-%d")
    conn = dxconn()
    cur = conn.cursor()
    # 其他8家分公司库
    src_table_columns_fz=get_org_src_columns(src_table_columns,"FZ",src_table_name)
    src_table_columns_jcg=get_org_src_columns(src_table_columns,"JCG",src_table_name)
    src_table_columns_ks=get_org_src_columns(src_table_columns,"KS",src_table_name)
    src_table_columns_qzdf=get_org_src_columns(src_table_columns,"QZDF",src_table_name)
    src_table_columns_sdsht=get_org_src_columns(src_table_columns,"SDSHT",src_table_name)
    src_table_columns_wfjx=get_org_src_columns(src_table_columns,"WFJX",src_table_name)
    src_table_columns_wst=get_org_src_columns(src_table_columns,"WST",src_table_name)
    src_table_columns_std=get_org_src_columns(src_table_columns,"STD",src_table_name)
    src_table_columns_wflsy=get_org_src_columns(src_table_columns,"WFLSY",src_table_name)
    src_table_columns_ky=get_org_src_columns(src_table_columns,"KY",src_table_name)
    src_table_columns_wfjy=get_org_src_columns(src_table_columns,"WFJY",src_table_name)

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
           " -Dsrc_table_columns_ky='" + src_table_columns_ky + "' " \
           " -Dsrc_table_columns_wflsy='" + src_table_columns_wflsy + "' " \
           " -Dsrc_table_columns_wfjy='" + src_table_columns_wfjy + "' " \
           " -Ddes_table_columns='"+des_table_columns+"' \" "
    #print(str1)

    ## 写入datax执行日志，当天没有执行或者没有错误日志
    if get_dataxlog(src_table_name,dt)==False and int(last_error_id)==0:
     ssql="insert into datax_log(table_name, datax_id, is_finished,dt,etl_begintime,etl_endtime) " \
        " values ('{0}','{1}','{2}','{3}','{4}','{5}')".format(src_table_name, str(dataxid),0,
          dt,str(getYesterday(etl_beginday)),str(getYesterday(etl_endday)))
     #print(ssql)
     cur.execute(ssql)
     conn.commit()

    result=''
    try:
     result = os.popen(str1).read()
    except Exception as e:
     print(e)
    # 处理执行结果（成功，异常，日志）
   # print(result)
    process_log(dataxid, src_table_name, result,last_error_id)


# 获取分公司库该表的字段，如对比宏仁堂库表字段的缺失，使用null as 字段替换，如果多余则废弃，
# 字段对比以宏仁堂库为标准
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
    conn = oldora_conn()
    cur = conn.cursor()
    cols=""
    sql="select WM_CONCAT(COLUMN_NAME) cols from (SELECT  COLUMN_NAME FROM  all_tab_columns WHERE OWNER=upper('"+org_name+"') " \
        "and  table_name =upper('"+tab_name+"') order by COLUMN_ID asc) t ";
    cur.execute(sql)
    datas = cur.fetchall()
    for row in datas:
      cols= str(row[0])
    return cols;

## 执行上次出错的datax
def get_error_log(table_name):
    conn = dxconn()
    cur = conn.cursor()
    sql = " select id,etl_begintime,etl_endtime, (etl_begintime::date-CURRENT_DATE) begin_day, " \
          " (etl_endtime::date-CURRENT_DATE) end_day from datax_log where " \
          " is_finished=0 and table_name='" + str(table_name) + "' order by id desc limit 1"
    cur.execute(sql)
    datas = cur.fetchall()
    title = ('id', 'etl_begintime', 'etl_endtime', 'begin_day', 'end_day')
    data_list = [dict(zip(title, item)) for item in  datas ]
    return data_list

# 处理执行信息
def process_log(dataxid, src_table_name, result,last_error_id):
    is_succss = re.findall("该任务最可能的错误原因是", result)  # 是否etl执行出错
    error_num = re.findall("脏数据条数检查不通过，限制是\[0\]条，但实际上捕获了\[(\d*)\]条", result)  # 抽取的行部分报错
    error_num = error_num[0].strip("") if error_num else 0
    if len(is_succss) == 0 and int(error_num) == 0:  ## 执行成功(没有错误和错误的行数）
        process_succss(dataxid, src_table_name, result,last_error_id)
        process_etl(src_table_name)
    elif len(is_succss) > 0 and int(error_num) > 0:  ## 执行报错的行
        process_row_error(dataxid, src_table_name, result)
    elif len(is_succss) > 0 and int(error_num) == 0:  ## etl执行报错
        process_etl_error(dataxid, src_table_name, result)
    print("******")


def main():
   data_list=get_datax_table()
   for row in data_list: # 遍历datax要抽取的表
    try:
      etl_table(row)
    except ValueError:
        print("error")

if __name__ == "__main__":
    main();