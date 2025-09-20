# Simple Calculator - Ramzy اليتيم

مكتبة بايثون بسيطة تحتوي على عمليات جمع، طرح، ضرب، وقسمة.

## طريقة الاستخدام

```python
from my_simple_calculator.calculator import add, subtract, multiply, divide

result_add = add(10, 5)
print(f"الجمع: {result_add}")

result_subtract = subtract(10, 5)
print(f"الطرح: {result_subtract}")

result_multiply = multiply(10, 5)
print(f"الضرب: {result_multiply}")

result_divide = divide(10, 5)
print(f"القسمة: {result_divide}")

try:
    divide(10, 0)
except ValueError as e:
    print(e)
```

## التثبيت

لتثبيت الحزمة، استخدم الأمر التالي:

`pip install simple-calculator-ramzy-elyatim`


