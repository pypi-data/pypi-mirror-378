from itertools import product
from typing import Sequence, Callable, Literal
import warnings
import traceback
import time
from byzh.core.Bwriter import B_Writer
class B_GridFunc():
    def __init__(
            self,
            mode:Literal["product", "zip"] = "product",
            run_verbose=False,
            log_path=None,
            **kwargs: Sequence
    ):
        '''
        :param mode: "product": 所有情况, "zip": 对应情况
        :param kwargs: 值需要被[]包裹
        '''
        self.mode = mode
        self.run_verbose = run_verbose
        self.log_path = log_path
        self.writer = B_Writer(self.log_path) if self.log_path else None
        self.keys = []

        for key, value in kwargs.items():
            setattr(self, key+"_list", value)
            self.keys.append(key)

        self.values_lst = self._get_values_lst()

    def _get_values_lst(self):
        temp = [getattr(self, key + "_list") for key in self.keys]
        if self.mode == "product":
            return list(product(*temp))
        elif self.mode == "zip":
            # 检查是否个数相同
            if len(set(map(len, temp))) != 1:
                warnings.warn("zip模式下, 如果各部分的len不一样, 则超出部分不参与遍历")
            return list(zip(*temp))
        else:
            raise ValueError("Invalid mode")

    def _set_values(self, index):
        for key, value in zip(self.keys, self.values_lst[index]):
            setattr(self, key, value)

    def _get_exact_name(self, value):
        if isinstance(value, Callable):
            return value.__name__
        else:
            return str(value)

    def run(self, func: Callable, *args, **kwargs):
        '''
        运行函数
        :param func:
        :param args:
        :param kwargs:
        :return:
        '''

        total = len(self.values_lst)
        for i in range(total):
            # 设置元素
            self._set_values(i)
            # 运行函数
            flag = "完成"
            try:
                func(*args, **kwargs)
            except Exception as e:
                flag = f"失败: {e}"
                traceback.print_exc()
            # 记录
            if self.run_verbose:
                print(f"[B_GridFunc] 第{i+1}/{total}次迭代{flag}")
                print(f"[B_GridFunc] 其参数为:")
                for key in self.keys:
                    content = self._get_exact_name(getattr(self, key))
                    if len(content) > 50:
                        content = content[:50] + "..."
                    print(f"------------ \t{key}={content}")
            if self.writer:
                self.writer.toFile(f"[B_GridFunc] 第{i + 1}/{total}次迭代{flag}")
                self.writer.toFile(f"[B_GridFunc] 其参数为:")
                for key in self.keys:
                    content = self._get_exact_name(getattr(self, key))
                    self.writer.toFile(f"------------ \t{key}={content}")

    def get_names(self, time_strf="%Y%m%d.%H%M%S", val_name=True) -> str:
        name_lst = []
        # 设置变量名, 函数名
        for key in self.keys:
            content = self._get_exact_name(getattr(self, key))
            name_lst.append(f"{key}_{content}" if val_name else content)
        # 设置时间
        if time_strf:
            name_lst.append(time.strftime(time_strf))

        result = '-'.join(name_lst)
        return result

    def __getattr__(self, item: str):
        # 防止 IDE 报未定义
        if item in self.keys:
            return getattr(self, item)
        raise AttributeError(f"{self.__class__.__name__} 没有属性 {item!r}")

if __name__ == '__main__':
    # 示例 1: product 笛卡尔积模式
    def demo_func1():
        print(f"x={wrapper.x}, y={wrapper.y}, x+y={wrapper.x + wrapper.y}, z={wrapper.z}")
    print("=== product 模式 ===")
    wrapper = B_GridFunc(
        mode="product",
        x=[1, 2, 3],
        y=[10, 20],
        z=[50]
    )
    wrapper.run(demo_func1)

    # 示例 2: zip 模式
    def demo_func2(awa, qwq):
        print(f"x={wrapper.x}, y={wrapper.y}, x+y={wrapper.x + wrapper.y}, awa={awa}, qwq={qwq}")
    print("\n=== zip 模式 ===")
    wrapper = B_GridFunc(
        "zip",
        True,
        x=[1, 2, 3],
        y=[10, 20, 30],
    )
    wrapper.run(demo_func2, "哈哈哈", qwq="呜呜呜")
    print(wrapper.get_names())
