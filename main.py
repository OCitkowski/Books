"""
Тестовий скрипт для роботи з Ollama моделями
Використовується для тестування моделі qwen3.5:9b

Функціонал:
- Генерація тексту за допомогою OllamaLLM
- Вивід результатів у зручному форматі
- Обробка помилок та винятків
- Підтримка налаштувань через змінні оточення
"""

from langchain_ollama import OllamaLLM
import logging
import os

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_llm(model_name="qwen3.5:9b", temperature=0.7):
    """
    Створює екземпляр OllamaLLM
    
    Args:
        model_name (str): Назва моделі Ollama
        temperature (float): Температура генерації (0.0-1.0)
    
    Returns:
        OllamaLLM: Екземпляр моделі
    
    Raises:
        Exception: При помилці створення моделі
    """
    try:
        llm = OllamaLLM(
            model=model_name,
            temperature=temperature
        )
        logger.info(f"Успішно створено LLM з моделлю {model_name}")
        return llm
    except Exception as e:
        logger.error(f"Помилка при створенні LLM: {e}")
        raise

def generate_text(llm, prompt):
    """
    Генерує текст за допомогою LLM
    
    Args:
        llm (OllamaLLM): Екземпляр моделі
        prompt (str): Запит для генерації
    
    Returns:
        str: Результат генерації
    
    Raises:
        Exception: При помилці генерації
    """
    try:
        logger.info(f"Генерація тексту для запиту: {prompt[:50]}.")
        response = llm.invoke(prompt)
        logger.info("Текст успішно згенеровано")
        return response
    except Exception as e:
        logger.error(f"Помилка при генерації тексту: {e}")
        raise

def main():
    """
    Основна функція проекту
    """
    logger.info("Початок тесту Ollama")
    
    try:
        # Отримуємо налаштування з оточення
        model_name = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
        temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
        
        # Створюємо LLM
        llm = create_llm(model_name, temperature)
        
        # Генеруємо текст
        prompt = "Напиши 2 речення в нуар стилі про нічне місто."
        
        print("\n--- Запит ---")
        print(prompt)
        
        print("\n--- Відповідь ---")
        response = generate_text(llm, prompt)
        print(response)
        
        logger.info("Тест успішно завершено")
        
    except Exception as e:
        logger.error(f"Помилка при виконанні: {e}")
        raise

if __name__ == "__main__":
    main()
