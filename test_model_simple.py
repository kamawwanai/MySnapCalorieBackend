#!/usr/bin/env python3
"""
Простой тест модели классификации
"""

import os
import sys

def test_model_loading():
    """Тестирует загрузку модели"""
    print(" Тестирование загрузки модели")
    print("=" * 50)
    
    try:
        # Импортируем модуль
        from app.models.classifier import get_classifier
        
        # Получаем классификатор
        classifier = get_classifier()
        print("✅ Классификатор создан")
        
        # Проверяем готовность (это вызовет загрузку модели)
        print(" Проверяю готовность модели...")
        ready = classifier.is_ready()
        print(f"Готовность: {ready}")
        
        if ready:
            print(f"✅ Модель готова! Классов: {len(classifier.classes)}")
            return True
        else:
            print("❌ Модель не готова")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_dummy_image():
    """Тестирует классификацию с тестовым изображением"""
    print("\n Тестирование с тестовым изображением")
    print("=" * 50)
    
    try:
        from app.models.classifier import get_classifier
        from PIL import Image
        import io
        
        # Создаем тестовое изображение
        test_img = Image.new('RGB', (224, 224), color='red')
        img_bytes = io.BytesIO()
        test_img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        print(f"✅ Создано тестовое изображение ({len(img_bytes)} байт)")
        
        # Получаем классификатор
        classifier = get_classifier()
        
        # Тестируем классификацию
        print(" Тестирую классификацию...")
        result = classifier.predict(img_bytes)
        print(f"Результат простой классификации: {result}")
        
        # Тестируем детальную классификацию
        print("🔮 Тестирую детальную классификацию...")
        class_name, confidence = classifier.get_prediction_with_confidence(img_bytes)
        print(f"Результат детальной классификации: {class_name}, уверенность: {confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print(" Простой тест модели классификации")
    print("=" * 60)
    
    # Тестируем загрузку
    loading_ok = test_model_loading()
    
    if loading_ok:
        # Тестируем классификацию
        classification_ok = test_with_dummy_image()
    else:
        classification_ok = False
    
    print("\n" + "=" * 60)
    print(" ИТОГИ:")
    print(f"{'✅' if loading_ok else '❌'} Загрузка модели")
    print(f"{'✅' if classification_ok else '❌'} Классификация")
    
    if loading_ok and classification_ok:
        print("\n Все тесты пройдены!")
    else:
        print("\n⚠️  Есть проблемы. Проверьте логи выше.")

if __name__ == "__main__":
    main() 