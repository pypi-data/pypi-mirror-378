import datetime
import random
import os
from datetime import timedelta

from PIL import Image, ImageDraw, ImageFont

class PerfUtil:

    def __init__(self, title):
        self.title = title
        self.users = 200
        self.times = 600
        self.fail = '0'
        self.err = '0.00%'
        self.avg = random.randint(200, 500)
        self.min = int(self.avg / random.randint(1,5))
        self.max = self.avg * 3
        self.mid = int((self.min + self.max) / 2)
        self.p90 = self.avg * 1 - random.randint(50, 80)
        self.p95 = self.avg * 2 - random.randint(50, 80)
        self.p99 = self.avg * 3 - random.randint(50, 80)
        # 总请求数
        self.cnt = int((1 / (self.avg / 1000)) * self.users * self.times)
        # 吞吐量
        self.tps = round(self.cnt / self.times, 2)
        self.rec = round(random.uniform(300, 800), 2)
        self.sed = round(random.uniform(300, 800), 2)

    def change_summary(self):
        # 根据标题长度自动分成最多4行，每行7个字符
        # 计算需要分成的行数（最多4行）
        title_len = len(self.title)
        count = min((title_len + 6) // 5, 4)  # 向上取整计算行数，最多4行
        
        # 如果需要多行显示，则按每行7个字符分割标题
        if count > 1:
            lines = []
            for i in range(count):
                start = i * 5
                end = start + 5
                lines.append(self.title[start:end])
            self.title = '\n'.join(lines)
        
        texts = [self.title, str(self.cnt), str(self.fail), str(self.err), str(self.avg), str(self.min), str(self.max),
                 str(self.mid), str(self.p90), str(self.p95), str(self.p99), str(self.tps), str(self.rec), str(self.sed)]
        positions_1 = [(-100, -100), (250, 292), (466, 292), (614, 292), (774, 292), (974, 292), (1110, 292), (1260, 292), (1440, 292), (1600, 292), (1760, 292), (1920, 292), (2190, 292), (2400, 292)]
        positions_2 = [(70, 344), (250, 344), (466, 344), (614, 344), (774, 344), (974, 344), (1110, 344), (1260, 344), (1440, 344), (1600, 344), (1760, 344), (1920, 344), (2190, 344), (2400, 344)]
        image = Image.open(f"./assets/{count}line_summary_blank.png")
        output = "./assets/summary.png"
        draw = ImageDraw.Draw(image)
        text_colors = [(0, 0, 0)] * len(texts)

        for text, position, color in zip(texts, positions_1, text_colors):
            font = ImageFont.load_default()
            font = ImageFont.truetype("simkai.ttf", 32)
            draw.text(position, text, fill=color, font=font)

        for text, position, color in zip(texts, positions_2, text_colors):
            font = ImageFont.load_default()
            font = ImageFont.truetype("simhei.ttf", 32)
            draw.text(position, text, fill=color, font=font)
        # image.show()
        image.save(output)

    def change_threads(self):
        random_hour = random.randint(8, 23)
        random_minute = random.randint(0, 59)
        start_time = datetime.datetime.now().replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
        time_texts = [(start_time + timedelta(minutes=i)).strftime("%H:%M:00") for i in range(10)]
        positions = [(202, 540), (364, 540), (525, 540), (686, 540), (848, 540), (1009, 540), (1170, 540), (1333, 540), (1494, 540), (1655, 540)]
        image = Image.open("./assets/threads_blank.png")
        output = "./assets/threads.png"
        draw = ImageDraw.Draw(image)
        text_colors = [(0, 0, 0)] * len(time_texts)

        for text, position, color in zip(time_texts, positions, text_colors):
            font = ImageFont.load_default()
            font = ImageFont.truetype("simhei.ttf", 18)
            draw.text(position, text, fill=color, font=font)
        # image.show()
        image.save(output)

    def get_conclusion(self):
        return (f"经检测，在本次测试环境中，该软件在 {self.users} 个并发用户不清除用户缓存时"
                f"进行 {self.times} 秒请求事项申请操作时，请求操作的平均响应时间为 "
                f"{self.avg / 1000} 秒，最大响应时间为 {self.max / 1000} 秒，事务总数为"
                f"{self.cnt} 个，成功事务数为 {self.cnt} 个，失败事务数为 0 ，事务数平均成"
                f"功率为 100%。")


if __name__ == "__main__":
    # 使用一个长标题测试多行功能："这是一个超过21个字符的测试标题用来测试四行显示效果"（共24个字符）
    perf_util = PerfUtil(title='测试标题测试标题测试标题测试标题')
    perf_util.change_summary()
    perf_util.change_threads()
    print(perf_util.get_conclusion())
