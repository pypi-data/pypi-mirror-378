"""
وحدة العمليات الحسابية الأساسية
تحتوي على وظائف الجمع والطرح والضرب والقسمة
"""


def add(a, b):
    """
    جمع رقمين
    
    Args:
        a (float): الرقم الأول
        b (float): الرقم الثاني
    
    Returns:
        float: ناتج الجمع
    """
    return a + b


def subtract(a, b):
    """
    طرح رقمين
    
    Args:
        a (float): الرقم الأول (المطروح منه)
        b (float): الرقم الثاني (المطروح)
    
    Returns:
        float: ناتج الطرح
    """
    return a - b


def multiply(a, b):
    """
    ضرب رقمين
    
    Args:
        a (float): الرقم الأول
        b (float): الرقم الثاني
    
    Returns:
        float: ناتج الضرب
    """
    return a * b


def divide(a, b):
    """
    قسمة رقمين
    
    Args:
        a (float): الرقم الأول (المقسوم)
        b (float): الرقم الثاني (المقسوم عليه)
    
    Returns:
        float: ناتج القسمة
    
    Raises:
        ValueError: إذا كان المقسوم عليه يساوي صفر
    """
    if b == 0:
        raise ValueError("لا يمكن القسمة على صفر!")
    return a / b
