python -m venv myenv

.\myenv\Scripts\Activate.ps1

RUN
uvicorn main:app --reload --port 1000