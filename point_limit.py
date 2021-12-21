def calculate(diameter: int):
	point_limit = 0

	for i in range(1, diameter + 1):
		point_limit += i

	return point_limit * 4
