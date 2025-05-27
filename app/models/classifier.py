import io
import os
from typing import Tuple, Optional

# Отложенные импорты для избежания проблем при запуске
torch = None
timm = None
transforms = None
Image = None

# Жёстко на CPU
DEVICE = None

# Пути к файлам модели
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'class_model.pth')
CLASSES_PATH = os.path.join(os.path.dirname(__file__), 'classes.pth')

def _lazy_import():
    """Отложенный импорт зависимостей"""
    global torch, timm, transforms, Image, DEVICE
    
    if torch is None:
        try:
            import torch as _torch
            import timm as _timm
            from torchvision import transforms as _transforms
            from PIL import Image as _Image
            
            torch = _torch
            timm = _timm
            transforms = _transforms
            Image = _Image
            DEVICE = torch.device('cpu')
            
        except ImportError as e:
            raise ImportError(f"Не удалось импортировать зависимости: {e}")

# Вызываем импорт сразу при загрузке модуля
try:
    _lazy_import()
except ImportError:
    # Если зависимости не установлены, оставляем None
    pass

class FineTunedViT(torch.nn.Module):
    """Архитектура модели Vision Transformer для классификации"""
    def __init__(self, num_classes, model_name='vit_base_patch16_224', freeze_backbone=False):
        # Убеждаемся, что torch импортирован
        if torch is None:
            _lazy_import()
        
        super().__init__()
        
        # Загружаем предобученную ViT (точно как при обучении)
        self.backbone = timm.create_model(model_name, pretrained=False)  # pretrained=False при загрузке
        in_feat = self.backbone.head.in_features
        
        # Убираем штатный head (точно как при обучении)
        self.backbone.head = torch.nn.Identity()
        
        # Заморозка бэкбона (если нужно)
        if freeze_backbone:
            for p in self.backbone.parameters():
                p.requires_grad = False
        
        # Своя голова (точно как при обучении)
        self.classifier = torch.nn.Sequential(
            torch.nn.Dropout(0.2),
            torch.nn.Linear(in_feat, num_classes)
        )
    
    def forward(self, x):
        feat = self.backbone(x)
        return self.classifier(feat)

class ImageClassifier:
    """Класс для классификации изображений"""
    
    def __init__(self):
        self.model: Optional[FineTunedViT] = None
        self.classes: Optional[list] = None
        self.transform = None
        self.confidence_threshold = 0.9  # 90% порог уверенности
        self._is_loaded = False
    
    def _load_model(self):
        """Загружает модель и классы"""
        if self._is_loaded:
            return
            
        try:
            _lazy_import()
            
            # Проверяем наличие файлов
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Файл модели не найден: {MODEL_PATH}")
            if not os.path.exists(CLASSES_PATH):
                raise FileNotFoundError(f"Файл классов не найден: {CLASSES_PATH}")
            
            # Загружаем список классов
            self.classes = torch.load(CLASSES_PATH, map_location='cpu')
            
            # Создаем модель
            self.model = FineTunedViT(num_classes=len(self.classes))
            
            # Загружаем веса
            model_state = torch.load(MODEL_PATH, map_location='cpu')
            
            # Загружаем веса в модель
            self.model.load_state_dict(model_state)
            
            # Перемещаем на устройство и переводим в режим оценки
            self.model = self.model.to(DEVICE)
            self.model.eval()
            
            # Настраиваем пре-процессинг
            self.transform = transforms.Compose([
                transforms.Lambda(lambda img: img.convert('RGB')),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])
            
            self._is_loaded = True
            
            # Тестовый прогон для проверки
            test_input = torch.randn(1, 3, 224, 224).to(DEVICE)
            with torch.no_grad():
                test_output = self.model(test_input)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
    
    def predict(self, image_bytes: bytes) -> str:
        """
        Классифицирует изображение
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            str: Название класса или 'unknown' если уверенность < 90%
        """
        try:
            # Загружаем модель при первом обращении
            self._load_model()
            
            # Открываем изображение
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Применяем трансформации
            x = self.transform(img).unsqueeze(0).to(DEVICE)
            
            # Делаем предсказание
            with torch.no_grad():
                logits = self.model(x)
                probs = torch.nn.functional.softmax(logits, dim=1)
                confidence, idx = probs.max(dim=1)
            
            # Проверяем порог уверенности
            if confidence.item() >= self.confidence_threshold:
                predicted_class = self.classes[idx.item()]
                return predicted_class
            else:
                return "unknown"
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return "unknown"
    
    def get_prediction_with_confidence(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Классифицирует изображение и возвращает результат с уверенностью
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            Tuple[str, float]: (класс, уверенность)
        """
        try:
            # Загружаем модель при первом обращении
            self._load_model()
            
            # Открываем изображение
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Применяем трансформации
            x = self.transform(img).unsqueeze(0).to(DEVICE)
            
            # Делаем предсказание
            with torch.no_grad():
                logits = self.model(x)
                probs = torch.nn.functional.softmax(logits, dim=1)
                confidence, idx = probs.max(dim=1)
            
            class_name = self.classes[idx.item()]
            conf_value = confidence.item()
            
            # Проверяем порог уверенности
            if conf_value >= self.confidence_threshold:
                return class_name, conf_value
            else:
                return "unknown", conf_value
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return "unknown", 0.0
    
    def is_ready(self) -> bool:
        """Проверяет, готова ли модель к работе"""
        try:
            # Проверяем наличие файлов
            files_exist = (os.path.exists(MODEL_PATH) and os.path.exists(CLASSES_PATH))
            
            # Если файлы есть, но модель не загружена, пытаемся загрузить
            if files_exist and not self._is_loaded:
                try:
                    self._load_model()
                except Exception as e:
                    return False
            
            return files_exist and self._is_loaded and self.model is not None
        except Exception as e:
            return False

# Создаем глобальный экземпляр классификатора
classifier = None

def get_classifier() -> ImageClassifier:
    """Возвращает экземпляр классификатора (singleton)"""
    global classifier
    if classifier is None:
        classifier = ImageClassifier()
    return classifier 