# Enhanced Travel Summarization Pipeline with NER and Travel-Specific Features

from transformers import (
    pipeline, T5ForConditionalGeneration, T5Tokenizer,
    BartForConditionalGeneration, BartTokenizer,
    AutoModelForCausalLM, AutoTokenizer,
    AutoTokenizer as NERTokenizer, AutoModelForTokenClassification
)
import textwrap
import warnings
import torch
import math
from evaluate import load
import textstat
import nltk
import json
import re
import spacy
from datetime import datetime, timedelta
from collections import defaultdict

# Suppress warnings
warnings.filterwarnings("ignore")

# Download spacy model if not present
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spacy English model: python -m spacy download en_core_web_sm")
    nlp = None

# Download necessary NLTK data
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading wordnet...")
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading punkt...")
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    print("Downloading omw-1.4...")
    nltk.download('omw-1.4', quiet=True)


class CompleteSummarizationPipeline:
    def __init__(self):
        """Initialize the travel-specific summarization pipeline"""
        print("Initializing Travel Summarization Pipeline...")

        # Initialize main summarization model
        self.model_name = "google/flan-t5-large"
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)

        # Set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Initialize NER model for travel entities
        try:
            self.ner_tokenizer = NERTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
            self.ner_model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
            self.ner_pipeline = pipeline("ner",
                                       model=self.ner_model,
                                       tokenizer=self.ner_tokenizer,
                                       aggregation_strategy="simple")
        except Exception as e:
            print(f"NER model loading failed: {e}")
            self.ner_pipeline = None

        # Initialize perplexity model
        self.ppl_model_name = "gpt2"
        self.ppl_model = AutoModelForCausalLM.from_pretrained(self.ppl_model_name)
        self.ppl_tokenizer = AutoTokenizer.from_pretrained(self.ppl_model_name)

        # Initialize evaluation metrics
        self.rouge = load("rouge")
        self.bleu = load("bleu")
        self.meteor = load("meteor")
        self.bertscore = load("bertscore")

        # Travel-specific patterns
        self.travel_patterns = {
            'price': re.compile(r'[₹$€£¥]\s*[\d,]+(?:\.\d{2})?|\d+\s*(?:rupees?|dollars?|euros?|pounds?)', re.IGNORECASE),
            'time': re.compile(r'\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\s*[AaPp][Mm])?\b'),
            'date': re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b', re.IGNORECASE),
            'duration': re.compile(r'\b\d+\s*(?:days?|nights?|hours?|minutes?|weeks?)\b', re.IGNORECASE),
            'rating': re.compile(r'\b(?:\d+(?:\.\d+)?[/\s]*(?:out\s+of\s+)?[5]|\d+(?:\.\d+)?\s*stars?|\d+(?:\.\d+)?[/★⭐])\b', re.IGNORECASE),
            'distance': re.compile(r'\b\d+(?:\.\d+)?\s*(?:km|miles?|meters?|feet)\b', re.IGNORECASE)
        }

        print("Pipeline initialization complete!")

    def extract_travel_entities(self, text):
        """Extract travel-specific entities using both NER and regex patterns"""
        entities = {
            'locations': [],
            'prices': [],
            'times': [],
            'dates': [],
            'durations': [],
            'ratings': [],
            'distances': [],
            'organizations': [],
            'persons': []
        }

        # Use NER pipeline if available
        if self.ner_pipeline and text: # Add check for empty text
            ner_results = self.ner_pipeline(text)
            for entity in ner_results:
                if entity['entity_group'] == 'LOC':
                    entities['locations'].append(entity['word'])
                elif entity['entity_group'] == 'ORG':
                    entities['organizations'].append(entity['word'])
                elif entity['entity_group'] == 'PER':
                    entities['persons'].append(entity['word'])

        # Use spaCy if available
        if nlp and text: # Add check for empty text
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:
                    entities['locations'].append(ent.text)
                elif ent.label_ == 'ORG':
                    entities['organizations'].append(ent.text)
                elif ent.label_ == 'PERSON':
                    entities['persons'].append(ent.text)

        # Extract using regex patterns
        if text: # Add check for empty text
            for pattern_type, pattern in self.travel_patterns.items():
                matches = pattern.findall(text)
                if pattern_type in entities:
                    entities[pattern_type].extend(matches)

        # Remove duplicates and clean up
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    def create_travel_prompt(self, text, summary_type="travel_comprehensive", entities=None):
        """Create travel-specific prompts that preserve important information"""

        entity_context = ""
        if entities:
            important_info = []
            if entities['prices']:
                important_info.append(f"Prices: {', '.join(entities['prices'][:5])}")
            if entities['locations']:
                important_info.append(f"Key locations: {', '.join(entities['locations'][:10])}")
            if entities['times']:
                important_info.append(f"Times: {', '.join(entities['times'][:5])}")
            if entities['dates']:
                important_info.append(f"Dates: {', '.join(entities['dates'][:5])}")
            if entities['durations']:
                important_info.append(f"Durations: {', '.join(entities['durations'][:3])}")
            if entities['ratings']:
                important_info.append(f"Ratings: {', '.join(entities['ratings'][:3])}")

            if important_info:
                entity_context = f"Key information to preserve: {'; '.join(important_info)}. "

        prompts = {
            "travel_comprehensive": f"{entity_context}Create a comprehensive travel summary including all flights, hotels, itinerary, food recommendations, transportation, budget breakdown, and important details like prices, times, dates, and ratings: {text}",

            "travel_itinerary": f"{entity_context}Summarize this travel itinerary preserving all dates, times, locations, activities, and costs in chronological order: {text}",

            "travel_budget": f"{entity_context}Summarize the travel budget and costs, preserving all price information, accommodation costs, transportation fees, and activity expenses: {text}",

            "travel_accommodation": f"{entity_context}Summarize accommodation options including hotel names, locations, prices, ratings, and amenities: {text}",

            "travel_transportation": f"{entity_context}Summarize transportation options including flights, local transport, times, prices, and booking details: {text}",

            "travel_activities": f"{entity_context}Summarize travel activities and attractions including locations, timings, entry fees, and descriptions: {text}",

            "general": f"{entity_context}Summarize this travel information preserving important details like dates, times, prices, and locations: {text}"
        }

        return prompts.get(summary_type, prompts["travel_comprehensive"])

    def preprocess_travel_text(self, text):
        """Enhanced preprocessing for travel documents"""
        # Remove excessive whitespace while preserving structure
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Keep paragraph breaks
        text = re.sub(r'\s+', ' ', text)  # Normalize spaces

        # Preserve important travel formatting
        text = re.sub(r'(\d+:\d+\s*[AaPp][Mm])', r' \1 ', text)  # Space around times
        text = re.sub(r'([₹$€£¥]\s*[\d,]+)', r' \1 ', text)  # Space around prices
        text = re.sub(r'(\d+(?:\.\d+)?[/★⭐])', r' \1 ', text)  # Space around ratings

        # Ensure proper sentence endings
        if not text.endswith(('.', '!', '?')):
            text += '.'

        return text.strip()

    def generate_travel_summary(self, text, max_length=1024, min_length=400,
                              summary_type="travel_comprehensive", temperature=0.7):
        """Generate travel-specific summary preserving key information"""

        # Preprocess text
        clean_text = self.preprocess_travel_text(text)

        # Extract travel entities
        entities = self.extract_travel_entities(clean_text)

        # Create travel-specific prompt
        prompt = self.create_travel_prompt(clean_text, summary_type, entities)

        # Tokenize with increased max length for travel content
        inputs = self.tokenizer.encode(
            prompt,
            return_tensors="pt",
            max_length=1024,  # Increased for travel content
            truncation=True
        ).to(self.device)

        # Generate with parameters optimized for travel content
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                min_length=min_length,
                num_beams=6,  # Increased for better quality
                do_sample=True,
                temperature=temperature,
                top_p=0.92,  # Slightly increased for variety
                top_k=60,
                repetition_penalty=1.05,
                length_penalty=1.8,  # Encourage longer, detailed summaries
                early_stopping=True,
                no_repeat_ngram_size=4,  # Avoid repeating longer phrases
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode and post-process
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self.postprocess_travel_summary(summary, entities)

    def postprocess_travel_summary(self, summary, entities=None):
        """Enhanced post-processing for travel summaries"""
        # Remove prompt artifacts
        artifacts = [
            "create a comprehensive travel summary including all flights",
            "summarize this travel itinerary preserving all dates",
            "summarize the travel budget and costs",
            "summarize accommodation options including",
            "summarize transportation options including",
            "summarize travel activities and attractions",
            "summarize this travel information preserving",
            "key information to preserve:",
        ]

        summary_lower = summary.lower()
        for artifact in artifacts:
            if artifact in summary_lower:
                idx = summary_lower.find(artifact)
                if idx != -1:
                    # Find the end of the artifact sentence
                    end_idx = summary.find(':', idx)
                    if end_idx == -1:
                        end_idx = summary.find('.', idx)
                    if end_idx != -1:
                        summary = summary[end_idx + 1:].strip()
                    break

        # Capitalize first letter
        if summary:
            summary = summary[0].upper() + summary[1:]

        # Ensure proper ending
        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'

        return summary

    def chunk_travel_text(self, text, chunk_size=600, overlap=100):
        """Travel-aware chunking that preserves sections"""
        words = text.split()

        if len(words) <= chunk_size:
            return [text]

        # Try to identify travel sections
        sections = []
        current_section = []

        travel_headers = [
            'flight', 'hotel', 'accommodation', 'itinerary', 'day',
            'transport', 'food', 'budget', 'cost', 'activity', 'attraction'
        ]

        for word in words:
            current_section.append(word)

            # Check if we hit a section boundary
            if any(header in word.lower() for header in travel_headers) and len(current_section) > 50:
                sections.append(" ".join(current_section))
                current_section = []

        # Add remaining words
        if current_section:
            sections.append(" ".join(current_section))

        # If no clear sections found, use regular chunking
        if len(sections) <= 1:
            sections = []
            start = 0
            while start < len(words):
                end = min(start + chunk_size, len(words))
                chunk = " ".join(words[start:end])
                sections.append(chunk)
                if end >= len(words):
                    break
                start += chunk_size - overlap

        return sections

    def summarize_long_travel_text(self, text, summary_type="travel_comprehensive"):
        """Handle long travel documents with section-aware processing"""
        sections = self.chunk_travel_text(text)

        if len(sections) == 1:
            return self.generate_travel_summary(text, summary_type=summary_type)

        # Summarize each section
        section_summaries = []
        for i, section in enumerate(sections):
            print(f"Processing section {i+1}/{len(sections)}...")
            summary = self.generate_travel_summary(
                section,
                max_length=600,
                min_length=50,
                summary_type=summary_type,
                temperature=0.6
            )
            section_summaries.append(summary)

        # Combine section summaries
        combined = " ".join(section_summaries)

        # Generate final comprehensive summary
        if len(combined.split()) > 400:
            final_summary = self.generate_travel_summary(
                combined,
                max_length=1500,  # Longer for comprehensive travel summaries
                min_length=600,
                summary_type="travel_comprehensive",
                temperature=0.7
            )
        else:
            final_summary = combined

        return final_summary

    def evaluate_travel_summary(self, generated_summary, reference_summary, original_text=None):
        """Enhanced evaluation with travel-specific metrics"""
        results = self.evaluate_summary(generated_summary, reference_summary, original_text)

        # Add travel-specific evaluation
        if original_text:
            original_entities = self.extract_travel_entities(original_text)
            summary_entities = self.extract_travel_entities(generated_summary)

            # Calculate entity preservation scores
            entity_preservation = {}
            for entity_type in original_entities:
                if original_entities[entity_type]:
                    preserved = len([e for e in original_entities[entity_type]
                                   if any(e.lower() in s.lower() for s in summary_entities[entity_type])])
                    total = len(original_entities[entity_type])
                    entity_preservation[f'{entity_type}_preservation'] = preserved / total if total > 0 else 0

            results['travel_specific'] = entity_preservation

            # Calculate information density (important for travel summaries)
            info_density = (len(summary_entities['prices']) +
                          len(summary_entities['locations']) +
                          len(summary_entities['times']) +
                          len(summary_entities['dates'])) / len(generated_summary.split())
            results['information_density'] = info_density

        return results

    # Include all other methods from the original class (calculate_perplexity, evaluate_summary, etc.)
    def calculate_perplexity(self, text):
        """Compute perplexity for a given text"""
        inputs = self.ppl_tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.ppl_model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
        ppl = math.exp(loss.item())
        return ppl

    def evaluate_summary(self, generated_summary, reference_summary, original_text=None):
        """Evaluate summary quality using multiple metrics"""
        results = {}

        # ROUGE
        rouge_result = self.rouge.compute(
            predictions=[generated_summary],
            references=[reference_summary]
        )
        results['rouge'] = rouge_result

        # BLEU
        bleu_result = self.bleu.compute(
            predictions=[generated_summary],
            references=[[reference_summary]]
        )
        results['bleu'] = bleu_result

        # METEOR
        meteor_result = self.meteor.compute(
            predictions=[generated_summary],
            references=[reference_summary]
        )
        results['meteor'] = meteor_result

        # BERTScore
        bertscore_result = self.bertscore.compute(
            predictions=[generated_summary],
            references=[reference_summary],
            lang="en"
        )
        results['bertscore'] = bertscore_result

        # Perplexity
        ppl = self.calculate_perplexity(generated_summary)
        results['perplexity'] = ppl

        # Flesch Reading Ease
        results['flesch_reading_ease'] = textstat.flesch_reading_ease(generated_summary)

        # Compression Ratio
        if original_text and isinstance(original_text, str):
            results['compression_ratio'] = len(generated_summary.split()) / len(original_text.split())
        else:
            if isinstance(reference_summary, str):
                results['compression_ratio'] = len(generated_summary.split()) / len(reference_summary.split())
            else:
                results['compression_ratio'] = None

        # Coverage
        if isinstance(reference_summary, str) and isinstance(generated_summary, str):
            ref_words = set(reference_summary.lower().split())
            gen_words = set(generated_summary.lower().split())
            coverage = len(ref_words & gen_words) / len(ref_words) * 100 if ref_words else 0
            results['coverage'] = coverage
        else:
            results['coverage'] = None

        return results

    def format_summary(self, summary, width=80):
        """Format summary for better readability"""
        return "\n".join(textwrap.wrap(summary, width=width))

    def travel_summarize_and_evaluate(self, text, reference_summary=None,
                                    summary_type="travel_comprehensive", length="large"):
        """Complete travel summarization pipeline"""

        length_configs = {
            "short": {"max_length": 150, "min_length": 50},
            "medium": {"max_length": 300, "min_length": 100},
            "long": {"max_length": 500, "min_length": 150},
            "large": {"max_length": 800, "min_length": 200},
            "comprehensive": {"max_length": 1200, "min_length": 300}
        }

        config = length_configs.get(length, length_configs["large"])

        print(f"\n{'='*70}")
        print(f"PROCESSING TRAVEL DOCUMENT ({summary_type.upper()}, {length.upper()})")
        print(f"{'='*70}")

        # Extract entities first
        entities = self.extract_travel_entities(text)

        print(f"\nEXTRACTED TRAVEL ENTITIES:")
        for entity_type, entity_list in entities.items():
            if entity_list:
                print(f"  {entity_type.title()}: {', '.join(entity_list[:5])}")

        print(f"\n{'-'*50}")
        print(f"ORIGINAL TEXT LENGTH: {len(text.split())} words")
        print(f"{'-'*50}\n")

        # Generate travel summary
        if len(text.split()) > 800:
            summary = self.summarize_long_travel_text(text, summary_type)
        else:
            summary = self.generate_travel_summary(
                text,
                summary_type=summary_type,
                **config
            )

        print(f"{summary_type.upper().replace('_', ' ')} SUMMARY:")
        print(self.format_summary(summary))

        # Calculate perplexity
        ppl = self.calculate_perplexity(summary)
        print(f"\nFluency Score (Perplexity): {ppl:.2f} (lower is better)")
        print(f"Summary Length: {len(summary.split())} words")

        # Evaluate if reference provided
        evaluation = None
        if reference_summary:
            print(f"\n{'-'*40}")
            print("EVALUATION METRICS")
            print(f"{'-'*40}")

            evaluation = self.evaluate_travel_summary(summary, reference_summary, text)

            print(f"\nROUGE Scores:")
            for key, value in evaluation['rouge'].items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")

            print(f"\nBLEU Score: {evaluation['bleu']['bleu']:.4f}")
            print(f"METEOR Score: {evaluation['meteor']['meteor']:.4f}")

            print(f"\nBERTScore:")
            print(f"  Precision: {evaluation['bertscore']['precision'][0]:.4f}")
            print(f"  Recall:    {evaluation['bertscore']['recall'][0]:.4f}")
            print(f"  F1:        {evaluation['bertscore']['f1'][0]:.4f}")

            if 'travel_specific' in evaluation:
                print(f"\nTravel Entity Preservation:")
                for metric, score in evaluation['travel_specific'].items():
                    print(f"  {metric}: {score:.2%}")

            if 'information_density' in evaluation:
                print(f"Information Density: {evaluation['information_density']:.4f}")

        return {
            'original_text': text,
            'summary': summary,
            'entities': entities,
            'perplexity': ppl,
            'evaluation': evaluation
        }

    def compare_travel_summaries(self, summaries_dict, metrics_list=None, output_json="travel_summaries.json"):
        """Compare travel summaries with enhanced scoring"""
        print(f"\n{'='*50}")
        print("TRAVEL SUMMARY COMPARISON")
        print(f"{'='*50}")

        results = []
        for idx, (name, summary) in enumerate(summaries_dict.items()):
            ppl = self.calculate_perplexity(summary)
            entities = self.extract_travel_entities(summary)

            # Count preserved travel information
            travel_info_score = (len(entities['prices']) * 0.3 +
                               len(entities['locations']) * 0.2 +
                               len(entities['times']) * 0.2 +
                               len(entities['dates']) * 0.15 +
                               len(entities['ratings']) * 0.1 +
                               len(entities['durations']) * 0.05)

            evaluation = {}
            if metrics_list and idx < len(metrics_list) and metrics_list[idx] is not None:
                evaluation = metrics_list[idx]
                bert_f1 = evaluation.get('bertscore', {}).get('f1', [0])[0]
                meteor = evaluation.get('meteor', {}).get('meteor', 0)
                coverage = evaluation.get('coverage', 0) / 100

                # Enhanced scoring for travel content
                final_score = (
                    0.4 * bert_f1 +           # Semantic similarity
                    0.15 * meteor +           # Lexical overlap
                    0.15 * coverage +         # Information coverage
                    0.2 * travel_info_score + # Travel-specific information
                    0.1 * (100 - min(ppl, 100)) / 100  # Fluency (normalized)
                )
            else:
                final_score = travel_info_score / max(ppl/10, 1)  # Simple fallback

            results.append((name, summary, ppl, final_score, evaluation, entities))

            print(f"\n{name}:")
            print(f"Perplexity: {ppl:.2f}")
            print(f"Travel Info Score: {travel_info_score:.2f}")
            print(f"Final Score: {final_score:.4f}")
            print(f"Key Travel Elements: Prices({len(entities['prices'])}), "
                  f"Locations({len(entities['locations'])}), Times({len(entities['times'])})")
            print(f"Summary Preview: {summary[:200]}...")

        # Find best summary
        best = max(results, key=lambda x: x[3])
        print(f"\n🏆 BEST TRAVEL SUMMARY: {best[0]} (Score: {best[3]:.4f})")

        # Save results
        best_summary_data = {
            "name": best[0],
            "summary": best[1],
            "perplexity": best[2],
            "final_score": best[3],
            "metrics": best[4],
            "entities": best[5],
            "timestamp": datetime.now().isoformat()
        }

        try:
            with open(output_json, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        timestamp = datetime.now().isoformat()
        data[timestamp] = best_summary_data

        with open(output_json, "w") as f:
            json.dump(data, f, indent=4)

        return results