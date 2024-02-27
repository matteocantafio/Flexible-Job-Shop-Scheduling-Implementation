


import docplex
from docplex.mp.model import Model

# Create the model
model = Model(name='flexible_job_shop_scheduling')

# Data for the FJSP instance
n = 2  # Number of jobs
m = 2  # Number of machines
L = 500  # A large number
# Processing times for each operation on each machine for each job
t = {
    (0, 0, 0): 2, (0, 0, 1): 37,
    (0, 1, 0): 32, (0, 1, 1): 24,
    (1, 0, 0): 45, (1, 0, 1): 65,
    (1, 1, 0): 21, (1, 1, 1): 65
}
# Set of machines available for each operation for each job
Mj = {
    (0, 0): {0, 1},
    (0, 1): {0, 1},
    (1, 0): {0, 1},
    (1, 1): {0, 1}
}

# Decision variables
X = {}
S = {}
C = {}
Y = {}
Ci = {}
Cmax = model.continuous_var(name='Cmax')
# Create decision variables
for i in range(n):
    for j in range(2):  # Assuming each job has two operations
        for k in Mj[i, j]:
            X[i, j, k] = model.binary_var(name=f'X_{i}_{j}_{k}')
            S[i, j, k] = model.continuous_var(name=f'S_{i}_{j}_{k}')
            C[i, j, k] = model.continuous_var(name=f'C_{i}_{j}_{k}')
            for i_prime in range(n):
                if i != i_prime:
                    for j_prime in range(2):
                        if k in Mj[i_prime, j_prime]:
                            Y[i, j, i_prime, j_prime, k] = model.binary_var(name=f'Y_{i}_{j}_{i_prime}_{j_prime}_{k}')

    Ci[i] = model.continuous_var(name=f'Ci_{i}')

# Objective function: Minimize makespan
model.minimize(Cmax)

# Constraints
for i in range(n):
    for j in range(1, 2):  # Assuming each job has two operations
        model.add_constraint(sum(S[i, j, k] for k in Mj[i, j]) >= sum(C[i, j-1, k] for k in Mj[i, j]), ctname=f'precedence_{i}_{j}')

for i in range(n):
    model.add_constraint(Ci[i] >= sum(C[i, 1, k] for k in Mj[i, 1]), ctname=f'completion_time_{i}')
    model.add_constraint(Cmax >= Ci[i], ctname=f'makespan_{i}')

    for j in range(2):  # Assuming each job has two operations
        for k in Mj[i, j]:
            model.add_constraint(C[i, j, k] >= 0, ctname=f'completion_time_nonnegative_{i}_{j}_{k}')

for i in range(n):
    for j in range(2):  # Assuming each job has two operations
        model.add_constraint(sum(X[i, j, k] for k in Mj[i, j]) == 1, ctname=f'assignment_{i}_{j}')

        for k in Mj[i, j]:
            model.add_constraint(S[i, j, k] + C[i, j, k] <= X[i, j, k] * L, ctname=f'time_limit_{i}_{j}_{k}')
            model.add_constraint(C[i, j, k] >= S[i, j, k] + t[i, j, k] - (1 - X[i, j, k]) * L, ctname=f'completion_{i}_{j}_{k}')

            for i_prime in range(n):
                if i != i_prime:
                    for j_prime in range(2):
                        if k in Mj[i_prime, j_prime]:
                            model.add_constraint(S[i, j, k] >= C[i_prime, j_prime, k] - Y[i, j, i_prime, j_prime, k] * L, ctname=f'precedence_{i}_{j}_{i_prime}_{j_prime}_{k}')
                            model.add_constraint(S[i_prime, j_prime, k] >= C[i, j, k] - (1 - Y[i, j, i_prime, j_prime, k]) * L, ctname=f'precedence_{i_prime}_{j_prime}_{i}_{j}_{k}')

# Solve the model
solution = model.solve()

# Print results
if solution:
    print("Makespan:", solution.get_value(Cmax))
    for i in range(n):
        for j in range(2):  # Assuming each job has two operations
            for k in Mj[i, j]:
                print(f"X_{i}_{j}_{k}:", solution.get_value(X[i, j, k]))
                print(f"S_{i}_{j}_{k}:", solution.get_value(S[i, j, k]))
                print(f"C_{i}_{j}_{k}:", solution.get_value(C[i, j, k]))
                for i_prime in range(n):
                    if i != i_prime:
                        for j_prime in range(2):
                            if k in Mj[i_prime, j_prime]:
                                print(f"Y_{i}_{j}_{i_prime}_{j_prime}_{k}:", solution.get_value(Y[i, j, i_prime, j_prime, k]))
        print(f"Ci_{i}:", solution.get_value(Ci[i]))
else:
    print("Il problema non ha soluzione.")

