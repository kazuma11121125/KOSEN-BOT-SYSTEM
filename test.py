import calendar
from datetime import datetime

class MonthInfo:
    def __init__(self, year, month):
        self.year = year
        self.month = month

    def get_current_year_and_month(self):
        current_date = datetime.now()
        self.year, self.month = current_date.year, current_date.month

    def get_number_of_weeks(self):
        cal = calendar.monthcalendar(self.year, self.month)
        return len(cal)-1


    def get_week_dates(self, week_number):
        cal = calendar.monthcalendar(self.year, self.month)
        week_dates = []

        for week in cal:
            if week[0] != 0 and week_number == calendar.monthcalendar(self.year, self.month).index(week):
                week_dates.extend(week)
                break

        return [day for day in week_dates if day != 0]

    def display_result(self, week_number, week_dates):
        print(f"現在の年: {self.year}")
        print(f"現在の月: {self.month}")
        print(f"{self.year}年{self.month}月の週数: {self.get_number_of_weeks()}")

        if week_dates:
            print(f"\n{self.year}年{self.month}月の第{week_number}週の日付: {week_dates}")
        else:
            print(f"\n{self.year}年{self.month}月には第{week_number}週が存在しません。")

if __name__ == "__main__":
    info = MonthInfo(0, 0)  # 初期化時にダミーの値を入れておく

    info.get_current_year_and_month()

    week_number = int(input("週を入力してください: "))
    week_dates = info.get_week_dates(week_number)
    formatted_dates = " ".join(f"{day:02}" for day in week_dates)
    info.display_result(week_number, formatted_dates)
