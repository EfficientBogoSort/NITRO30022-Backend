from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Test
from .serializers import TestSerializer

@api_view(['GET', 'POST'])
def test(request, format=None):

    if request.method == 'GET':
        tests = Test.objects.all()
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

@api_view(['GET', 'PUT', 'DELETE'])
def test_detail(request, id, format=None):
    try:
        test = Test.objects.get(pk=id)
    except Test.DoesNotExist:
        return Response(status=404)
    
    if request.method == 'GET':
        serializer = TestSerializer(test)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TestSerializer(test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        test.delete()
        return Response(status=204)