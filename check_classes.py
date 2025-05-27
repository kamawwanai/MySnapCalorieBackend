import torch
import os

try:
    classes_path = 'app/models/classes.pth'
    print(f"Проверяю файл: {classes_path}")
    print(f"Файл существует: {os.path.exists(classes_path)}")
    
    if os.path.exists(classes_path):
        classes = torch.load(classes_path, map_location='cpu')
        print(f"Тип данных: {type(classes)}")
        print(f"Количество классов: {len(classes)}")
        print(f"Все классы: {classes}")
        
        # Проверяем, что это список строк
        if isinstance(classes, list) and len(classes) > 0:
            print(f"Тип первого элемента: {type(classes[0])}")
            print("✅ Файл классов выглядит корректно")
        else:
            print("❌ Файл классов имеет неожиданный формат")
    
except Exception as e:
    print(f"❌ Ошибка при загрузке файла классов: {e}") 