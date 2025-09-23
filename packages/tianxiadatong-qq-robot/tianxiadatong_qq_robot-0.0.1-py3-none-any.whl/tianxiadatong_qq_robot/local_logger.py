import os
import re

import aiofiles

from tianxiadatong_qq_robot import public


#日志写入本地文件（异步）
#
# 日志文件名从 asset.public指定，当日志行数 至少 > 1000 行，至多 < 2000 行时，会自动写入新日志文件，名称为 {BaseName(asset.public指定) + 1}.{suffix}
# 启动时自动遍历到最新的 Base 文件名 + index
#
class AsyncLogWriter:
    def __init__(self, base_filename, max_lines=1000):
        self.base_filename = base_filename
        self.max_lines = max_lines
        self.log_count = 0
        self.file_index = self._get_start_index()
        self.current_file = self._get_filename()

    #获取最新 index
    def _get_start_index(self):
        base_name, ext = os.path.splitext(self.base_filename)
        pattern = re.compile(rf"{re.escape(base_name)}(?:_(\d+))?{re.escape(ext)}$")
        max_index = -1

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        LOG_DIR = os.path.join(BASE_DIR, 'log')
        os.makedirs(LOG_DIR, exist_ok=True)
        for f in os.listdir(LOG_DIR):
            match = pattern.match(f)
            if match:
                idx = match.group(1)
                idx = int(idx) if idx else 0
                max_index = max(max_index, idx)

        return max_index if max_index >= 0 else 0

    def _get_filename(self):
        base_name, ext = os.path.splitext(self.base_filename)
        if self.file_index == 0:
            return self.base_filename
        else:
            return f"{base_name}_{self.file_index}{ext}"

    #写
    async def write_log(self, text: str):
        try:
            if self.log_count >= self.max_lines:
                self.file_index += 1
                self.current_file = self._get_filename()
                self.log_count = 0

            async with aiofiles.open(self.current_file, mode='a', encoding='utf-8') as f:
                await f.write(text + '\n')

            self.log_count += 1

        except Exception as e:
            print(f"异步写入日志失败：{e}")

# 实例。 在 main 被使用
instance = AsyncLogWriter(public.Log_File_Name)