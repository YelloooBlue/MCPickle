from starlette.responses import PlainTextResponse

def health(request):
    return PlainTextResponse("healthy!")