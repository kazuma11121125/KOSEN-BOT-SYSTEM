import openpyxl

# Excelファイルのパス
excel_file_path = 'your_excel_file.xlsx'

# ワークブックを開く
workbook = openpyxl.load_workbook(excel_file_path)

# アクティブなシートを取得
sheet = workbook.active

# 問題と答えを格納するリスト
data_list = []

# Excelファイルの各行を走査
for row in sheet.iter_rows(min_row=1, values_only=True):
    # 各行のデータを問題と答えのリストに追加
    question = row[0]  # Aラインのデータが問題
    answer = row[1]    # Bラインのデータが答え
    data_list.append([question, answer])

# ワークブックを閉じる
workbook.close()

print(data_list)
