# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import os

def get_broker_stock_analysis(base_date: str = None, return_days: int = 5):
    """
    从CSV文件读取券商股票分析记录，按日期要求过滤并返回
    
    :param base_date: 基准日期(格式YYYYMMDD)，默认为当前日期
    :param return_days: 返回最后几条数据 (默认为5条)
    :return: 包含分析记录的DataFrame
    """
    # 从环境变量获取CSV文件路径，如果未设置则使用默认路径
    csv_path = os.environ.get('BROKER_STOCK_ANALYSIS_CSV_PATH')
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'broker_stock_analysis.csv')
    
    # 读取CSV文件
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV文件未找到: {csv_path}")
    
    # 确保timestamp列是datetime类型
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 处理base_date参数
    if base_date:
        # 将base_date转换为datetime对象
        base_date_dt = datetime.strptime(base_date, '%Y%m%d')
    else:
        base_date_dt = datetime.now()
    
    # 过滤数据：选择base_date之前的数据，并按日期降序排序
    filtered_df = df[df['timestamp'] <= base_date_dt].sort_values('timestamp', ascending=False)
    
    # 返回指定天数的数据
    result_df = filtered_df.head(return_days)
    
    return result_df

if __name__ == "__main__":
    # 测试代码
    result = get_broker_stock_analysis(base_date="20240910", return_days=3)
    print(result.to_string(index=False))