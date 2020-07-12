import random


def get_random_code():
    # 生成验证码的逻辑
    code = "%06d" % random.randint(0, 999999)
    return code


if __name__ == '__main__':
    get_random_code()
