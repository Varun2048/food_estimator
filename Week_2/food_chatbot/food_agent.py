from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
from sentence_transformers import SentenceTransformer
import chromadb
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama

# Load all models once
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to("cpu").eval()

clip_model = SentenceTransformer("clip-ViT-B-32")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("food_macros_clip")

llm = Ollama(model="llama2") 
prompt = PromptTemplate.from_template("""
You are a nutrition expert. Answer strictly based on the given food database context.

Image Caption:
{caption}

Context:
{context}

Question:
{query}

If the answer is not in the context, say "I don't know based on the given data."
""")
chain = LLMChain(llm=llm, prompt=prompt)

# === Logic Functions ===
def generate_caption(image_path: str) -> str:
    image = Image.open(image_path).convert("RGB")
    inputs = blip_processor(image, return_tensors="pt", use_fast=False)
    with torch.no_grad():
        out = blip_model.generate(**inputs)
    return blip_processor.decode(out[0], skip_special_tokens=True)

def get_context_from_chroma(caption: str, question: str, threshold: float = 0.2) -> str:
    combined_query = f"{caption}. Question: {question}"
    query_embedding = clip_model.encode(combined_query)
    results = collection.query(query_embeddings=[query_embedding.tolist()], n_results=5, include=["documents", "distances"])
    filtered = [doc for doc, dist in zip(results["documents"], results["distances"]) if dist[0] < threshold]
    return "\n".join([d[0] for d in filtered])

def get_answer(caption: str, context: str, question: str) -> str:
    return chain.run(caption=caption, context=context, query=question)
