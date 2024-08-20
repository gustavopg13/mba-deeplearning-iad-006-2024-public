from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
from typing import List
import base64
import io
from PIL import Image

# Inicialize o FastAPI
app = FastAPI()

# Carregue o modelo globalmente
model = joblib.load('model.joblib')

# Definição da classe para a requisição
class ImageRequest(BaseModel):
    image: str  # Imagem codificada em base64

# Definição da classe para a resposta
class PredictionResponse(BaseModel):
    prediction: int

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: ImageRequest):
    try:
        # Decodifica a imagem base64
        img_bytes = base64.b64decode(request.image)
        img = Image.open(io.BytesIO(img_bytes))
        
        # Redimensiona a imagem para 8x8 pixels
        img = img.resize((8, 8))

        # Converte a imagem para escala de cinza
        img = img.convert('L')
        img_array = np.array(img)

        # Achata a matriz para um vetor de características
        img_array = img_array.reshape(1, -1)

        # Realiza a previsão
        prediction = model.predict(img_array)

        return PredictionResponse(prediction=int(prediction[0]))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao realizar a previsão: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)