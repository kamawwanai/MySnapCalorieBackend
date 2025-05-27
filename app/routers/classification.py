from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import logging
import os

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def _get_classifier_safe():
    """Безопасное получение классификатора с обработкой ошибок"""
    try:
        from app.models.classifier import get_classifier
        return get_classifier()
    except ImportError as e:
        logger.error(f"Ошибка импорта зависимостей: {e}")
        raise HTTPException(
            status_code=500,
            detail="Зависимости для машинного обучения не установлены. Установите: pip install torch torchvision timm pillow"
        )
    except Exception as e:
        logger.error(f"Ошибка при получении классификатора: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка инициализации модели: {str(e)}"
        )

@router.post("/classify")
async def classify_image(file: UploadFile = File(...)):
    """
    Классифицирует загруженное изображение
    
    Args:
        file: Загруженный файл изображения
        
    Returns:
        JSON с результатом классификации
    """
    # Проверяем тип файла
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="Файл должен быть изображением"
        )
    
    try:
        # Читаем содержимое файла
        image_bytes = await file.read()
        
        # Получаем классификатор
        classifier = _get_classifier_safe()
        
        # Классифицируем изображение
        predicted_class = classifier.predict(image_bytes)
        
        logger.info(f"Классификация завершена: {predicted_class}")
        
        return JSONResponse(
            status_code=200,
            content={
                "class": predicted_class,
                "message": "Классификация выполнена успешно"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при классификации: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке изображения: {str(e)}"
        )

@router.post("/classify-detailed")
async def classify_image_detailed(file: UploadFile = File(...)):
    """
    Классифицирует загруженное изображение с подробной информацией
    
    Args:
        file: Загруженный файл изображения
        
    Returns:
        JSON с результатом классификации и уверенностью
    """
    # Проверяем тип файла
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="Файл должен быть изображением"
        )
    
    try:
        # Читаем содержимое файла
        image_bytes = await file.read()
        
        # Получаем классификатор
        classifier = _get_classifier_safe()
        
        # Классифицируем изображение с получением уверенности
        predicted_class, confidence = classifier.get_prediction_with_confidence(image_bytes)
        
        logger.info(f"Классификация завершена: {predicted_class} (уверенность: {confidence:.3f})")
        
        return JSONResponse(
            status_code=200,
            content={
                "class": predicted_class,
                "confidence": round(confidence, 3),
                "confidence_percentage": round(confidence * 100, 1),
                "threshold_met": confidence >= 0.9,
                "message": "Классификация выполнена успешно"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при классификации: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке изображения: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Проверка работоспособности модели классификации"""
    try:
        from app.models.classifier import MODEL_PATH, CLASSES_PATH
        
        # Проверяем наличие файлов напрямую
        model_file_exists = os.path.exists(MODEL_PATH)
        classes_file_exists = os.path.exists(CLASSES_PATH)
        
        classifier = _get_classifier_safe()
        
        # Проверяем готовность модели
        model_ready = classifier.is_ready()
        
        return JSONResponse(
            status_code=200 if model_ready else 503,
            content={
                "status": "healthy" if model_ready else "not_ready",
                "model_loaded": classifier._is_loaded,
                "classes_count": len(classifier.classes) if classifier.classes else 0,
                "files_exist": {
                    "model_file": model_file_exists,
                    "classes_file": classes_file_exists
                },
                "file_paths": {
                    "model_path": MODEL_PATH,
                    "classes_path": CLASSES_PATH
                },
                "message": "Сервис классификации работает" if model_ready else f"Модель не готова. Файлы: model={model_file_exists}, classes={classes_file_exists}"
            }
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": "unhealthy",
                "error": e.detail,
                "message": "Сервис классификации недоступен"
            }
        )
    except Exception as e:
        logger.error(f"Ошибка при проверке здоровья: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "message": "Сервис классификации недоступен"
            }
        ) 