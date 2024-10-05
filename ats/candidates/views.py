from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Candidate
from .serializers import CandidateSerializer
from django.db.models import Q, Case, When, IntegerField

class CandidateListCreateAPIView(APIView):
    """
    Handles creating a candidate and listing all candidates.
    """
    def get(self, request, *args, **kwargs):
        candidates = Candidate.objects.all()
        serializer = CandidateSerializer(candidates, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = CandidateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CandidateRetrieveUpdateDestroyAPIView(APIView):
    """
    Handles retrieving, updating, and deleting a candidate.
    """
    def get(self, request, pk, *args, **kwargs):
        candidate = get_object_or_404(Candidate, pk=pk)
        serializer = CandidateSerializer(candidate)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        candidate = get_object_or_404(Candidate, pk=pk)
        serializer = CandidateSerializer(candidate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        candidate = get_object_or_404(Candidate, pk=pk)
        candidate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CandidateSearchAPIView(APIView):

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        query_words = query.split()
        print(query,query_words)
        if not query_words:
            return Response([])  

    
        conditions = Q(name__icontains=query_words[0])
        score_annotation = Case(
            When(name__icontains=query_words[0], then=1),
            output_field=IntegerField()
        )

        for word in query_words[1:]:
            conditions |= Q(name__icontains=word)
            score_annotation += Case(
                When(name__icontains=word, then=1),
                output_field=IntegerField()
            )

        
        candidates = Candidate.objects.filter(conditions).annotate(
            relevancy=score_annotation
        ).order_by('-relevancy')

        serializer = CandidateSerializer(candidates, many=True)

 
        return Response(serializer.data)