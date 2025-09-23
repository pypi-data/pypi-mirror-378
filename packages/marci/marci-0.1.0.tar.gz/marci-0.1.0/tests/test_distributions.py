import numpy as np
from marci import Lognormal


def test_lognormal_generate_shape_and_stats():
	mean = 10.0
	cv = 0.5
	d = Lognormal(mean=mean, cv=cv)
	size = 100_000
	samples = d.generate(size)

	assert samples.shape == (size,)
	assert np.all(samples > 0)

	# Empirical stats should be close to target
	emp_mean = float(np.mean(samples))
	emp_std = float(np.std(samples, ddof=0))
	emp_cv = emp_std / emp_mean

	assert abs(emp_mean - mean) / mean < 0.03  # within 3%
	assert abs(emp_cv - cv) / cv < 0.08        # within 8%


def test_lognormal_invalid_size():
	d = Lognormal(mean=1.0, cv=0.2)
	for bad in [0, -1, 1.5, None]:
		try:
			d.generate(bad)  # type: ignore[arg-type]
			assert False, "Expected ValueError"
		except ValueError:
			pass
