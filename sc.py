import asyncio
from student_schedule_manager import ClassScheduleManager,SubmissionManager

# 基本スケジュールの設定
basic_schedule_classM = {
    "Basic": {
        "Monday": ["基礎数学1", "情報2", "物理1", "補講"],
        "Tuesday": ["日本史", "保健-体育", "英語1A", "国語1"],
        "Wednesday": ["基礎数学2", "工学基礎", "特活", "ALH"],
        "Thursday": ["化学1", "機械製図1", "英語1B", "基礎数学1"],
        "Friday": ["生物", "物理1", "機械実習", "機械実習"]
    }
}
# 使用例
async def main():
    schedule_manager = ClassScheduleManager()
    submission_manager = SubmissionManager()
    # クラスごとに基本スケジュールをセットアップ
    await schedule_manager.add_class_schedule("M", basic_schedule_classM)
    # # 指定した日付のスケジュールを編集
    target_date = "2023-12-22"
    edited_schedule_for_target_date = ["基礎数学1", "情報2", "物理1", "物理1"]
    await schedule_manager.edit_class_schedule("M", target_date, edited_schedule_for_target_date)
    await submission_manager.add_submission("1M", "2023-12-13", ["プレゼンテーション","課題x100"])
    upcoming_submissions = await submission_manager.get_upcoming_submissions("1M")
    print("提出物:")
    for deadline, assignments in upcoming_submissions.items():
        remaining_days = await submission_manager.count_remaining_days(deadline)
        print(f"{deadline}: {assignments} (Remaining Days: {remaining_days})")
    # 特定のクラス・日にちのスケジュールを表示
    result = await schedule_manager.view_class_schedule("M", "2023-12-11")
    result2 = await schedule_manager.view_class_schedule("M", "2023-12-22")
    print(result)
    print(result2)

if __name__ == "__main__":
    asyncio.run(main())


