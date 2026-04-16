#!/bin/bash

# 定義絕對路徑
PYTHON_BIN="/home/jimub/repos/ctdb/.venv/bin/python"
MANAGE_PY="/home/jimub/repos/ctdb/manage.py"

# 取得當前時間並印出
echo "========================================="
echo "排程執行時間: $(date +'%Y%m%d%H%M%S')"

echo "start send_diary_user_email.."
$PYTHON_BIN $MANAGE_PY senddiaryuseremail

echo "start send_reminder_email.."
$PYTHON_BIN $MANAGE_PY sendreminderemail

echo "start check_news_signatures.."
$PYTHON_BIN $MANAGE_PY check_news_signatures

echo "排程執行結束。"