import numpy as np
import random
import copy
import matplotlib.pyplot as plt

class Problem:
    def __init__(self, K, Pmax, Rmin, H, W, gain_matrix):
        self.K = K                      # số lượng người dùng
        self.Pmax = Pmax                # tổng công suất tối đa
        self.Rmin = Rmin                # tốc độ tối thiểu yêu cầu (bits/s/Hz)
        self.H = H                      # ma trận kênh
        self.W = W                      # ma trận tiền mã hóa ZF
        self.gain_matrix = gain_matrix  # |H^H W|^2

def decode(chromosome):
    return chromosome  # chromosome là vector công suất thực

def get_fitness(chromosome, problem: Problem):
    p = chromosome
    total_power = np.sum(p)

    # Ràng buộc: tổng công suất không được vượt quá Pmax
    if total_power > problem.Pmax:
        return [1e9, 1e9]

    # Tính SINR và rate cho từng user
    sinr = np.zeros(problem.K)
    for k in range(problem.K):
        desired = p[k] * problem.gain_matrix[k, k]
        interference = np.sum(p * problem.gain_matrix[k, :]) - desired
        sinr[k] = desired / (interference + 1.0)

    rates = np.log2(1 + sinr)
    sum_rate = np.sum(rates)
    satisfied = np.sum(rates >= problem.Rmin)

    return [-sum_rate, -satisfied]

class Individual:
    def __init__(self):
        self.chromosome = None
        self.fitness = None

    def gen_indi(self, problem: Problem):
        # Khởi tạo ngẫu nhiên công suất cho từng user, giới hạn trong [0, Pmax/K]
        max_per_user = problem.Pmax / problem.K
        self.chromosome = np.random.uniform(0.0, max_per_user, problem.K)

    def cal_fitness(self, problem):
        self.fitness = get_fitness(self.chromosome, problem)

    def clone(self):
        return copy.deepcopy(self)

    def __lt__(self, other):
        return np.all(self.fitness <= other.fitness) and np.any(self.fitness < other.fitness)

    def __eq__(self, other):
        return np.all(self.chromosome == other.chromosome)

    def __hash__(self):
        return hash(tuple(self.chromosome))

    def __repr__(self):
        return f"chromosome={self.chromosome}, fitness={self.fitness}"

def crossover(parent1, parent2, problem: Problem, eta=2.0):
    off1 = Individual()
    off2 = Individual()
    r = np.random.rand()
    if r <= 0.5:
        beta = (2 * r) ** (1.0 / (eta + 1))
    else:
        beta = (1.0 / (2 * (1 - r))) ** (1.0 / (eta + 1))

    p1 = parent1.chromosome
    p2 = parent2.chromosome
    c1 = 0.5 * ((1 + beta) * p1 + (1 - beta) * p2)
    c2 = 0.5 * ((1 - beta) * p1 + (1 + beta) * p2)

    c1 = np.clip(c1, 0.0, problem.Pmax)
    c2 = np.clip(c2, 0.0, problem.Pmax)

    off1.chromosome = c1
    off2.chromosome = c2
    return off1.clone(), off2.clone()

def mutation(indi, problem: Problem, eta=20.0):
    chr = indi.chromosome.copy()
    for i in range(chr.size):
        mu = np.random.rand()
        if mu <= 0.5:
            delta = (2 * mu) ** (1.0 / (1 + eta)) - 1
            chr[i] = chr[i] + delta * chr[i]
        else:
            delta = 1 - (2 - 2 * mu) ** (1.0 / (1 + eta))
            chr[i] = chr[i] + delta * (problem.Pmax - chr[i])

    chr = np.clip(chr, 0.0, problem.Pmax)
    indi.chromosome = chr
    return indi.clone()

class Population:
    def __init__(self, pop_size, problem: Problem):
        self.pop_size = pop_size
        self.list_indi = []
        self.problem = problem

    def gen_pop(self):
        for _ in range(self.pop_size):
            indi = Individual()
            indi.gen_indi(self.problem)
            indi.cal_fitness(self.problem)
            self.list_indi.append(indi)

def selection(list_indi, k=4):
    tour1 = random.sample(list_indi, k)
    tour2 = random.sample(list_indi, k)
    x = min(tour1)
    y = min(tour2)
    return x.clone(), y.clone()

def fast_nondominated_sort(pop: list):
    n = len(pop)
    pn = np.zeros(n, dtype=int)      # domination count
    pS = [[] for _ in range(n)]      # list of dominated indices

    for i, p in enumerate(pop):
        for j, q in enumerate(pop):
            if i == j:
                continue
            if p < q:                # p dominates q
                pn[j] += 1
                pS[i].append(j)

    
    fronts = [[i for i in range(n) if pn[i] == 0]]
    while True:
        next_front = []
        for i in fronts[-1]:
            for j in pS[i]:
                pn[j] -= 1
                if pn[j] == 0:
                    next_front.append(j)
        if not next_front:
            break
        fronts.append(next_front)

    return [[pop[idx] for idx in front] for front in fronts]

def assign_crowding_distance(pop: list):
    if len(pop) < 3:
        return pop
    I = np.zeros(len(pop))
    num_obj = len(pop[0].fitness)

    for m in range(num_obj):
        # Sắp xếp theo mục tiêu thứ m
        indices = np.argsort([ind.fitness[m] for ind in pop])
        # Gán khoảng cách vô cùng cho hai biên
        I[indices[0]] = I[indices[-1]] = 1e9
        f_min = pop[indices[0]].fitness[m]
        f_max = pop[indices[-1]].fitness[m]
        if f_max - f_min < 1e-9:
            continue
        for i in range(1, len(pop) - 1):
            I[indices[i]] += (pop[indices[i+1]].fitness[m] - pop[indices[i-1]].fitness[m]) / (f_max - f_min)

    # Sắp xếp giảm dần theo crowding distance
    sorted_idx = np.argsort(I)[::-1]
    return [pop[i] for i in sorted_idx]

def survival_selection(pop_list, pop_size):
    fronts = fast_nondominated_sort(pop_list)
    next_gen = []
    for front in fronts:
        front = assign_crowding_distance(front)
        for indi in front:
            next_gen.append(indi)
            pop_size -= 1
            if pop_size == 0:
                return next_gen
    if pop_size != 0:
        print("Warning: Không đủ cá thể để lấp đầy quần thể mới")
    return next_gen

def NSGAII(problem, pop_size, max_gen, p_c, p_m):
    # Khởi tạo quần thể ban đầu
    pop = Population(pop_size, problem)
    pop.gen_pop()

    for gen in range(max_gen):
        # Tạo thế hệ con
        nextPop = []
        while len(nextPop) < pop_size:
            p1, p2 = selection(pop.list_indi)
            c1, c2 = Individual(), Individual()
            if np.random.rand() <= p_c:
                c1, c2 = crossover(p1, p2, problem)
                if np.random.rand() <= p_m:
                    c1 = mutation(c1, problem)
                if np.random.rand() <= p_m:
                    c2 = mutation(c2, problem)
                c1.cal_fitness(problem)
                c2.cal_fitness(problem)
                nextPop.extend([c1, c2])
            else:
                c1 = p1.clone()
                c2 = p2.clone()
                if np.random.rand() <= p_m:
                    c1 = mutation(c1, problem)
                if np.random.rand() <= p_m:
                    c2 = mutation(c2, problem)
                c1.cal_fitness(problem)
                c2.cal_fitness(problem)
                nextPop.extend([c1, c2])

        combined = pop.list_indi + nextPop
        pop.list_indi = survival_selection(combined, pop_size)

    # Lấy Pareto front cuối cùng
    fronts = fast_nondominated_sort(pop.list_indi)
    pareto_front = fronts[0]  # chỉ lấy front tốt nhất
    return pareto_front

# ================= CÀI ĐẶT BÀI TOÁN SATELLITE =================
if __name__ == "__main__":
    # Tham số hệ thống
    K = 7
    PdB = 14.9202
    Pmax = (10 ** (PdB / 10)) * K   # tổng công suất tối đa (W)
    Rmin = 1.0                      # tốc độ tối thiểu (bits/s/Hz) – có thể thay đổi

    # Tạo kênh Rayleigh và nhiễu
    k_B = 1.3806503e-23
    T = 50
    Tref = 290
    NF = 10 ** (2.278 / 10)
    B = 500e6 * 0.9 / 1.05
    sigma2 = k_B * ((NF - 1) * Tref + T) * B

    H = np.random.randn(K, K) + 1j * np.random.randn(K, K)
    H = H / np.sqrt(sigma2)
    sigma2 = 1   # chuẩn hóa

    # Zero‑forcing precoding
    W = H @ np.linalg.inv(H.conj().T @ H)
    for i in range(K):
        W[:, i] /= np.linalg.norm(W[:, i])

    gain_matrix = np.abs(H.conj().T @ W) ** 2

    # Khởi tạo bài toán
    problem = Problem(K, Pmax, Rmin, H, W, gain_matrix)

    # Tham số NSGA-II
    pop_size = 100
    max_gen = 100
    Pc = 0.8
    Pm = 0.2

    # Chạy giải thuật
    pareto_front = NSGAII(problem, pop_size, max_gen, Pc, Pm)

    # Hiển thị kết quả
    print("Pareto Front (tối thiểu hóa):")
    for ind in pareto_front:
        print(f"  Fitness = {ind.fitness}  ->  SumRate = {-ind.fitness[0]:.2f}, Satisfied = {-ind.fitness[1]}")

    # Vẽ biểu đồ
    all_pop = Population(pop_size, problem)
    all_pop.gen_pop()
    # Tính fitness cho tất cả (chỉ để vẽ, không ảnh hưởng)
    for ind in all_pop.list_indi:
        ind.cal_fitness(problem)

    all_x = [-ind.fitness[0] for ind in all_pop.list_indi]
    all_y = [-ind.fitness[1] for ind in all_pop.list_indi]
    pareto_x = [-ind.fitness[0] for ind in pareto_front]
    pareto_y = [-ind.fitness[1] for ind in pareto_front]

    plt.figure(figsize=(8, 6))
    plt.scatter(all_x, all_y, alpha=0.5, label="Quần thể")
    plt.scatter(pareto_x, pareto_y, s=80, edgecolors='black', color='red', label="Pareto Front")
    plt.xlabel("Tổng tốc độ (bits/s/Hz)")
    plt.ylabel("Số người dùng thỏa mãn")
    plt.title("Pareto Front - NSGA-II cho bài toán vệ tinh")
    plt.legend()
    plt.grid(True)
    plt.show()