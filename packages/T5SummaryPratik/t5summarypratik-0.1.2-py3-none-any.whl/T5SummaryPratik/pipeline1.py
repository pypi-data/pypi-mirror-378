# Enhanced Medical Query Summarization Pipeline with NER and Healthcare-Specific Features

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


class MedicalSummarizationPipeline:
    def __init__(self):
        """Initialize the medical-specific summarization pipeline"""
        print("Initializing Medical Summarization Pipeline...")

        # Initialize main summarization model
        self.model_name = "google/flan-t5-large"
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)

        # Set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Initialize NER model for medical entities
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

        # Medical-specific patterns
        self.medical_patterns = {
            'phone': re.compile(r'\b(?:\+91[-\s]?)?[6789]\d{9}\b|\b\d{4,5}[-\s]?\d{5,6}\b'),
            'rating': re.compile(r'\b(?:\d+(?:\.\d+)?[/\s]*(?:out\s+of\s+)?[5]|\d+(?:\.\d+)?\s*stars?|\d+(?:\.\d+)?[/★⭐])\b', re.IGNORECASE),
            'address': re.compile(r'\b(?:sector|road|street|marg|vihar|nagar|colony|park|place|enclave|extension)\b.*?(?:delhi|new delhi|gurgaon|noida|faridabad|mumbai|bangalore|hyderabad|chennai|pune|kolkata)', re.IGNORECASE),
            'appointment_time': re.compile(r'\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\s*[AaPp][Mm])?\b|\b\d{1,2}:\d{2}-\d{1,2}:\d{2}\b'),
            'date': re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b', re.IGNORECASE),
            'experience': re.compile(r'\b\d+\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)\b', re.IGNORECASE),
            'specialties': re.compile(r'\b(?:cardiologist|neurologist|orthopedic|gynecologist|pediatrician|dermatologist|ophthalmologist|psychiatrist|oncologist|urologist|gastroenterologist|endocrinologist|rheumatologist|pulmonologist|nephrologist|surgeon|physician|dentist|radiologist|pathologist|anesthesiologist)\b', re.IGNORECASE),
            'hospital': re.compile(r'\b(?:hospital|clinic|medical center|healthcare|nursing home|dispensary|polyclinic)\b', re.IGNORECASE),
            'booking_status': re.compile(r'\b(?:booked successfully|appointment confirmed|booking completed|scheduled|confirmed)\b', re.IGNORECASE),
            'reviews': re.compile(r'\b\d+\s*(?:reviews?|ratings?)\b', re.IGNORECASE)
        }

        # Medical specialties list for better recognition
        self.medical_specialties = [
            'cardiology', 'neurology', 'orthopedics', 'gynecology', 'pediatrics',
            'dermatology', 'ophthalmology', 'psychiatry', 'oncology', 'urology',
            'gastroenterology', 'endocrinology', 'rheumatology', 'pulmonology',
            'nephrology', 'surgery', 'internal medicine', 'dentistry', 'radiology',
            'pathology', 'anesthesiology', 'emergency medicine', 'family medicine'
        ]

        print("Pipeline initialization complete!")

    def extract_medical_entities(self, text):
        """Extract medical-specific entities using both NER and regex patterns"""
        entities = {
            'doctors': [],
            'hospitals': [],
            'specialties': [],
            'phones': [],
            'ratings': [],
            'addresses': [],
            'appointment_times': [],
            'dates': [],
            'experience': [],
            'booking_status': [],
            'reviews': [],
            'locations': [],
            'organizations': [],
            'persons': []
        }

        # Use NER pipeline if available
        if self.ner_pipeline and text:
            ner_results = self.ner_pipeline(text)
            for entity in ner_results:
                if entity['entity_group'] == 'LOC':
                    entities['locations'].append(entity['word'])
                elif entity['entity_group'] == 'ORG':
                    entities['organizations'].append(entity['word'])
                elif entity['entity_group'] == 'PER':
                    # Filter for likely doctor names (with Dr. prefix or in medical context)
                    if 'dr' in entity['word'].lower() or any(spec in text.lower() for spec in self.medical_specialties):
                        entities['doctors'].append(entity['word'])
                    else:
                        entities['persons'].append(entity['word'])

        # Use spaCy if available
        if nlp and text:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:
                    entities['locations'].append(ent.text)
                elif ent.label_ == 'ORG':
                    # Check if organization is likely a hospital/medical facility
                    if any(h_word in ent.text.lower() for h_word in ['hospital', 'clinic', 'medical', 'health']):
                        entities['hospitals'].append(ent.text)
                    else:
                        entities['organizations'].append(ent.text)
                elif ent.label_ == 'PERSON':
                    if 'dr' in ent.text.lower() or any(spec in text.lower() for spec in self.medical_specialties):
                        entities['doctors'].append(ent.text)
                    else:
                        entities['persons'].append(ent.text)

        # Extract using regex patterns
        if text:
            for pattern_type, pattern in self.medical_patterns.items():
                matches = pattern.findall(text)
                if pattern_type in entities:
                    entities[pattern_type].extend(matches)

        # Extract specialties from predefined list
        text_lower = text.lower() if text else ""
        for specialty in self.medical_specialties:
            if specialty in text_lower:
                entities['specialties'].append(specialty)

        # Remove duplicates and clean up
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    def create_medical_prompt(self, text, summary_type="medical_comprehensive", entities=None):
        """Create medical-specific prompts that preserve important information"""

        entity_context = ""
        if entities:
            important_info = []
            if entities['doctors']:
                important_info.append(f"Doctors: {', '.join(entities['doctors'][:5])}")
            if entities['hospitals']:
                important_info.append(f"Hospitals/Clinics: {', '.join(entities['hospitals'][:5])}")
            if entities['specialties']:
                important_info.append(f"Specialties: {', '.join(entities['specialties'][:5])}")
            if entities['phones']:
                important_info.append(f"Contact numbers: {', '.join(entities['phones'][:3])}")
            if entities['ratings']:
                important_info.append(f"Ratings: {', '.join(entities['ratings'][:3])}")
            if entities['appointment_times']:
                important_info.append(f"Appointment times: {', '.join(entities['appointment_times'][:3])}")
            if entities['dates']:
                important_info.append(f"Dates: {', '.join(entities['dates'][:3])}")
            if entities['addresses']:
                important_info.append(f"Addresses: {', '.join(entities['addresses'][:3])}")

            if important_info:
                entity_context = f"Key medical information to preserve: {'; '.join(important_info)}. "

        prompts = {
            "medical_comprehensive": f"{entity_context}Create a comprehensive medical summary including all doctors found, hospitals/clinics, specialties, appointment details, contact information, ratings, addresses, and booking status: {text}",

            "doctor_search": f"{entity_context}Summarize the doctor search results including doctor names, specialties, ratings, experience, hospital affiliations, contact details, and availability: {text}",

            "appointment_booking": f"{entity_context}Summarize the appointment booking process including doctor name, specialty, appointment date/time, patient details, booking status, and any confirmation information: {text}",

            "hospital_search": f"{entity_context}Summarize hospital/clinic information including names, locations, specialties offered, ratings, contact information, and online booking availability: {text}",

            "medical_consultation": f"{entity_context}Summarize medical consultation details including doctor information, symptoms discussed, diagnosis, treatment recommendations, and follow-up instructions: {text}",

            "healthcare_services": f"{entity_context}Summarize healthcare services including available treatments, medical procedures, facilities, staff details, and service quality indicators: {text}",

            "general": f"{entity_context}Summarize this medical information preserving important details like doctor names, appointments, contact information, and medical specialties: {text}"
        }

        return prompts.get(summary_type, prompts["medical_comprehensive"])

    def preprocess_medical_text(self, text):
        """Enhanced preprocessing for medical documents"""
        # Remove excessive whitespace while preserving structure
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Keep paragraph breaks
        text = re.sub(r'\s+', ' ', text)  # Normalize spaces

        # Preserve important medical formatting
        text = re.sub(r'(\d+:\d+\s*[AaPp][Mm])', r' \1 ', text)  # Space around times
        text = re.sub(r'(\d{10})', r' \1 ', text)  # Space around phone numbers
        text = re.sub(r'(Dr\.?\s+[A-Za-z\s]+)', r' \1 ', text)  # Space around doctor names
        text = re.sub(r'(\d+(?:\.\d+)?[/★⭐])', r' \1 ', text)  # Space around ratings

        # Ensure proper sentence endings
        if not text.endswith(('.', '!', '?')):
            text += '.'

        return text.strip()

    def generate_medical_summary(self, text, max_length=1024, min_length=400,
                               summary_type="medical_comprehensive", temperature=0.7):
        """Generate medical-specific summary preserving key information"""

        # Preprocess text
        clean_text = self.preprocess_medical_text(text)

        # Extract medical entities
        entities = self.extract_medical_entities(clean_text)

        # Create medical-specific prompt
        prompt = self.create_medical_prompt(clean_text, summary_type, entities)

        # Tokenize with increased max length for medical content
        inputs = self.tokenizer.encode(
            prompt,
            return_tensors="pt",
            max_length=1024,  # Increased for medical content
            truncation=True
        ).to(self.device)

        # Generate with parameters optimized for medical content
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
        return self.postprocess_medical_summary(summary, entities)

    def postprocess_medical_summary(self, summary, entities=None):
        """Enhanced post-processing for medical summaries"""
        # Remove prompt artifacts
        artifacts = [
            "create a comprehensive medical summary including all doctors",
            "summarize the doctor search results including",
            "summarize the appointment booking process including",
            "summarize hospital/clinic information including",
            "summarize medical consultation details including",
            "summarize healthcare services including",
            "summarize this medical information preserving",
            "key medical information to preserve:",
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

    def chunk_medical_text(self, text, chunk_size=600, overlap=100):
        """Medical-aware chunking that preserves sections"""
        words = text.split()

        if len(words) <= chunk_size:
            return [text]

        # Try to identify medical sections
        sections = []
        current_section = []

        medical_headers = [
            'doctor', 'appointment', 'hospital', 'clinic', 'specialty', 'booking',
            'consultation', 'treatment', 'diagnosis', 'rating', 'review', 'contact'
        ]

        for word in words:
            current_section.append(word)

            # Check if we hit a section boundary
            if any(header in word.lower() for header in medical_headers) and len(current_section) > 50:
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

    def summarize_long_medical_text(self, text, summary_type="medical_comprehensive"):
        """Handle long medical documents with section-aware processing"""
        sections = self.chunk_medical_text(text)

        if len(sections) == 1:
            return self.generate_medical_summary(text, summary_type=summary_type)

        # Summarize each section
        section_summaries = []
        for i, section in enumerate(sections):
            print(f"Processing section {i+1}/{len(sections)}...")
            summary = self.generate_medical_summary(
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
            final_summary = self.generate_medical_summary(
                combined,
                max_length=1500,  # Longer for comprehensive medical summaries
                min_length=600,
                summary_type="medical_comprehensive",
                temperature=0.7
            )
        else:
            final_summary = combined

        return final_summary

    def evaluate_medical_summary(self, generated_summary, reference_summary, original_text=None):
        """Enhanced evaluation with medical-specific metrics"""
        results = self.evaluate_summary(generated_summary, reference_summary, original_text)

        # Add medical-specific evaluation
        if original_text:
            original_entities = self.extract_medical_entities(original_text)
            summary_entities = self.extract_medical_entities(generated_summary)

            # Calculate entity preservation scores
            entity_preservation = {}
            for entity_type in original_entities:
                if original_entities[entity_type]:
                    preserved = len([e for e in original_entities[entity_type]
                                   if any(e.lower() in s.lower() for s in summary_entities[entity_type])])
                    total = len(original_entities[entity_type])
                    entity_preservation[f'{entity_type}_preservation'] = preserved / total if total > 0 else 0

            results['medical_specific'] = entity_preservation

            # Calculate medical information density
            info_density = (len(summary_entities['doctors']) +
                          len(summary_entities['hospitals']) +
                          len(summary_entities['specialties']) +
                          len(summary_entities['phones']) +
                          len(summary_entities['appointment_times'])) / len(generated_summary.split())
            results['medical_information_density'] = info_density

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

    def medical_summarize_and_evaluate(self, text, reference_summary=None,
                                     summary_type="medical_comprehensive", length="large"):
        """Complete medical summarization pipeline"""

        length_configs = {
            "short": {"max_length": 150, "min_length": 50},
            "medium": {"max_length": 300, "min_length": 100},
            "long": {"max_length": 500, "min_length": 150},
            "large": {"max_length": 800, "min_length": 200},
            "comprehensive": {"max_length": 1200, "min_length": 300}
        }

        config = length_configs.get(length, length_configs["large"])

        print(f"\n{'='*70}")
        print(f"PROCESSING MEDICAL DOCUMENT ({summary_type.upper()}, {length.upper()})")
        print(f"{'='*70}")

        # Extract entities first
        entities = self.extract_medical_entities(text)

        print(f"\nEXTRACTED MEDICAL ENTITIES:")
        for entity_type, entity_list in entities.items():
            if entity_list:
                print(f"  {entity_type.title()}: {', '.join(entity_list[:5])}")

        print(f"\n{'-'*50}")
        print(f"ORIGINAL TEXT LENGTH: {len(text.split())} words")
        print(f"{'-'*50}\n")

        # Generate medical summary
        if len(text.split()) > 800:
            summary = self.summarize_long_medical_text(text, summary_type)
        else:
            summary = self.generate_medical_summary(
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

            evaluation = self.evaluate_medical_summary(summary, reference_summary, text)

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

            if 'medical_specific' in evaluation:
                print(f"\nMedical Entity Preservation:")
                for metric, score in evaluation['medical_specific'].items():
                    print(f"  {metric}: {score:.2%}")

            if 'medical_information_density' in evaluation:
                print(f"Medical Information Density: {evaluation['medical_information_density']:.4f}")

        return {
            'original_text': text,
            'summary': summary,
            'entities': entities,
            'perplexity': ppl,
            'evaluation': evaluation
        }

    def compare_medical_summaries(self, summaries_dict, metrics_list=None, output_json="medical_summaries.json"):
        """Compare medical summaries with enhanced scoring"""
        print(f"\n{'='*50}")
        print("MEDICAL SUMMARY COMPARISON")
        print(f"{'='*50}")

        results = []
        for idx, (name, summary) in enumerate(summaries_dict.items()):
            ppl = self.calculate_perplexity(summary)
            entities = self.extract_medical_entities(summary)

            # Count preserved medical information
            medical_info_score = (len(entities['doctors']) * 0.25 +
                                len(entities['hospitals']) * 0.2 +
                                len(entities['specialties']) * 0.2 +
                                len(entities['phones']) * 0.15 +
                                len(entities['appointment_times']) * 0.1 +
                                len(entities['ratings']) * 0.1)

            evaluation = {}
            if metrics_list and idx < len(metrics_list) and metrics_list[idx] is not None:
                evaluation = metrics_list[idx]
                bert_f1 = evaluation.get('bertscore', {}).get('f1', [0])[0]
                meteor = evaluation.get('meteor', {}).get('meteor', 0)
                coverage = evaluation.get('coverage', 0) / 100

                # Enhanced scoring for medical content
                final_score = (
                    0.4 * bert_f1 +           # Semantic similarity
                    0.15 * meteor +           # Lexical overlap
                    0.15 * coverage +         # Information coverage
                    0.2 * medical_info_score + # Medical-specific information
                    0.1 * (100 - min(ppl, 100)) / 100  # Fluency (normalized)
                )
            else:
                final_score = medical_info_score / max(ppl/10, 1)  # Simple fallback

            results.append((name, summary, ppl, final_score, evaluation, entities))

            print(f"\n{name}:")
            print(f"Perplexity: {ppl:.2f}")
            print(f"Medical Info Score: {medical_info_score:.2f}")
            print(f"Final Score: {final_score:.4f}")
            print(f"Key Medical Elements: Doctors({len(entities['doctors'])}), "
                  f"Hospitals({len(entities['hospitals'])}), Specialties({len(entities['specialties'])})")
            print(f"Summary Preview: {summary[:200]}...")

        # Find best summary
        best = max(results, key=lambda x: x[3])
        print(f"\n🏆 BEST MEDICAL SUMMARY: {best[0]} (Score: {best[3]:.4f})")

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