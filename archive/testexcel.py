import pandas as pd
import os
from datetime import datetime, timedelta
import django
import sys

# 設定 Django 環境
# 確保正確的路徑和設定模組
project_root = r'C:\Users\Administrator\repos\chris-ctdb'
sys.path.insert(0, project_root)
os.chdir(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctdb.settings')

try:
    django.setup()
    from django.contrib.auth.models import Group
    from accounts.models import GroupProfile
    django_loaded = True
except Exception as e:
    print(f"Django 載入失敗: {e}")
    print("將使用模擬資料...")
    django_loaded = False

def get_department_members(department_code):
    """根據部門代碼取得參與者清單（使用群組郵件）"""
    if not django_loaded:
        # 模擬資料，當 Django 無法載入時使用
        return [f'{department_code.lower()}@chief.com.tw']
    
    try:
        # 直接使用部門群組郵件，不需要撈取個別成員
        # 因為 mail server 已經設定好群組郵件（如 i04@chief.com.tw）
        group_email = f'{department_code.lower()}@chief.com.tw'
        return [group_email]
        
    except Exception as e:
        print(f"取得參與者時發生錯誤：{str(e)}")
        return [f'{department_code.lower()}@chief.com.tw']

def read_excel_file(file_path):
    """讀取 Excel 檔案並顯示其內容"""
    try:
        # 讀取 Excel 檔案
        df = pd.read_excel(file_path)
        
        # 使用iloc選擇B、C、D欄位，並重新命名
        selected_columns = df.iloc[:, 1:4]
        selected_columns.columns = ['department', 'meeting_time', 'meeting_room']
        
        # 跳過標題列（第一列）
        selected_columns = selected_columns.iloc[1:]
        
        # 轉換會議時間為datetime格式
        selected_columns['meeting_time'] = pd.to_datetime(selected_columns['meeting_time'])
        
        # 新增提醒時間欄位（會議時間前一週）
        selected_columns['reminder_time'] = selected_columns['meeting_time'] - timedelta(days=7)
        
        # 只顯示核心資訊
        print(f"\n=== 會議清單（共{len(selected_columns)}筆） ===")
        
        # 格式化並顯示所有會議資料
        for idx, row in selected_columns.iterrows():
            meeting_date = row['meeting_time'].strftime('%Y-%m-%d %H:%M')
            reminder_date = row['reminder_time'].strftime('%Y-%m-%d')
            
            # 取得參與者清單
            participants = get_department_members(row['department'])
            participants_str = ', '.join(participants) if participants else '無相關成員'
            
            print(f"單位: {row['department']} | 會議時間: {meeting_date} | 地點: {row['meeting_room']} | 提醒日: {reminder_date}")
            print(f"參與者: {participants_str}")
            print("-" * 80)
        
        return selected_columns
        
    except Exception as e:
        print(f"讀取檔案時發生錯誤：{str(e)}")
        return None

if __name__ == "__main__":
    excel_file_path = r"C:\Users\Administrator\repos\chris-ctdb\media\archive\your_excel_file.xlsx"
    
    if os.path.exists(excel_file_path):
        df = read_excel_file(excel_file_path)
    else:
        print(f"找不到檔案：{excel_file_path}")