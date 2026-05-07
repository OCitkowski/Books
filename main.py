from langchain_ollama import OllamaLLM

def main():
    print("=== Тест Ollama ===")

    llm = OllamaLLM(
        model="qwen3.5:9b",
        temperature=0.7
    )

    prompt = "Напиши 2 речення в нуар стилі про нічне місто."

    print("\n--- Запит ---")
    print(prompt)

    print("\n--- Відповідь ---")
    response = llm.invoke(prompt)

    print(response)


if __name__ == "__main__":
    main()
