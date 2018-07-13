import os
import psutil


def print_memory_usage():
    process = psutil.Process(os.getpid())
    print("Memory usage: ", process.memory_info().rss >> 20, "MB")
