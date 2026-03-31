# LAB
1. NSGA là gì?
NSGA viết tắt của Non‑dominated Sorting Genetic Algorithm (thuật toán di truyền sắp xếp không trội).
Đây là một thuật toán tiến hóa đa mục tiêu, dùng để tìm tập nghiệm Pareto‑optimal cho bài toán có nhiều mục tiêu cần tối ưu cùng lúc.

2. Ý tưởng chính của NSGA‑II
NSGA‑II là phiên bản cải tiến của NSGA, có thêm kỹ thuật crowding distance để phân bố nghiệm đều trên đường cong Pareto.
Các bước chính:
  Tạo quần thể ban đầu
      Khởi tạo một quần thể cá thể (giải pháp) ngẫu nhiên.
  Sắp xếp các “front” không trội (non‑dominated sorting)
      Phân nhóm các cá thể thành các front (front 1 là các nghiệm không trội, front 2 kém hơn front 1, v.v.).
  Tính crowding distance
      Với mỗi front, tính khoảng cách “mật độ” giữa các cá thể để ưa tiên chọn nghiệm phân bố đều trên mặt Pareto.
  Lai ghép và đột biến
      Dùng các toán tử di truyền (crossover, mutation) để tạo quần thể con mới từ quần thể cha mẹ.
  Kết hợp và chọn lọc
      Kết hợp quần thể cũ và quần thể mới, chọn ra số cá thể tốt nhất để sang thế hệ tiếp theo.
   =>  Quá trình lặp vài trăm–vài nghìn thế hệ cho đến khi hội tụ gần Pareto‑front.

4. Ứng dụng của NSGA‑II
NSGA‑II thường được dùng khi:
Bài toán tối ưu đa mục tiêu phức tạp, không thể giải bằng phương pháp toán học cổ điển.

Ví dụ:
  Tối ưu mạng điện phân phối (giảm tổn thất công suất, tối ưu vị trí đặt tụ bù).
  Tối ưu vận hành hồ chứa nước (cung cấp đủ nước mùa khô, tối thiểu nước thiếu hụt).
  Các bài toán logistics, định vị, điều phối, v.v.
