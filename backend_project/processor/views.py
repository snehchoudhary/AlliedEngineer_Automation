# from pathlib import Path
# from django.http import FileResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings
# from .pipelines import PROCESSOR_MAP, process_cips_on_psp, process_attenuation_acca

# @csrf_exempt
# def process_file(request, processor_key: str):
#     if request.method != "POST":
#         return JsonResponse({"error": "POST a file to this endpoint"}, status=405)

#     if processor_key not in PROCESSOR_MAP:
#         return JsonResponse({"error": f"Unknown processor '{processor_key}'"}, status=404)

#     if "file" not in request.FILES:
#         return JsonResponse({"error": "Missing file (form key: 'file')"}, status=400)

#     uploaded = request.FILES["file"]
#     uploads_dir = Path(settings.MEDIA_ROOT) / "uploads"
#     uploads_dir.mkdir(parents=True, exist_ok=True)
#     in_path = uploads_dir / uploaded.name

#     with open(in_path, "wb") as f:
#         for chunk in uploaded.chunks():
#             f.write(chunk)

#     threshold = request.POST.get("threshold")
#     try:
#         if processor_key == "cips_on_psp":
#             res = process_cips_on_psp(in_path, float(threshold) if threshold else -1.0)
#         elif processor_key == "attenuation_acca":
#             res = process_attenuation_acca(in_path, float(threshold) if threshold else 2.0)
#         elif processor_key == "ac_psp":
#             from .pipelines import process_ac_psp
#             res = process_ac_psp(in_path, float(threshold) if threshold else 4.0)
#         else:
#             res = PROCESSOR_MAP[processor_key](in_path)

#         return FileResponse(open(res.output_path, "rb"), as_attachment=True, filename=res.output_path.name)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from django.conf import settings
from pathlib import Path
from .pipelines import PROCESSOR_MAP  # sirf yeh import rakho

class ProcessFileAPIView(APIView):
    def post(self, request, processor_key: str):
        if processor_key not in PROCESSOR_MAP:
            return Response({"error": f"Unknown processor '{processor_key}'"}, status=status.HTTP_404_NOT_FOUND)

        if "file" not in request.FILES:
            return Response({"error": "Missing file (form key: 'file')"}, status=status.HTTP_400_BAD_REQUEST)

        uploaded = request.FILES["file"]
        uploads_dir = Path(settings.MEDIA_ROOT) / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        in_path = uploads_dir / uploaded.name

        with open(in_path, "wb") as f:
            for chunk in uploaded.chunks():
                f.write(chunk)

        threshold = request.data.get("threshold")
        try:
            # Processor ke hisaab se threshold pass karna hai
            if processor_key == "cips_on_psp":
                res = PROCESSOR_MAP[processor_key](in_path, float(threshold) if threshold else -1.0)
            elif processor_key == "attenuation_acca":
                res = PROCESSOR_MAP[processor_key](in_path, float(threshold) if threshold else 2.0)
            elif processor_key == "ac_psp":
                res = PROCESSOR_MAP[processor_key](in_path, float(threshold) if threshold else 4.0)
            else:
                res = PROCESSOR_MAP[processor_key](in_path)

            return FileResponse(open(res.output_path, "rb"), as_attachment=True, filename=res.output_path.name)

        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
         import traceback
         print("🔥 ERROR in processor:", traceback.format_exc())  # full traceback terminal me print karega
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
