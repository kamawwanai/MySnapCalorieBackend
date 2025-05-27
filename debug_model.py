#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с моделью классификации
"""

import os
import sys

def check_files():
    """Проверяет наличие файлов модели"""
    print("🔍 Диагностика файлов модели")
    print("=" * 50)
    
    # Определяем пути
    models_dir = os.path.join("app", "models")
    model_path = os.path.join(models_dir, "class_model.pth")
    classes_path = os.path.join(models_dir, "classes.pth")
    
    print(f"Папка models: {models_dir}")
    print(f"Путь к модели: {model_path}")
    print(f"Путь к классам: {classes_path}")
    print()
    
    # Проверяем папку
    if os.path.exists(models_dir):
        print(f"Папка {models_dir} существует")
        
        # Показываем содержимое
        print(f"Содержимое папки {models_dir}:")
        try:
            files = os.listdir(models_dir)
            for file in files:
                file_path = os.path.join(models_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"{file} ({size:,} байт)")
                else:
                    print(f"{file}/")
        except Exception as e:
            print(f"Ошибка чтения папки: {e}")
    else:
        print(f"Папка {models_dir} не существует")
        return False
    
    print()
    
    # Проверяем файлы
    model_exists = os.path.exists(model_path)
    classes_exists = os.path.exists(classes_path)
    
    print(f"{'✅' if model_exists else '❌'} class_model.pth: {model_exists}")
    print(f"{'✅' if classes_exists else '❌'} classes.pth: {classes_exists}")
    
    if model_exists:
        size = os.path.getsize(model_path)
        print(f"Размер модели: {size:,} байт ({size/1024/1024:.1f} MB)")
    
    if classes_exists:
        size = os.path.getsize(classes_path)
        print(f"Размер файла классов: {size:,} байт")
    
    return model_exists and classes_exists

def test_import():
    """Тестирует импорт модуля классификации"""
    print("\n Тестирование импорта")
    print("=" * 50)
    
    try:
        from app.models.classifier import MODEL_PATH, CLASSES_PATH, get_classifier
        print("Импорт модуля успешен")
        print(f"MODEL_PATH: {MODEL_PATH}")
        print(f"CLASSES_PATH: {CLASSES_PATH}")
        
        # Проверяем пути из модуля
        model_exists = os.path.exists(MODEL_PATH)
        classes_exists = os.path.exists(CLASSES_PATH)
        
        print(f"{'✅' if model_exists else '❌'} Модель найдена по пути из модуля: {model_exists}")
        print(f"{'✅' if classes_exists else '❌'} Классы найдены по пути из модуля: {classes_exists}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_classifier():
    """Тестирует создание классификатора"""
    print("\n Тестирование классификатора")
    print("=" * 50)
    
    try:
        from app.models.classifier import get_classifier
        
        classifier = get_classifier()
        print(" Классификатор создан")
        
        # Проверяем готовность
        ready = classifier.is_ready()
        print(f"{'✅' if ready else '❌'} Готовность модели: {ready}")
        
        if not ready:
            print("Попытка загрузки модели...")
            try:
                classifier._load_model()
                print("✅ Модель загружена успешно")
                print(f"Количество классов: {len(classifier.classes) if classifier.classes else 0}")
            except Exception as e:
                print(f"❌ Ошибка загрузки: {e}")
        
        return ready
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция"""
    print("Диагностика модели классификации")
    print("=" * 60)
    
    # Проверяем рабочую директорию
    cwd = os.getcwd()
    print(f"Текущая директория: {cwd}")
    
    # Проверяем файлы
    files_ok = check_files()
    
    # Тестируем импорт
    import_ok = test_import()
    
    # Тестируем классификатор
    classifier_ok = test_classifier()
    
    print("\n" + "=" * 60)
    print("📋 ИТОГИ:")
    print(f"{'✅' if files_ok else '❌'} Файлы модели найдены")
    print(f"{'✅' if import_ok else '❌'} Импорт модуля работает")
    print(f"{'✅' if classifier_ok else '❌'} Классификатор готов")
    
    if files_ok and import_ok and classifier_ok:
        print("\n Все проверки пройдены! Модель готова к работе.")
    else:
        print("\n Обнаружены проблемы. Проверьте ошибки выше.")

if __name__ == "__main__":
    main() 