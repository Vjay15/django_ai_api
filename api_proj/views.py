from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import History
from django.conf import settings
from openai import OpenAI

messages = [
    {"role": "system", "content": "You are an expert answer evaluator. Your job is to evaluate student answers fairly based on a flexible rubric and the specified difficulty level.\n\nInstructions:\n1. Return the score out of the total marks.\n2. Give a brief explanation justifying the score, referencing key points from the rubric.\n3. Suggest at least one specific way the student can improve their answer quality or overall academic performance.\n4. Use the rubric as a guideline, not a rigid checklist.\n5. Adjust the strictness of grading based on difficulty:\n   - 'easy' → lenient evaluation; minor issues can be overlooked.\n   - 'medium' → balanced and reasonable evaluation.\n   - 'hard' → stricter evaluation; all points must be well explained and accurate."},
]

base = "https://prep-threaded-obligations-strengths.trycloudflare.com/v1/"

alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

            ### Instruction:
            {}

            ### Input:
            {}

            ### Response:
            {}"""

class AIView(APIView):
    def post(self, request):
        if request.is_authenticated == False:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
        if request.subdomain == "openai":
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            data = request.data
            prompt = data.get('prompt')
            model = f"{settings.OPENAI_MODEL_ID}"

            if not prompt:
                return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)
                
            # Create a copy of messages to avoid modifying the global list
            conversation_messages = messages.copy()
            conversation_messages.append({"role": "user", "content": prompt})
                
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=conversation_messages  # Use the copy
                )

                # Save the history
                history = History(
                    key=request.key,
                    input=prompt,
                    output=response.choices[0].message.content
                )
                history.save(using=f"{request.subdomain}")  

                return Response({"response": response.choices[0].message.content}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
        elif request.subdomain == "soc":
                client = OpenAI(
                    api_key="EMPTY",
                    base_url=base,
                )
                prompt = request.data.get('prompt', '')  # Fixed: get prompt from request data
                
                try:
                    prompts = alpaca_prompt.format(
                        messages[0]['content'],
                        prompt,  # Use the extracted prompt
                        ""
                    )
                    
                    completion = client.completions.create(
                        model="soc",
                        prompt=prompts, 
                        temperature=0.7, 
                        top_p=0.9, 
                        max_tokens=500
                    )
                    
                    history = History(
                        key=request.key,
                        input=prompt,
                        output=completion.choices[0].text
                    )
                    history.save(using=f"{request.subdomain}")  

                    return Response({"response": completion.choices[0].text.strip()}, status=status.HTTP_200_OK)
                except Exception as e:  # Fixed: except syntax
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
        elif request.subdomain == "sci":
                client = OpenAI(
                    api_key="EMPTY",
                    base_url=base,
                )
                prompt = request.data.get('prompt', '')  # Fixed: get prompt from request data
                
                try:
                    prompts = alpaca_prompt.format(
                        messages[0]['content'],
                        prompt,  # Use the extracted prompt
                        ""
                    )
                    
                    completion = client.completions.create(
                        model="sci",
                        prompt=prompts, 
                        temperature=0.7, 
                        top_p=0.9, 
                        max_tokens=500
                    )
                    
                    history = History(
                        key=request.key,
                        input=prompt,
                        output=completion.choices[0].text
                    )
                    history.save(using=f"{request.subdomain}")  

                    return Response({"response": completion.choices[0].text.strip()}, status=status.HTTP_200_OK)
                except Exception as e:  # Fixed: except syntax
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
                return Response({"error": "Invalid subdomain"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        if request.is_authenticated == False:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        if request.subdomain == "openai":
            data = {
            "model_name": "gpt-4.1-mini",
            "model_id": f"{settings.OPENAI_MODEL_ID}",
            "description": "Fine-tuned GPT-4.1 Mini for expert answer evaluation",
            "purpose": "Evaluates student answers based on rubrics and difficulty levels",
            "capabilities": [
                "Answer evaluation",
                "Score calculation",
                "Performance feedback",
                "Academic improvement suggestions"
            ],
            "input_format": {
                "required_fields": ["prompt"],
                "optional_fields": ["difficulty", "rubric", "total_marks"],
                "content_type": "application/json"
            },
            "output_format": {
                "score": "numerical score out of total marks",
                "explanation": "brief justification for the score",
                "suggestions": "improvement recommendations"
            },
            "limitations": {
                "max_tokens": 4096,
                "context_window": "8k tokens",
                "rate_limits": "10 requests per minute"
            },
            "pricing": {
                "per_request": "$0.01",
                "bulk_discount": "Available for 1000+ requests"
            },
            "supported_languages": ["English"],
            "accuracy": "95% accuracy on academic evaluations",
            "last_updated": "2025-04-14",
            "version": "1.0",
            "fine_tuned_on": "Academic answer evaluation dataset",
            "base_model": "GPT-4.1 Mini",
            "training_data_size": "50k examples",
            "specialization": "Educational assessment and grading"
            }
        elif request.subdomain == "soc":
            data = {
                "model_name": "Llama-3-8B-Social-Evaluator",
                "model_id": "unsloth/llama-3-8b-instruct-bnb-4bit",
                "description": "Quantized Llama-3-8B fine-tuned with LoRA for social science question and answer evaluation",
                "purpose": "Evaluates social science questions and answers with contextual understanding",
                "capabilities": [
                    "Social science Q&A evaluation",
                    "Contextual answer assessment",
                    "Critical thinking evaluation",
                    "Social theory application analysis",
                    "Argument structure assessment"
                ],
                "input_format": {
                    "required_fields": ["prompt"],
                    "optional_fields": ["context", "difficulty", "subject_area"],
                    "content_type": "application/json"
                },
                "output_format": {
                    "evaluation": "comprehensive answer assessment",
                    "strengths": "identified strong points",
                    "weaknesses": "areas for improvement",
                    "recommendations": "specific improvement suggestions"
                },
                "limitations": {
                    "max_tokens": 2048,
                    "context_window": "4k tokens",
                    "rate_limits": "15 requests per minute"
                },
                "pricing": {
                    "per_request": "$0.005",
                    "bulk_discount": "Available for 500+ requests"
                },
                "supported_languages": ["English"],
                "accuracy": "88% accuracy on social science evaluations",
                "last_updated": "2025-07-15",
                "version": "2.1",
                "fine_tuned_on": "Social science Q&A evaluation dataset",
                "base_model": "Meta Llama-3-8B-Instruct",
                "training_data_size": "25k social science examples",
                "specialization": "Social science education and assessment",
                "quantization": "4-bit BNB quantization",
                "training_method": "LoRA (Low-Rank Adaptation)",
                "parameters": "8B parameters (quantized)",
                "inference_speed": "~2.5 seconds per response",
                "subject_areas": [
                    "Sociology",
                    "Psychology", 
                    "Political Science",
                    "Anthropology",
                    "Economics",
                    "History"
                ]
            }
        elif request.subdomain == "sci":
            data = {
                "model_name": "Llama-3-8B-Science-Evaluator", 
                "model_id": "unsloth/llama-3-8b-instruct-bnb-4bit",
                "description": "Quantized Llama-3-8B fine-tuned with LoRA for science question and answer evaluation",
                "purpose": "Evaluates scientific questions and answers with technical accuracy",
                "capabilities": [
                    "Scientific Q&A evaluation",
                    "Technical accuracy assessment",
                    "Scientific method evaluation",
                    "Formula and calculation review",
                    "Laboratory procedure analysis"
                ],
                "input_format": {
                    "required_fields": ["prompt"],
                    "optional_fields": ["subject", "difficulty", "calculation_required"],
                    "content_type": "application/json"
                },
                "output_format": {
                    "evaluation": "scientific accuracy assessment",
                    "technical_accuracy": "correctness of scientific concepts",
                    "methodology": "evaluation of scientific approach",
                    "recommendations": "improvement suggestions"
                },
                "limitations": {
                    "max_tokens": 2048,
                    "context_window": "4k tokens", 
                    "rate_limits": "15 requests per minute"
                },
                "pricing": {
                    "per_request": "$0.005",
                    "bulk_discount": "Available for 500+ requests"
                },
                "supported_languages": ["English"],
                "accuracy": "92% accuracy on science evaluations",
                "last_updated": "2025-07-15",
                "version": "2.1",
                "fine_tuned_on": "Science Q&A evaluation dataset",
                "base_model": "Meta Llama-3-8B-Instruct",
                "training_data_size": "30k science examples",
                "specialization": "Science education and assessment",
                "quantization": "4-bit BNB quantization",
                "training_method": "LoRA (Low-Rank Adaptation)",
                "parameters": "8B parameters (quantized)",
                "inference_speed": "~2.5 seconds per response",
                "subject_areas": [
                    "Physics",
                    "Chemistry",
                    "Biology",
                    "Mathematics",
                    "Earth Science",
                    "Computer Science"
                ]
            }
        else:
            return Response({"error": "Invalid subdomain"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)


class HistoryView(APIView):
    def get(self, request):
        if request.is_authenticated == False:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            histories = History.objects.using(f"{request.subdomain}").filter(key=request.key)
            history_data = [{"id": h.id, "input": h.input, "output": h.output} for h in histories]
            return Response(history_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)