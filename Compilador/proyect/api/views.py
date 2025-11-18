from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
import json
import logging

# Importamos nuestro metodo
from .utils import run_code

# Configurar logger
logger = logging.getLogger(__name__)

@api_view(['POST'])
def main(request):
    # Log para debugging
    logger.info(f"Request received - Method: {request.method}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Definimos el metodo de la peticion
    if request.method != 'POST':
        return JsonResponse( 
            {'error':'Método no permitido. Use POST.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        # Parseamos el cuerpo de la peticion en un JSON
        body = request.body.decode('utf-8') if request.body else '{}'
        logger.info(f"Raw body: {body[:500]}")  # Log primeros 500 caracteres
        
        data = json.loads(body) if body else {}
        logger.info(f"Parsed data: {data}")
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse(
            {'error':'JSON inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error parsing request: {e}")
        return JsonResponse(
            {'error':'Error procesando la solicitud'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Intentamos obtener el código de diferentes campos posibles
    code = data.get('code', '') or data.get('text', '') or data.get('input', '')
    
    # Validamos que el código no esté vacío
    if not code or not code.strip():
        logger.warning("Empty code received")
        return JsonResponse(
            {'error':'El código no puede estar vacío'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    logger.info(f"Code to execute (first 200 chars): {code[:200]}")

    try:
        # Ejecutamos las instrucciones con el metodo que definimos
        output = run_code(code)
        logger.info(f"Execution successful. Output: {output}")
        
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        return JsonResponse(
            {'error': f'Error ejecutando el código: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Da una respuesta de tipo JSON
    return JsonResponse(
        {
            "success": True,
            "output": output,
            "code_received": code[:100] + "..." if len(code) > 100 else code
        },
        status=status.HTTP_200_OK
    )
