import random
import argparse

def calculate_success_rate_slide(n, s, T):
    success_count = 0
    
    for _ in range(T):
        # 生成1到10000的整数列表
        all_numbers = list(range(1, 10001))
        
        # 随机选择n个整数
        chosen_numbers = random.sample(all_numbers, n)
        
        # 随机选择一个起始位置，确保剩余的长度足够s
        start_position = random.randint(0, 10000 - s)
        
        # 取一段长度为s的连续subset
        subset = set(range(start_position, start_position + s))
        
        # 检查chosen_numbers是否与subset没有交集
        if subset.isdisjoint(chosen_numbers):
            success_count += 1
    
    # 计算成功率
    success_rate = success_count / T * 100
    return success_rate

def calculate_success_rate_random(n, s, T):
    success_count = 0
    
    for _ in range(T):
        # 生成1到10000的整数列表
        all_numbers = list(range(1, 10001))
        
        # 随机选择n个整数
        chosen_numbers = random.sample(all_numbers, n)
        
        # 随机选择s个元素，不保证连续
        subset = set(random.sample(all_numbers, s))
        
        # 检查chosen_numbers是否与subset没有交集
        if subset.isdisjoint(chosen_numbers):
            success_count += 1
    
    # 计算成功率
    success_rate = success_count / T * 100
    return success_rate

if __name__ == "__main__":
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="Calculate the success rate of chosen integers not intersecting a random subset.")
    parser.add_argument('-n', type=int, required=True, help='Number of random integers to choose.')
    parser.add_argument('-s', type=int, required=True, help='Length of the subset.')
    parser.add_argument('-T', type=int, required=True, help='Number of trials.')
    parser.add_argument('--mode', choices=['slide', 'random'], required=True, help='Mode of selecting the subset: slide (continuous) or random (non-continuous).')
    
    args = parser.parse_args()
    
    if args.mode == 'slide':
        # 计算并输出成功率（slide模式）
        success_rate = calculate_success_rate_slide(args.n, args.s, args.T)
    elif args.mode == 'random':
        # 计算并输出成功率（random模式）
        success_rate = calculate_success_rate_random(args.n, args.s, args.T)
    
    print(f"Success rate ({args.mode} mode): {success_rate:.2f}%")
