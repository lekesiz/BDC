"""AI utilities using OpenAI API."""

import os
import json
import re
import openai
from flask import current_app
from typing import Dict, List, Optional, Any, Union

# Configure OpenAI
def configure_openai():
    """Configure OpenAI API with credentials."""
    openai.api_key = current_app.config.get('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))
    org = current_app.config.get('OPENAI_ORGANIZATION', os.getenv('OPENAI_ORGANIZATION', ''))
    if org:
        openai.organization = org

def analyze_evaluation_responses(evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze evaluation responses using OpenAI and generate insights.
    
    Args:
        evaluation: Dictionary containing evaluation data including questions and answers
        
    Returns:
        Dictionary with analysis results including strengths, areas_to_improve, and recommendations
    """
    configure_openai()
    
    if not openai.api_key:
        current_app.logger.error("OpenAI API key not configured")
        return {
            "error": "AI integration not configured",
            "strengths": [],
            "areas_to_improve": [],
            "recommendations": []
        }
    
    # Prepare the data for analysis
    questions_and_answers = []
    for question in evaluation.get('questions', []):
        q_text = question.get('text', '')
        a_text = question.get('answer', {}).get('text', 'No answer provided')
        score = question.get('answer', {}).get('score')
        
        if score is not None:
            questions_and_answers.append(f"Question: {q_text}\nAnswer: {a_text}\nScore: {score}")
        else:
            questions_and_answers.append(f"Question: {q_text}\nAnswer: {a_text}")
    
    # Prepare the prompt for analysis
    prompt = f"""
    As an AI assistant, analyze the following evaluation responses and provide insights. 
    Identify strengths, areas for improvement, and recommendations.
    
    Evaluation: {evaluation.get('title', 'Evaluation')}
    
    Responses:
    {questions_and_answers}
    
    Provide the analysis in the following JSON format:
    {{
        "strengths": ["strength 1", "strength 2", ...],
        "areas_to_improve": ["area 1", "area 2", ...],
        "recommendations": ["recommendation 1", "recommendation 2", ...],
        "summary": "A brief summary paragraph of the overall performance."
    }}
    
    Keep the response concise and focused on the most important insights.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use GPT-4 or appropriate model
            messages=[
                {"role": "system", "content": "You are an educational assessment expert analyzing evaluation responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract and parse the JSON response
        response_text = response.choices[0].message['content'].strip()
        
        # Extract JSON from the response if it's wrapped in formatting
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_text
            
        # Remove any non-JSON text
        json_str = re.sub(r'^[^{]*', '', json_str)
        json_str = re.sub(r'[^}]*$', '', json_str)
        
        try:
            analysis = json.loads(json_str)
            
            # Ensure required fields exist
            if not isinstance(analysis.get('strengths'), list):
                analysis['strengths'] = []
            if not isinstance(analysis.get('areas_to_improve'), list):
                analysis['areas_to_improve'] = []
            if not isinstance(analysis.get('recommendations'), list):
                analysis['recommendations'] = []
            if not isinstance(analysis.get('summary'), str):
                analysis['summary'] = "Analysis summary not available."
                
            return analysis
            
        except json.JSONDecodeError:
            current_app.logger.error(f"Failed to parse AI response as JSON: {response_text}")
            return {
                "error": "Failed to parse AI response",
                "strengths": [],
                "areas_to_improve": [],
                "recommendations": [],
                "summary": "Analysis summary not available due to processing error."
            }
            
    except Exception as e:
        current_app.logger.error(f"Error calling OpenAI API: {str(e)}")
        return {
            "error": f"AI analysis failed: {str(e)}",
            "strengths": [],
            "areas_to_improve": [],
            "recommendations": [],
            "summary": "Analysis summary not available due to API error."
        }

def generate_report_content(beneficiary_data: Dict[str, Any], evaluation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate report content with recommendations using OpenAI.
    
    Args:
        beneficiary_data: Dictionary with beneficiary information
        evaluation_data: List of evaluation dictionaries with results
        
    Returns:
        Dictionary with generated report sections
    """
    configure_openai()
    
    if not openai.api_key:
        current_app.logger.error("OpenAI API key not configured")
        return {
            "error": "AI integration not configured",
            "executive_summary": "Not available",
            "strengths": [],
            "areas_for_development": [],
            "recommendations": [],
            "conclusion": "Not available"
        }
    
    # Prepare the data for the report generation
    prompt = f"""
    As an educational expert, generate a comprehensive report for a beneficiary based on their evaluation results.
    
    Beneficiary Information:
    Name: {beneficiary_data.get('first_name', '')} {beneficiary_data.get('last_name', '')}
    Status: {beneficiary_data.get('status', '')}
    
    Evaluation Results:
    {json.dumps(evaluation_data, indent=2)}
    
    Generate a report with the following sections in JSON format:
    {{
        "executive_summary": "A concise summary of the overall performance and key findings",
        "strengths": ["strength 1", "strength 2", ...],
        "areas_for_development": ["area 1", "area 2", ...],
        "recommendations": ["recommendation 1", "recommendation 2", ...],
        "conclusion": "A concluding paragraph with next steps and encouragement"
    }}
    
    Make the report professional, constructive, and actionable.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use GPT-4 or appropriate model
            messages=[
                {"role": "system", "content": "You are an educational assessment expert creating reports."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract and parse the JSON response
        response_text = response.choices[0].message['content'].strip()
        
        # Extract JSON from the response if it's wrapped in formatting
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_text
            
        # Remove any non-JSON text
        json_str = re.sub(r'^[^{]*', '', json_str)
        json_str = re.sub(r'[^}]*$', '', json_str)
        
        try:
            report = json.loads(json_str)
            
            # Ensure required fields exist
            if not isinstance(report.get('executive_summary'), str):
                report['executive_summary'] = "Executive summary not available."
            if not isinstance(report.get('strengths'), list):
                report['strengths'] = []
            if not isinstance(report.get('areas_for_development'), list):
                report['areas_for_development'] = []
            if not isinstance(report.get('recommendations'), list):
                report['recommendations'] = []
            if not isinstance(report.get('conclusion'), str):
                report['conclusion'] = "Conclusion not available."
                
            return report
            
        except json.JSONDecodeError:
            current_app.logger.error(f"Failed to parse AI response as JSON: {response_text}")
            return {
                "error": "Failed to parse AI response",
                "executive_summary": "Not available due to processing error",
                "strengths": [],
                "areas_for_development": [],
                "recommendations": [],
                "conclusion": "Not available due to processing error"
            }
            
    except Exception as e:
        current_app.logger.error(f"Error calling OpenAI API: {str(e)}")
        return {
            "error": f"AI report generation failed: {str(e)}",
            "executive_summary": "Not available due to API error",
            "strengths": [],
            "areas_for_development": [],
            "recommendations": [],
            "conclusion": "Not available due to API error"
        }