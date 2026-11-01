# Setup do Ambiente — Flow Voice AI

## Requisitos de Sistema
- Windows 10 ou 11
- Python 3.10 ou superior
- Microfone funcional

## Instalação Passo a Passo

1. Crie e ative um ambiente virtual:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```

3. Configure o arquivo `.env`:
   Copie `.env.example` para `.env` e preencha suas chaves:
   - `GROQ_API_KEY`: Para transcrição ultra rápida com Whisper Large-v3.
   - `GEMINI_API_KEY`: Para refino de contexto de alta inteligência.
