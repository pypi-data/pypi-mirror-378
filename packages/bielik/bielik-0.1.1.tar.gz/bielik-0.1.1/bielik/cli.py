#!/usr/bin/env python3
"""
bielik CLI - interactive chat shell using Ollama.
Tries REST API first, falls back to `ollama` library if available.
"""

import os
import sys
import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("BIELIK_MODEL", "bielik")
CHAT_ENDPOINT = OLLAMA_HOST.rstrip("/") + "/v1/chat/completions"

# try to import official ollama client
try:
    import ollama
    HAVE_OLLAMA = True
except ImportError:
    HAVE_OLLAMA = False


def send_chat(messages, model=DEFAULT_MODEL):
    """Send chat messages to Ollama via REST API or ollama lib fallback."""
    payload = {"model": model, "messages": messages, "stream": False}

    # try REST first
    try:
        resp = requests.post(CHAT_ENDPOINT, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {}).get("content")
        if msg:
            return msg
    except Exception as e:
        print(f"[REST API failed: {e}]")

    # fallback: official ollama library
    if HAVE_OLLAMA:
        try:
            response = ollama.chat(model=model, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            return f"[OLLAMA LIB ERROR] {e}"

    return "[ERROR] No working Ollama integration (REST and lib failed)."


def show_welcome():
    """Display welcome message and help for beginners."""
    print("🦅 " + "="*50)
    print("   BIELIK - Polski Asystent AI")
    print("   Powered by Ollama + Speakleash")
    print("="*53)
    print()
    print("📋 Dostępne komendy:")
    print("  :help    - pokaż tę pomoc")
    print("  :status  - sprawdź połączenie z Ollama")
    print("  :clear   - wyczyść historię rozmowy")
    print("  :exit    - zakończ sesję")
    print("  Ctrl+C   - szybkie wyjście")
    print()
    print("💡 Wskazówki:")
    print("  • Pisz po polsku - Bielik rozumie język polski!")
    print("  • Zadawaj pytania, proś o pomoc, rozmawiaj naturalnie")
    print("  • Jeśli Ollama nie działa, zobaczysz komunikat o błędzie")
    print()


def check_ollama_status():
    """Check if Ollama is running and accessible."""
    import requests
    try:
        # Quick health check
        resp = requests.get(f"{OLLAMA_HOST.rstrip('/')}/api/tags", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            models = [m['name'] for m in data.get('models', [])]
            if any('bielik' in model.lower() for model in models):
                return "✅ Ollama działa, model Bielik dostępny"
            else:
                return f"⚠️ Ollama działa, ale brak modelu 'bielik'. Dostępne: {', '.join(models[:3])}"
        else:
            return f"❌ Ollama odpowiada, ale błąd HTTP {resp.status_code}"
    except Exception as e:
        return f"❌ Ollama niedostępny: {str(e)}"


def main():
    show_welcome()
    
    # Check Ollama status at startup
    status = check_ollama_status()
    print(f"🔗 Status: {status}")
    print()
    
    if "❌" in status:
        print("🚨 UWAGA: Ollama nie działa poprawnie!")
        print("📖 Jak naprawić:")
        print("  1. Zainstaluj Ollama: https://ollama.com")
        print("  2. Uruchom: ollama serve")
        print("  3. Zainstaluj model: ollama pull bielik")
        print("  4. Sprawdź: ollama list")
        print()
        
        try:
            continue_anyway = input("Czy kontynuować mimo problemów? (t/N): ").lower()
            if continue_anyway not in ['t', 'tak', 'y', 'yes']:
                print("Sesja przerwana. Napraw Ollama i spróbuj ponownie.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nSesja przerwana.")
            return
        print()
    
    print("🚀 Gotowy do rozmowy! Napisz coś...")
    print("─" * 53)
    
    messages = [{"role": "system", "content": "You are Bielik, a helpful Polish AI assistant. Respond in Polish unless asked otherwise."}]
    
    try:
        while True:
            try:
                user = input("\n🧑 Ty: ").strip()
            except EOFError:
                print("\n👋 Do zobaczenia!")
                break
                
            if not user:
                continue
                
            # Handle special commands
            if user.startswith(':'):
                if user in [":exit", ":quit", ":q"]:
                    print("👋 Do zobaczenia!")
                    break
                elif user == ":help":
                    show_welcome()
                    continue
                elif user == ":status":
                    status = check_ollama_status()
                    print(f"🔗 Status: {status}")
                    continue
                elif user == ":clear":
                    messages = [{"role": "system", "content": "You are Bielik, a helpful Polish AI assistant. Respond in Polish unless asked otherwise."}]
                    print("🧹 Historia rozmowy wyczyszczona.")
                    continue
                else:
                    print(f"❓ Nieznana komenda: {user}. Wpisz :help aby zobaczyć dostępne komendy.")
                    continue
            
            messages.append({"role": "user", "content": user})
            print("🦅 Bielik myśli...", end="", flush=True)
            
            resp = send_chat(messages)
            print("\r🦅 Bielik: " + " "*20)  # Clear "thinking" message
            print(f"    {resp}")
            
            # Only add to history if it's a real response, not an error
            if not resp.startswith("[ERROR]") and not resp.startswith("[REST ERROR]") and not resp.startswith("[OLLAMA LIB ERROR]"):
                messages.append({"role": "assistant", "content": resp})
            
    except KeyboardInterrupt:
        print("\n\n👋 Przerwano przez użytkownika. Do zobaczenia!")
        sys.exit(0)


if __name__ == "__main__":
    main()
