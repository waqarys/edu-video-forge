# Quadratic Formula

## Scene: chalkboard
**Narration:** The quadratic formula solves any equation of the form a x squared plus b x plus c equals zero.
**Content:**
The quadratic formula:

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

## Scene: code
**Narration:** Here is a clean Python implementation that returns both roots.
**Content:**
```python
import cmath

def quadratic(a, b, c):
    disc = b**2 - 4*a*c
    root1 = (-b + cmath.sqrt(disc)) / (2*a)
    root2 = (-b - cmath.sqrt(disc)) / (2*a)
    return root1, root2
```

## Scene: chalkboard
**Narration:** Always check the discriminant to know how many real solutions you have.
**Content:**
Discriminant d = b² - 4ac

- d > 0 : two real roots
- d = 0 : one real root
- d < 0 : two complex roots
