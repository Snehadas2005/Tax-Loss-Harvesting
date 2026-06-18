FROM python:3.11-slim

# Create a non-root user with UID 1000 (Hugging Face default execution user)
RUN useradd -m -u 1000 user

# Set up environment variables for the user path
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements and install dependencies
COPY --chown=user:user ./requirements.txt $HOME/app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r $HOME/app/requirements.txt

# Copy the rest of the backend files and assign ownership to the user
COPY --chown=user:user . $HOME/app

USER user

# Hugging Face Spaces defaults to exposing port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]